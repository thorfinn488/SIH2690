from typing import Optional, List
from fastapi import APIRouter, Depends, status, BackgroundTasks, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ResponseEnvelope
from app.schemas.product import (
    ProductCreateRequest,
    ProcessProductRequest,
    ProductCreateResponse,
    UploadImageResponse,
    UploadAudioResponse,
    ProcessProductResponse,
    ProcessingStatusResponse,
    ProductUpdateResponse,
    ProductDeleteResponse,
    ProductDetailResponse,
    ProductListResponse,
    ProductOpportunitiesResponse,
    OpportunityListItem,
)
from app.schemas.catalogue import CatalogueUpdate
from app.schemas.pricing import PriceRecalculateRequest, PriceSchema
from app.services.product_service import ProductService
from app.repositories.opportunity_repository import OpportunityRepository
from app.middleware.auth_middleware import get_current_user
from app.auth.rbac import require_role
from app.models.user import User, UserRole

router = APIRouter(tags=["Products"])


@router.post("/products", response_model=ResponseEnvelope[ProductCreateResponse], status_code=status.HTTP_201_CREATED)
def create_product(
    req: Optional[ProductCreateRequest] = None,
    current_user: User = Depends(require_role("ARTISAN", "ADMIN")),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    res = service.create_product(current_user, req)
    return ResponseEnvelope.success_response(res)


@router.post("/products/{id}/image", response_model=ResponseEnvelope[UploadImageResponse], status_code=status.HTTP_200_OK)
async def upload_product_image(
    id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("ARTISAN", "ADMIN")),
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()
    service = ProductService(db)
    res = service.upload_image(id, file, file_bytes, current_user)
    return ResponseEnvelope.success_response(res)


@router.post("/products/{id}/audio", response_model=ResponseEnvelope[UploadAudioResponse], status_code=status.HTTP_200_OK)
async def upload_product_audio(
    id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("ARTISAN", "ADMIN")),
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()
    service = ProductService(db)
    res = service.upload_audio(id, file, file_bytes, current_user)
    return ResponseEnvelope.success_response(res)


@router.post("/products/{id}/process", response_model=ResponseEnvelope[ProcessProductResponse], status_code=status.HTTP_200_OK)
def trigger_processing(
    id: str,
    background_tasks: BackgroundTasks,
    req: Optional[ProcessProductRequest] = None,
    current_user: User = Depends(require_role("ARTISAN", "ADMIN")),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    res = service.trigger_processing(id, background_tasks, current_user, req.transcript if req else None)
    return ResponseEnvelope.success_response(res)


@router.get("/products/{id}/processing-status", response_model=ResponseEnvelope[ProcessingStatusResponse], status_code=status.HTTP_200_OK)
def get_processing_status(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    res = service.get_processing_status(id, current_user)
    return ResponseEnvelope.success_response(res)


@router.get("/products/{id}", response_model=ResponseEnvelope[ProductDetailResponse], status_code=status.HTTP_200_OK)
def get_product(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    res = service.get_product_detail(id, current_user)
    return ResponseEnvelope.success_response(res)


@router.post(
    "/products/{id}/recalculate-price",
    response_model=ResponseEnvelope[PriceSchema],
    status_code=status.HTTP_200_OK,
)
def recalculate_price(
    id: str,
    req: PriceRecalculateRequest,
    current_user: User = Depends(require_role("ARTISAN", "ADMIN")),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    res = service.recalculate_price(id, req, current_user)
    return ResponseEnvelope.success_response(res)


@router.put("/products/{id}/catalogue", response_model=ResponseEnvelope[ProductUpdateResponse], status_code=status.HTTP_200_OK)
def update_catalogue(
    id: str,
    req: CatalogueUpdate,
    current_user: User = Depends(require_role("ARTISAN", "ADMIN")),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    res = service.update_catalogue(id, req, current_user)
    return ResponseEnvelope.success_response(res)


@router.get("/products", response_model=ResponseEnvelope[ProductListResponse], status_code=status.HTTP_200_OK)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    res = service.list_products(current_user, page=page, page_size=page_size)
    return ResponseEnvelope.success_response(res)


@router.delete("/products/{id}", response_model=ResponseEnvelope[ProductDeleteResponse], status_code=status.HTTP_200_OK)
def delete_product(
    id: str,
    current_user: User = Depends(require_role("ARTISAN", "ADMIN")),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    res = service.delete_product(id, current_user)
    return ResponseEnvelope.success_response(res)


@router.get("/products/{id}/opportunities", response_model=ResponseEnvelope[ProductOpportunitiesResponse], status_code=status.HTTP_200_OK)
def get_product_opportunities(
    id: str,
    current_user: User = Depends(require_role("ARTISAN", "ADMIN")),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    detail = service.get_product_detail(id, current_user)
    return ResponseEnvelope.success_response(ProductOpportunitiesResponse(opportunities=detail.opportunities))


@router.get("/opportunities", response_model=ResponseEnvelope[List[OpportunityListItem]], status_code=status.HTTP_200_OK)
def list_opportunities(
    current_user: User = Depends(require_role("BUYER", "ADMIN")),
    db: Session = Depends(get_db),
):
    opp_repo = OpportunityRepository(db)
    opps = opp_repo.list_open_opportunities()
    items = []
    for opp in opps:
        buyer_name = opp.buyer.user.name if opp.buyer and opp.buyer.user else "Verified Buyer"
        company_name = opp.buyer.company_name if opp.buyer else "Enterprise Buyer"
        req_str = opp.buyer.requirements if opp.buyer else "Open requirement"
        items.append(
            OpportunityListItem(
                opportunity_id=opp.id,
                product_id=opp.product_id,
                buyer_name=buyer_name,
                company_name=company_name,
                match_score=opp.match_score,
                status=opp.status.value,
                requirement=req_str or "Standard procurement match",
            )
        )
    return ResponseEnvelope.success_response(items)
