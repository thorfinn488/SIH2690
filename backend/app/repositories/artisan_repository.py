from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.artisan import Artisan


class ArtisanRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, artisan_id: str) -> Optional[Artisan]:
        return self.db.query(Artisan).filter(Artisan.id == artisan_id).first()

    def get_by_user_id(self, user_id: str) -> Optional[Artisan]:
        return self.db.query(Artisan).filter(Artisan.user_id == user_id).first()

    def create(self, user_id: str, region: str, craft_specialty: str) -> Artisan:
        artisan = Artisan(
            user_id=user_id,
            region=region,
            craft_specialty=craft_specialty,
        )
        self.db.add(artisan)
        self.db.commit()
        self.db.refresh(artisan)
        return artisan

    def list_all(self) -> List[Artisan]:
        return self.db.query(Artisan).all()
