import uuid
from sqlalchemy import Column, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Pricing(Base):
    __tablename__ = "pricing"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    suggested_price = Column(Float, nullable=False)
    price_range_low = Column(Float, nullable=False)
    price_range_high = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)

    product = relationship("Product", back_populates="pricing")
