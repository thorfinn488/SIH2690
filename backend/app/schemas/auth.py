from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.user import UserRole


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    phone: str = Field(..., min_length=5, max_length=50)
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.ARTISAN
    # Role specific optional fields:
    region: Optional[str] = "India"
    craft_specialty: Optional[str] = "Handicrafts"
    company_name: Optional[str] = None
    requirements: Optional[str] = None


class LoginRequest(BaseModel):
    phone: str = Field(...)
    password: str = Field(...)


class AuthTokenResponse(BaseModel):
    user_id: str
    name: str
    role: str
    token: str

    model_config = ConfigDict(from_attributes=True)


class UserMeResponse(BaseModel):
    user_id: str
    name: str
    role: str
    phone: str

    model_config = ConfigDict(from_attributes=True)
