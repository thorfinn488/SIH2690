from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.user_repository import UserRepository
from app.repositories.artisan_repository import ArtisanRepository
from app.repositories.buyer_repository import BuyerRepository
from app.repositories.audit_repository import AuditRepository
from app.auth.password_handler import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.models.user import UserRole
from app.schemas.auth import RegisterRequest, LoginRequest, AuthTokenResponse, UserMeResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.artisan_repo = ArtisanRepository(db)
        self.buyer_repo = BuyerRepository(db)
        self.audit_repo = AuditRepository(db)

    def register(self, req: RegisterRequest) -> AuthTokenResponse:
        existing_user = self.user_repo.get_by_phone(req.phone)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this phone number already exists",
            )

        hashed_pwd = hash_password(req.password)
        user = self.user_repo.create(
            name=req.name,
            phone=req.phone,
            password_hash=hashed_pwd,
            role=req.role,
        )

        if req.role == UserRole.ARTISAN:
            region = req.region or "India"
            craft = req.craft_specialty or "Handicrafts"
            self.artisan_repo.create(user_id=user.id, region=region, craft_specialty=craft)
        elif req.role == UserRole.BUYER:
            company = req.company_name or f"{req.name}'s Enterprise"
            self.buyer_repo.create(user_id=user.id, company_name=company, requirements=req.requirements)

        token = create_access_token({"user_id": user.id, "role": user.role.value})
        self.audit_repo.log_action(user_id=user.id, action="register", metadata={"role": user.role.value})

        return AuthTokenResponse(
            user_id=user.id,
            name=user.name,
            role=user.role.value,
            token=token,
        )

    def login(self, req: LoginRequest) -> AuthTokenResponse:
        user = self.user_repo.get_by_phone(req.phone)
        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone number or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token({"user_id": user.id, "role": user.role.value})
        self.audit_repo.log_action(user_id=user.id, action="login", metadata={"phone": user.phone})

        return AuthTokenResponse(
            user_id=user.id,
            name=user.name,
            role=user.role.value,
            token=token,
        )

    def get_me(self, user) -> UserMeResponse:
        return UserMeResponse(
            user_id=user.id,
            name=user.name,
            role=user.role.value if isinstance(user.role, UserRole) else str(user.role),
            phone=user.phone,
        )
