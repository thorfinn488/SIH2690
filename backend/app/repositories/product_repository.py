from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.models.product import Product, ProductStatus, ProductImage, ProductAudio


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def create(self, artisan_id: str) -> Product:
        product = Product(
            artisan_id=artisan_id,
            status=ProductStatus.DRAFT,
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def add_image(self, product_id: str, url: str) -> ProductImage:
        image = ProductImage(product_id=product_id, url=url)
        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)
        return image

    def add_audio(self, product_id: str, url: str) -> ProductAudio:
        audio = ProductAudio(product_id=product_id, url=url)
        self.db.add(audio)
        self.db.commit()
        self.db.refresh(audio)
        return audio

    def update_status(
        self,
        product_id: str,
        status: ProductStatus,
        step: Optional[str] = None,
        progress: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> Optional[Product]:
        product = self.get_by_id(product_id)
        if product:
            product.status = status
            if step is not None:
                product.processing_step = step
            if progress is not None:
                product.processing_progress = progress
            if error_message is not None:
                product.error_message = error_message
            self.db.commit()
            self.db.refresh(product)
        return product

    def list_products(
        self,
        artisan_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[Product], int]:
        query = self.db.query(Product)
        if artisan_id:
            query = query.filter(Product.artisan_id == artisan_id)

        total = query.count()
        offset = (page - 1) * page_size
        products = query.order_by(Product.created_at.desc()).offset(offset).limit(page_size).all()
        return products, total

    def delete(self, product_id: str) -> bool:
        product = self.get_by_id(product_id)
        if product:
            self.db.delete(product)
            self.db.commit()
            return True
        return False
