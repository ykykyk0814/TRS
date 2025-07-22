from uuid import UUID

from fastapi import Depends, HTTPException

from app.api.auth import fastapi_users
from app.core.models import User

# Authentication dependencies
current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
optional_current_user = fastapi_users.current_user(optional=True)


def get_user_or_superuser(
    target_user_id: UUID, current_user: User = Depends(current_user)
) -> User:
    """
    Dependency that allows access if the user is accessing their own data
    or if they are a superuser.
    """
    if target_user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Access denied. You can only access your own data."
        )
    return current_user


def require_superuser(current_user: User = Depends(current_user)) -> User:
    """Dependency that requires superuser privileges."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser privileges required")
    return current_user
