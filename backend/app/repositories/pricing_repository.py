from typing import Optional
from sqlalchemy.orm import Session
from app.models.pricing import Pricing


class PricingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_product_id(self, product_id: str) -> Optional[Pricing]:
        return self.db.query(Pricing).filter(Pricing.product_id == product_id).first()

    def create_or_update(
        self,
        product_id: str,
        suggested_price: float,
        price_range_low: float,
        price_range_high: float,
        explanation: str,
    ) -> Pricing:
        pricing = self.get_by_product_id(product_id)
        if pricing:
            pricing.suggested_price = suggested_price
            pricing.price_range_low = price_range_low
            pricing.price_range_high = price_range_high
            pricing.explanation = explanation
        else:
            pricing = Pricing(
                product_id=product_id,
                suggested_price=suggested_price,
                price_range_low=price_range_low,
                price_range_high=price_range_high,
                explanation=explanation,
            )
            self.db.add(pricing)

        self.db.commit()
        self.db.refresh(pricing)
        return pricing
