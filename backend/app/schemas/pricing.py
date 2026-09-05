from typing import List
from pydantic import BaseModel, ConfigDict


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
