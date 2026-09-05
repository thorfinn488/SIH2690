import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base


class ProductStatus(str, Enum):
    DRAFT = "DRAFT"
    PROCESSING = "PROCESSING"
    READY = "READY"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


def generate_uuid():
    return str(uuid.uuid4())


def utc_now():
    return datetime.now(timezone.utc)


class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    artisan_id = Column(String(36), ForeignKey("artisans.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(SQLEnum(ProductStatus, native_enum=False), nullable=False, default=ProductStatus.DRAFT)
    processing_step = Column(String(100), nullable=True, default="idle")
    processing_progress = Column(Integer, nullable=True, default=0)
    error_message = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    artisan = relationship("Artisan", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    audio = relationship("ProductAudio", back_populates="product", cascade="all, delete-orphan")
    catalogue = relationship("Catalogue", back_populates="product", uselist=False, cascade="all, delete-orphan")
    pricing = relationship("Pricing", back_populates="product", uselist=False, cascade="all, delete-orphan")
    opportunities = relationship("MarketOpportunity", back_populates="product", cascade="all, delete-orphan")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String(1024), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    product = relationship("Product", back_populates="images")


class ProductAudio(Base):
    __tablename__ = "product_audio"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String(1024), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    product = relationship("Product", back_populates="audio")
