from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.product_repository import ProductRepository
from app.repositories.artisan_repository import ArtisanRepository
from app.repositories.opportunity_repository import OpportunityRepository
from app.repositories.buyer_repository import BuyerRepository
from app.models.user import User, UserRole
from app.models.product import ProductStatus
from app.models.ai_insight import AIInsight
from app.schemas.dashboard import DashboardSummaryResponse, CatalogueStatusCounts, DashboardInsightsResponse, InsightItem
from app.services.product_service import ProductService
from app.ai_mocks.mock_ai_services import generate_business_insight


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.artisan_repo = ArtisanRepository(db)
        self.opp_repo = OpportunityRepository(db)
        self.buyer_repo = BuyerRepository(db)
        self.product_service = ProductService(db)

    def get_artisan_dashboard(self, user: User) -> DashboardSummaryResponse:
        artisan = self.artisan_repo.get_by_user_id(user.id)
        artisan_id = artisan.id if artisan else None

        products, total = self.product_repo.list_products(artisan_id=artisan_id, page=1, page_size=5)
        
        status_counts = CatalogueStatusCounts(ready=0, processing=0, draft=0)
        if artisan_id:
            all_artisan_products, _ = self.product_repo.list_products(artisan_id=artisan_id, page=1, page_size=1000)
            for p in all_artisan_products:
                if p.status == ProductStatus.READY or p.status == ProductStatus.PUBLISHED:
                    status_counts.ready += 1
                elif p.status == ProductStatus.PROCESSING:
                    status_counts.processing += 1
                elif p.status == ProductStatus.DRAFT:
                    status_counts.draft += 1

        recent_items = [self.product_service.get_product_detail(p.id, user) for p in products]

        return DashboardSummaryResponse(
            total_products=total,
            catalogue_status=status_counts,
            recent_products=recent_items,
        )

    def get_artisan_insights(self, user: User) -> DashboardInsightsResponse:
        artisan = self.artisan_repo.get_by_user_id(user.id)
        items = []

        if artisan:
            insights_rows = self.db.query(AIInsight).filter(AIInsight.artisan_id == artisan.id).all()
            for row in insights_rows:
                items.append(InsightItem(type=row.type, message=row.message))

        if not items:
            raw_insights = generate_business_insight([], {})
            for text in raw_insights:
                items.append(InsightItem(type="MARKET_TREND", message=text))

        return DashboardInsightsResponse(insights=items)
