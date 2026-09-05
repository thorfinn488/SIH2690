from typing import List
from fastapi import Depends, HTTPException, status
from app.middleware.auth_middleware import get_current_user
from app.models.user import User, UserRole


def require_role(*allowed_roles: str):
    """
    Dependency factory to enforce Role-Based Access Control (RBAC).
    Usage: Depends(require_role("ARTISAN", "ADMIN")) or Depends(require_role("ADMIN"))
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_str = current_user.role.value if isinstance(current_user.role, UserRole) else str(current_user.role)
        normalized_allowed = [r.value if isinstance(r, UserRole) else str(r) for r in allowed_roles]
        
        if user_role_str not in normalized_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden. Required role(s): {', '.join(normalized_allowed)}"
            )
        return current_user

    return role_checker
