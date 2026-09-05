from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.market_opportunity import MarketOpportunity, OpportunityStatus


class OpportunityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_product_id(self, product_id: str) -> List[MarketOpportunity]:
        return self.db.query(MarketOpportunity).filter(MarketOpportunity.product_id == product_id).all()

    def list_open_opportunities(self) -> List[MarketOpportunity]:
        return self.db.query(MarketOpportunity).filter(MarketOpportunity.status == OpportunityStatus.OPEN).all()

    def list_all(self) -> List[MarketOpportunity]:
        return self.db.query(MarketOpportunity).all()

    def create(self, product_id: str, buyer_id: str, match_score: int, status: OpportunityStatus = OpportunityStatus.OPEN) -> MarketOpportunity:
        opp = MarketOpportunity(
            product_id=product_id,
            buyer_id=buyer_id,
            match_score=match_score,
            status=status,
        )
        self.db.add(opp)
        self.db.commit()
        self.db.refresh(opp)
        return opp
