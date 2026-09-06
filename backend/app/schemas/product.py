from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.catalogue import CatalogueResponse
from app.schemas.pricing import PricingResponse, PriceSchema


class ProductCreateRequest(BaseModel):
    artisan_id: Optional[str] = None


class ProductCreateResponse(BaseModel):
    product_id: str
    status: str


class UploadImageResponse(BaseModel):
    product_id: str
    image_url: str


class UploadAudioResponse(BaseModel):
    product_id: str
    audio_url: str


class ProcessProductResponse(BaseModel):
    product_id: str
    status: str
    job_id: str


class ProcessProductRequest(BaseModel):
    transcript: Optional[str] = None


class ProcessingStatusResponse(BaseModel):
    product_id: str
    status: str
    step: str
    progress_percent: int


class ProductUpdateResponse(BaseModel):
    product_id: str
    updated: bool


class ProductDeleteResponse(BaseModel):
    product_id: str
    deleted: bool


class ProductImageSchema(BaseModel):
    id: str
    url: str

    model_config = ConfigDict(from_attributes=True)


class ProductAudioSchema(BaseModel):
    id: str
    url: str

    model_config = ConfigDict(from_attributes=True)


class OpportunityItem(BaseModel):
    buyer_name: str
    match_score: int
    location: str
    requirement: str


class ProductOpportunitiesResponse(BaseModel):
    opportunities: List[OpportunityItem]


class OpportunityListItem(BaseModel):
    opportunity_id: str
    product_id: str
    buyer_name: str
    company_name: str
    match_score: int
    status: str
    requirement: str


class ProductDetailResponse(BaseModel):
    product_id: str
    id: Optional[str] = None
    artisan_id: str
    status: str
    created_at: str
    image_url: Optional[str] = None
    images: List[ProductImageSchema] = []
    audio: List[ProductAudioSchema] = []
    catalogue: Optional[CatalogueResponse] = None
    price: Optional[PriceSchema] = None
    pricing: Optional[PricingResponse] = None
    opportunities: List[OpportunityItem] = []

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    products: List[ProductDetailResponse]
    total: int
    page: int
