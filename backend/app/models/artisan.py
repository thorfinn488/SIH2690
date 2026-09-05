import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


def utc_now():
    return datetime.now(timezone.utc)


class Artisan(Base):
    __tablename__ = "artisans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    region = Column(String(255), nullable=False)
    craft_specialty = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("User", back_populates="artisan_profile")
    products = relationship("Product", back_populates="artisan", cascade="all, delete-orphan")
    ai_insights = relationship("AIInsight", back_populates="artisan", cascade="all, delete-orphan")
