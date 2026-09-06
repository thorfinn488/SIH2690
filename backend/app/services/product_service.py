from typing import Tuple, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, BackgroundTasks, UploadFile

from app.repositories.product_repository import ProductRepository
from app.repositories.artisan_repository import ArtisanRepository
from app.repositories.catalogue_repository import CatalogueRepository
from app.repositories.pricing_repository import PricingRepository
from app.repositories.opportunity_repository import OpportunityRepository
from app.repositories.audit_repository import AuditRepository
from app.models.user import User, UserRole
from app.models.product import ProductStatus, Product
from app.schemas.product import (
    ProductCreateRequest,
    ProductCreateResponse,
    UploadImageResponse,
    UploadAudioResponse,
    ProcessProductResponse,
    ProcessingStatusResponse,
    ProductUpdateResponse,
    ProductDeleteResponse,
    ProductDetailResponse,
    ProductImageSchema,
    ProductAudioSchema,
    OpportunityItem,
)
from app.schemas.catalogue import CatalogueResponse, CatalogueUpdate
from app.schemas.pricing import PricingResponse, PriceSchema
from app.schemas.pricing import PriceRecalculateRequest
from app.services.pipeline_service import run_ai_pipeline
from app.storage.supabase_storage import get_storage_service
from app.utils.file_validation import validate_image_file, validate_audio_file
from app.ai_mocks.mock_ai_services import calculate_price, explain_price


class ProductService:
    VALID_TRANSITIONS = {
        ProductStatus.DRAFT: {ProductStatus.PROCESSING},
        ProductStatus.PROCESSING: {ProductStatus.READY, ProductStatus.FAILED},
        ProductStatus.READY: {ProductStatus.PUBLISHED, ProductStatus.PROCESSING},
        ProductStatus.PUBLISHED: set(),
        ProductStatus.FAILED: {ProductStatus.PROCESSING},
    }

    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.artisan_repo = ArtisanRepository(db)
        self.catalogue_repo = CatalogueRepository(db)
        self.pricing_repo = PricingRepository(db)
        self.opp_repo = OpportunityRepository(db)
        self.audit_repo = AuditRepository(db)
        self.storage = get_storage_service()

    def verify_ownership(self, product: Product, user: User):
        """
        Verify product ownership. Artisans can only access their own products.
        ADMIN can access any product.
        """
        user_role_str = user.role.value if isinstance(user.role, UserRole) else str(user.role)
        if user_role_str == UserRole.ADMIN.value:
            return

        artisan = self.artisan_repo.get_by_user_id(user.id)
        if not artisan or product.artisan_id != artisan.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="FORBIDDEN: You do not own this product",
            )

    def validate_status_transition(self, current_status: ProductStatus, target_status: ProductStatus):
        allowed = self.VALID_TRANSITIONS.get(current_status, set())
        if target_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from {current_status.value} to {target_status.value}",
            )

    def create_product(self, user: User, req: Optional[ProductCreateRequest] = None) -> ProductCreateResponse:
        artisan_id = None
        if req and req.artisan_id:
            artisan_id = req.artisan_id
        else:
            artisan = self.artisan_repo.get_by_user_id(user.id)
            if not artisan:
                artisan = self.artisan_repo.create(user.id, region="India", craft_specialty="General")
            artisan_id = artisan.id

        product = self.product_repo.create(artisan_id=artisan_id)
        self.audit_repo.log_action(user_id=user.id, action="product_creation", metadata={"product_id": product.id})

        return ProductCreateResponse(
            product_id=product.id,
            status=product.status.value,
        )

    def upload_image(self, product_id: str, file: UploadFile, file_bytes: bytes, user: User) -> UploadImageResponse:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND: Product not found")
        self.verify_ownership(product, user)

        validate_image_file(file, file_bytes)
        image_url = self.storage.save_file(file_bytes, file.filename or "image.jpg", file.content_type or "image/jpeg")

        self.product_repo.add_image(product_id, image_url)
        return UploadImageResponse(product_id=product_id, image_url=image_url)

    def upload_audio(self, product_id: str, file: UploadFile, file_bytes: bytes, user: User) -> UploadAudioResponse:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND: Product not found")
        self.verify_ownership(product, user)

        validate_audio_file(file, file_bytes)
        audio_url = self.storage.save_file(file_bytes, file.filename or "audio.mp3", file.content_type or "audio/mpeg")

        self.product_repo.add_audio(product_id, audio_url)
        return UploadAudioResponse(product_id=product_id, audio_url=audio_url)

    def trigger_processing(
        self,
        product_id: str,
        background_tasks: BackgroundTasks,
        user: User,
        transcript: Optional[str] = None,
    ) -> ProcessProductResponse:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND: Product not found")
        self.verify_ownership(product, user)

        self.validate_status_transition(product.status, ProductStatus.PROCESSING)
        self.product_repo.update_status(product_id, ProductStatus.PROCESSING, step="understanding_image", progress=10)

        background_tasks.add_task(run_ai_pipeline, product_id, transcript)
        self.audit_repo.log_action(user_id=user.id, action="product_processing_trigger", metadata={"product_id": product_id})

        return ProcessProductResponse(
            product_id=product_id,
            status=ProductStatus.PROCESSING.value,
            job_id=f"job_{product_id}",
        )

    def get_processing_status(self, product_id: str, user: User) -> ProcessingStatusResponse:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND: Product not found")
        self.verify_ownership(product, user)

        if product.status == ProductStatus.FAILED:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI_PROCESSING_FAILED: {product.error_message or 'Pipeline error occurred'}",
            )

        return ProcessingStatusResponse(
            product_id=product.id,
            status=product.status.value,
            step=product.processing_step or "idle",
            progress_percent=product.processing_progress or 0,
        )

    def get_product_detail(self, product_id: str, user: User) -> ProductDetailResponse:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND: Product not found")
        self.verify_ownership(product, user)

        images = [ProductImageSchema(id=img.id, url=img.url) for img in product.images]
        audio = [ProductAudioSchema(id=aud.id, url=aud.url) for aud in product.audio]
        primary_image_url = images[0].url if images else None

        cat_schema = None
        if product.catalogue:
            cat = product.catalogue
            cat_schema = CatalogueResponse(
                id=cat.id,
                product_id=cat.product_id,
                name=cat.name,
                category=cat.category,
                material=cat.material,
                craft=cat.craft,
                description=cat.description,
                tags=cat.tags or [],
            )

        pricing_schema = None
        price_schema = None
        if product.pricing:
            pr = product.pricing
            pricing_schema = PricingResponse(
                id=pr.id,
                product_id=pr.product_id,
                suggested_price=pr.suggested_price,
                price_range_low=pr.price_range_low,
                price_range_high=pr.price_range_high,
                explanation=pr.explanation,
            )
            price_schema = PriceSchema(
                suggested_price=pr.suggested_price,
                price_range=[pr.price_range_low, pr.price_range_high],
                explanation=pr.explanation,
            )

        opps = []
        for opp in product.opportunities:
            buyer_name = opp.buyer.company_name if opp.buyer else "Verified Buyer"
            location = "India"
            req_text = opp.buyer.requirements if opp.buyer else "Product match"
            opps.append(
                OpportunityItem(
                    buyer_name=buyer_name,
                    match_score=opp.match_score,
                    location=location,
                    requirement=req_text or "Standard requirements",
                )
            )

        return ProductDetailResponse(
            product_id=product.id,
            id=product.id,
            artisan_id=product.artisan_id,
            status=product.status.value,
            created_at=product.created_at.isoformat(),
            image_url=primary_image_url,
            images=images,
            audio=audio,
            catalogue=cat_schema,
            price=price_schema,
            pricing=pricing_schema,
            opportunities=opps,
        )

    def recalculate_price(
        self,
        product_id: str,
        req: PriceRecalculateRequest,
        user: User,
    ) -> PriceSchema:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND: Product not found")
        self.verify_ownership(product, user)

        price_data = calculate_price(
            material_cost=req.material_cost,
            days_to_make=req.days_to_make,
            complexity=req.complexity,
        )
        explanation = explain_price(price_data)
        self.pricing_repo.create_or_update(
            product_id=product_id,
            suggested_price=price_data["suggested_price"],
            price_range_low=price_data["price_range"][0],
            price_range_high=price_data["price_range"][1],
            explanation=explanation,
        )

        return PriceSchema(
            suggested_price=price_data["suggested_price"],
            price_range=price_data["price_range"],
            explanation=explanation,
        )

    def update_catalogue(self, product_id: str, req: CatalogueUpdate, user: User) -> ProductUpdateResponse:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND: Product not found")
        self.verify_ownership(product, user)

        cat = product.catalogue
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalogue not yet generated for this product")

        name = req.name if req.name is not None else cat.name
        category = req.category if req.category is not None else cat.category
        material = req.material if req.material is not None else cat.material
        craft = req.craft if req.craft is not None else cat.craft
        description = req.description if req.description is not None else cat.description
        tags = req.tags if req.tags is not None else cat.tags

        self.catalogue_repo.create_or_update(product_id, name, category, material, craft, description, tags)
        self.audit_repo.log_action(user_id=user.id, action="catalogue_edit", metadata={"product_id": product_id})

        return ProductUpdateResponse(product_id=product_id, updated=True)

    def list_products(self, user: User, page: int = 1, page_size: int = 10):
        user_role_str = user.role.value if isinstance(user.role, UserRole) else str(user.role)
        artisan_id = None
        if user_role_str == UserRole.ARTISAN.value:
            artisan = self.artisan_repo.get_by_user_id(user.id)
            artisan_id = artisan.id if artisan else "none"

        products, total = self.product_repo.list_products(artisan_id=artisan_id, page=page, page_size=page_size)
        items = []
        for p in products:
            items.append(self.get_product_detail(p.id, user))

        return {"products": items, "total": total, "page": page}

    def delete_product(self, product_id: str, user: User) -> ProductDeleteResponse:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND: Product not found")
        self.verify_ownership(product, user)

        deleted = self.product_repo.delete(product_id)
        return ProductDeleteResponse(product_id=product_id, deleted=deleted)
