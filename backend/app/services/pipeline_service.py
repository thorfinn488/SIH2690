import logging
import traceback
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.repositories.product_repository import ProductRepository
from app.repositories.catalogue_repository import CatalogueRepository
from app.repositories.pricing_repository import PricingRepository
from app.repositories.opportunity_repository import OpportunityRepository
from app.repositories.buyer_repository import BuyerRepository
from app.repositories.user_repository import UserRepository
from app.storage.supabase_storage import get_storage_service
from app.models.product import ProductStatus
from app.models.user import UserRole, User
from app.models.buyer import Buyer
from app.ai_mocks.mock_ai_services import (
    analyze_image,
    transcribe,
    translate_to_english,
    understand_product,
    get_craft_context,
    calculate_price,
    explain_price,
    find_opportunities,
)

logger = logging.getLogger(__name__)


def run_ai_pipeline(product_id: str):
    """
    Background worker function executing the 6-step AI orchestration sequence.
    Uses an independent DB session.
    """
    db: Session = SessionLocal()
    try:
        product_repo = ProductRepository(db)
        catalogue_repo = CatalogueRepository(db)
        pricing_repo = PricingRepository(db)
        opp_repo = OpportunityRepository(db)
        buyer_repo = BuyerRepository(db)
        user_repo = UserRepository(db)
        storage = get_storage_service()

        product = product_repo.get_by_id(product_id)
        if not product:
            logger.error(f"Pipeline error: product {product_id} not found")
            return

        # Update status to PROCESSING
        product_repo.update_status(product_id, ProductStatus.PROCESSING, step="understanding_image", progress=15)

        # 1. Image analysis
        image_bytes = b""
        original_image_url = None
        if product.images and len(product.images) > 0:
            original_image_url = product.images[0].url
            image_bytes = storage.read_file(original_image_url)
        vision_data = analyze_image(image_bytes)

        enhanced_image_bytes = vision_data.get("enhanced_image_bytes")
        if enhanced_image_bytes and enhanced_image_bytes != image_bytes:
            enhanced_image_url = storage.save_file(
                enhanced_image_bytes,
                f"{product_id}-enhanced.jpg",
                "image/jpeg",
            )
            product_repo.add_image(product_id, enhanced_image_url)

        # 2. Voice transcription & translation
        product_repo.update_status(product_id, ProductStatus.PROCESSING, step="understanding_voice", progress=35)
        audio_bytes = b""
        if product.audio and len(product.audio) > 0:
            audio_bytes = b"sample_artisan_audio_bytes"
        
        transcription_res = transcribe(audio_bytes)
        translation_res = translate_to_english(
            text=transcription_res.get("raw_text", ""),
            source_language=transcription_res.get("detected_language", "hi")
        )

        # 3. Generating catalogue
        product_repo.update_status(product_id, ProductStatus.PROCESSING, step="generating_catalogue", progress=55)
        product_understanding = understand_product(
            transcript=translation_res.get("translated_text", ""),
            vision_data=vision_data
        )
        craft_info = get_craft_context(product_understanding.get("craft", "Handicrafts"))

        # Save catalogue
        catalogue = catalogue_repo.create_or_update(
            product_id=product_id,
            name=product_understanding.get("name", "Artisan Craft Product"),
            category=product_understanding.get("category", "Handicrafts"),
            material=product_understanding.get("material", "Natural Materials"),
            craft=product_understanding.get("craft", "Traditional Craft"),
            description=product_understanding.get("description", ""),
            tags=product_understanding.get("tags", []),
        )

        # 4. Calculating price (Pure Python formula)
        product_repo.update_status(product_id, ProductStatus.PROCESSING, step="calculating_price", progress=75)
        mat_cost = product_understanding.get("material_cost_estimate", 500.0)
        days = product_understanding.get("estimated_days_to_make", 3)
        
        price_data = calculate_price(
            material_cost=mat_cost,
            days_to_make=days,
            complexity="medium",
            category_avg=1500.0
        )
        explanation_str = explain_price(price_data)

        # Save pricing
        pricing_repo.create_or_update(
            product_id=product_id,
            suggested_price=price_data["suggested_price"],
            price_range_low=price_data["price_range"][0],
            price_range_high=price_data["price_range"][1],
            explanation=explanation_str,
        )

        # 5. Finding opportunities
        product_repo.update_status(product_id, ProductStatus.PROCESSING, step="finding_opportunities", progress=90)
        opp_list = find_opportunities({
            "id": product_id,
            "name": catalogue.name,
            "category": catalogue.category,
            "craft": catalogue.craft,
        })

        # Ensure a default buyer exists to link opportunities
        all_buyers = buyer_repo.list_all()
        target_buyer = all_buyers[0] if all_buyers else None
        if not target_buyer:
            # Create mock buyer user if missing
            dummy_user = user_repo.get_by_phone("9999999999")
            if not dummy_user:
                dummy_user = user_repo.create("Default Buyer Enterprise", "9999999999", "hashed_secret", UserRole.BUYER)
            target_buyer = buyer_repo.create(dummy_user.id, "Default Buyer Enterprise", "Looking for authentic handicraft products")

        for opp_item in opp_list:
            opp_repo.create(
                product_id=product_id,
                buyer_id=target_buyer.id,
                match_score=opp_item["match_score"],
            )

        # 6. Pipeline completed -> status = READY
        product_repo.update_status(
            product_id=product_id,
            status=ProductStatus.READY,
            step="done",
            progress=100
        )

    except Exception as exc:
        err_msg = f"Pipeline execution failed: {str(exc)}"
        logger.error(err_msg + "\n" + traceback.format_exc())
        try:
            product_repo = ProductRepository(db)
            product_repo.update_status(
                product_id=product_id,
                status=ProductStatus.FAILED,
                step="failed",
                progress=0,
                error_message=err_msg
            )
        except Exception:
            pass
    finally:
        db.close()
