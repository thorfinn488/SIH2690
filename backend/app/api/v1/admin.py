from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ResponseEnvelope
from app.auth.rbac import require_role
from app.models.user import User
from app.repositories.artisan_repository import ArtisanRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.opportunity_repository import OpportunityRepository

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/artisans", response_model=ResponseEnvelope[List[Dict[str, Any]]], status_code=status.HTTP_200_OK)
def get_admin_artisans(
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    artisan_repo = ArtisanRepository(db)
    artisans = artisan_repo.list_all()
    res = []
    for a in artisans:
        res.append({
            "artisan_id": a.id,
            "user_id": a.user_id,
            "name": a.user.name if a.user else "N/A",
            "phone": a.user.phone if a.user else "N/A",
            "region": a.region,
            "craft_specialty": a.craft_specialty,
            "created_at": a.created_at.isoformat(),
        })
    return ResponseEnvelope.success_response(res)


@router.get("/products", response_model=ResponseEnvelope[List[Dict[str, Any]]], status_code=status.HTTP_200_OK)
def get_admin_products(
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    product_repo = ProductRepository(db)
    products, total = product_repo.list_products(page=1, page_size=1000)
    res = []
    for p in products:
        res.append({
            "product_id": p.id,
            "artisan_id": p.artisan_id,
            "artisan_name": p.artisan.user.name if p.artisan and p.artisan.user else "N/A",
            "status": p.status.value,
            "created_at": p.created_at.isoformat(),
            "catalogue_name": p.catalogue.name if p.catalogue else None,
            "suggested_price": p.pricing.suggested_price if p.pricing else None,
        })
    return ResponseEnvelope.success_response(res)


@router.get("/opportunities", response_model=ResponseEnvelope[List[Dict[str, Any]]], status_code=status.HTTP_200_OK)
def get_admin_opportunities(
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    opp_repo = OpportunityRepository(db)
    opps = opp_repo.list_all()
    res = []
    for opp in opps:
        res.append({
            "opportunity_id": opp.id,
            "product_id": opp.product_id,
            "buyer_id": opp.buyer_id,
            "buyer_company": opp.buyer.company_name if opp.buyer else "N/A",
            "match_score": opp.match_score,
            "status": opp.status.value,
            "created_at": opp.created_at.isoformat(),
        })
    return ResponseEnvelope.success_response(res)
