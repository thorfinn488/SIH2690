from typing import List, Literal
from pydantic import BaseModel, ConfigDict, Field


class PriceRecalculateRequest(BaseModel):
    material_cost: float = Field(..., ge=50, le=20000)
    days_to_make: int = Field(..., ge=1, le=60)
    complexity: Literal["low", "medium", "high"]


class PriceSchema(BaseModel):
    suggested_price: float
    price_range: List[float]
    explanation: str

    model_config = ConfigDict(from_attributes=True)


class PricingResponse(BaseModel):
    id: str
    product_id: str
    suggested_price: float
    price_range_low: float
    price_range_high: float
    explanation: str

    model_config = ConfigDict(from_attributes=True)
