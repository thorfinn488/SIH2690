from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ResponseEnvelope
from app.schemas.dashboard import DashboardSummaryResponse, DashboardInsightsResponse
from app.services.dashboard_service import DashboardService
from app.auth.rbac import require_role
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=ResponseEnvelope[DashboardSummaryResponse], status_code=status.HTTP_200_OK)
def get_dashboard(
    current_user: User = Depends(require_role("ARTISAN", "ADMIN")),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)
    res = service.get_artisan_dashboard(current_user)
    return ResponseEnvelope.success_response(res)


@router.get("/insights", response_model=ResponseEnvelope[DashboardInsightsResponse], status_code=status.HTTP_200_OK)
def get_insights(
    current_user: User = Depends(require_role("ARTISAN", "ADMIN")),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)
    res = service.get_artisan_insights(current_user)
    return ResponseEnvelope.success_response(res)
