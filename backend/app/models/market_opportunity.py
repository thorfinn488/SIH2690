import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base


class OpportunityStatus(str, Enum):
    OPEN = "OPEN"
    CONTACTED = "CONTACTED"
    CLOSED = "CLOSED"


def generate_uuid():
    return str(uuid.uuid4())


def utc_now():
    return datetime.now(timezone.utc)


class MarketOpportunity(Base):
    __tablename__ = "market_opportunities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    buyer_id = Column(String(36), ForeignKey("buyers.id", ondelete="CASCADE"), nullable=False, index=True)
    match_score = Column(Integer, nullable=False)
    status = Column(SQLEnum(OpportunityStatus, native_enum=False), nullable=False, default=OpportunityStatus.OPEN)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    product = relationship("Product", back_populates="opportunities")
    buyer = relationship("Buyer", back_populates="opportunities")
