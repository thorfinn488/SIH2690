from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.buyer import Buyer


class BuyerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, buyer_id: str) -> Optional[Buyer]:
        return self.db.query(Buyer).filter(Buyer.id == buyer_id).first()

    def get_by_user_id(self, user_id: str) -> Optional[Buyer]:
        return self.db.query(Buyer).filter(Buyer.user_id == user_id).first()

    def create(self, user_id: str, company_name: str, requirements: Optional[str] = None) -> Buyer:
        buyer = Buyer(
            user_id=user_id,
            company_name=company_name,
            requirements=requirements,
        )
        self.db.add(buyer)
        self.db.commit()
        self.db.refresh(buyer)
        return buyer

    def list_all(self) -> List[Buyer]:
        return self.db.query(Buyer).all()
