"""
FastAPI dependencies for authentication.
"""
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.auth.security import get_user_id_from_token
from src.database.session import get_db
from src.users.models import User
from src.users.services import get_user_with_profile

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user.

    Validates JWT access token and returns User object.

    Args:
        credentials: HTTP Authorization header with Bearer token
        db: Database session

    Returns:
        User object with profile loaded

    Raises:
        HTTPException 401: If token is invalid or user not found
    """
    token = credentials.credentials

    # Decode token
    user_id_str = get_user_id_from_token(token)
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_with_profile(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Dependency to optionally get the current authenticated user.

    Returns None if no token provided or token is invalid.
    Useful for endpoints that support both authenticated and unauthenticated access.

    Args:
        credentials: Optional HTTP Authorization header with Bearer token
        db: Database session

    Returns:
        User object with profile loaded, or None if not authenticated
    """
    if credentials is None:
        return None

    token = credentials.credentials

    # Decode token
    user_id_str = get_user_id_from_token(token)
    if user_id_str is None:
        return None

    # Get user from database
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        return None

    user = get_user_with_profile(db, user_id)
    if user is None or not user.is_active:
        return None

    return user
