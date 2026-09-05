from typing import List, Dict
from pydantic import BaseModel, ConfigDict
from app.schemas.product import ProductDetailResponse


class CatalogueStatusCounts(BaseModel):
    ready: int = 0
    processing: int = 0
    draft: int = 0


class DashboardSummaryResponse(BaseModel):
    total_products: int
    catalogue_status: CatalogueStatusCounts
    recent_products: List[ProductDetailResponse]


class InsightItem(BaseModel):
    type: str
    message: str


class DashboardInsightsResponse(BaseModel):
    insights: List[InsightItem]
