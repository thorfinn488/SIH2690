import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from app.config.settings import settings

ALGORITHM = "HS256"


def create_access_token(payload_data: Dict[str, Any], expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token.
    Payload must contain user_id and role.
    """
    to_encode = payload_data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.
    Raises PyJWTError if token is invalid or expired.
    """
    try:
        decoded_data = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.PyJWTError:
        raise
