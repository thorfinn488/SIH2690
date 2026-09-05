from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ResponseEnvelope
from app.schemas.auth import RegisterRequest, LoginRequest, AuthTokenResponse, UserMeResponse
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=ResponseEnvelope[AuthTokenResponse], status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    result = auth_service.register(req)
    return ResponseEnvelope.success_response(result)


@router.post("/login", response_model=ResponseEnvelope[AuthTokenResponse], status_code=status.HTTP_200_OK)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    result = auth_service.login(req)
    return ResponseEnvelope.success_response(result)


@router.get("/me", response_model=ResponseEnvelope[UserMeResponse], status_code=status.HTTP_200_OK)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    result = auth_service.get_me(current_user)
    return ResponseEnvelope.success_response(result)
