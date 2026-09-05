from typing import Optional
from sqlalchemy.orm import Session
from app.models.catalogue import Catalogue


class CatalogueRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_product_id(self, product_id: str) -> Optional[Catalogue]:
        return self.db.query(Catalogue).filter(Catalogue.product_id == product_id).first()

    def create_or_update(
        self,
        product_id: str,
        name: str,
        category: str,
        material: str,
        craft: str,
        description: str,
        tags: list,
    ) -> Catalogue:
        catalogue = self.get_by_product_id(product_id)
        if catalogue:
            catalogue.name = name
            catalogue.category = category
            catalogue.material = material
            catalogue.craft = craft
            catalogue.description = description
            catalogue.tags = tags
        else:
            catalogue = Catalogue(
                product_id=product_id,
                name=name,
                category=category,
                material=material,
                craft=craft,
                description=description,
                tags=tags,
            )
            self.db.add(catalogue)

        self.db.commit()
        self.db.refresh(catalogue)
        return catalogue
