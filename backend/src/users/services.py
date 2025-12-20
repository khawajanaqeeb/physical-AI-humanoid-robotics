"""
User service layer for business logic.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.auth.security import hash_password, verify_password, create_access_token, create_refresh_token
from src.users.models import User, UserProfile, Session as UserSession, SoftwareExperience, HardwareExperience
from src.core.config import get_settings

settings = get_settings()


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing email."""
    pass


class UserNotFoundError(Exception):
    """Raised when user is not found."""
    pass


def create_user(
    db: Session,
    email: str,
    password: str,
    software_experience: str,
    hardware_experience: str,
    interests: list[str],
) -> User:
    """
    Create a new user with profile atomically.

    Args:
        db: Database session
        email: User email (must be unique)
        password: Plain text password (will be hashed)
        software_experience: Software experience level (BEGINNER/INTERMEDIATE/ADVANCED)
        hardware_experience: Hardware experience level (NONE/BASIC/ADVANCED)
        interests: List of interest strings

    Returns:
        Created User object with profile loaded

    Raises:
        UserAlreadyExistsError: If email already exists
    """
    # Check if user already exists
    existing_user = db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if existing_user:
        raise UserAlreadyExistsError(f"User with email {email} already exists")

    # Hash password
    hashed_password = hash_password(password)

    # Create user
    user = User(
        email=email,
        hashed_password=hashed_password,
        is_active=True,
    )
    db.add(user)
    db.flush()  # Flush to get user.id

    # Create profile
    profile = UserProfile(
        user_id=user.id,
        software_experience=SoftwareExperience(software_experience),
        hardware_experience=HardwareExperience(hardware_experience),
        interests=interests,
    )
    db.add(profile)

    # Commit transaction
    db.commit()
    db.refresh(user)

    return user


def create_user_session(
    db: Session,
    user_id: UUID,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> tuple[str, str]:
    """
    Create a new session for a user (generates access and refresh tokens).

    Args:
        db: Database session
        user_id: User's UUID
        user_agent: Optional user agent string from request
        ip_address: Optional IP address from request

    Returns:
        Tuple of (access_token, refresh_token)
    """
    # Create access token
    access_token = create_access_token(str(user_id))

    # Create refresh token
    refresh_token, expires_at = create_refresh_token()

    # Store session in database
    session = UserSession(
        user_id=user_id,
        refresh_token=refresh_token,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    db.add(session)

    # Update last_login_at
    user = db.get(User, user_id)
    if user:
        user.last_login_at = datetime.now(timezone.utc)

    db.commit()

    return access_token, refresh_token


def get_user_with_profile(db: Session, user_id: UUID) -> Optional[User]:
    """
    Get user by ID with profile eagerly loaded.

    Args:
        db: Database session
        user_id: User's UUID

    Returns:
        User object with profile loaded, or None if not found
    """
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(joinedload(User.profile))
    )
    user = db.execute(stmt).scalar_one_or_none()
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get user by email.

    Args:
        db: Database session
        email: User email

    Returns:
        User object or None if not found
    """
    stmt = select(User).where(User.email == email)
    user = db.execute(stmt).scalar_one_or_none()
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate user with email and password.

    Args:
        db: Database session
        email: User email
        password: Plain text password

    Returns:
        User object if credentials valid and account active, None otherwise
    """
    # Get user by email
    user = get_user_by_email(db, email)
    if not user:
        return None

    # Verify password
    if not verify_password(password, user.hashed_password):
        return None

    # Check if account is active
    if not user.is_active:
        return None

    return user


def delete_user_session(db: Session, refresh_token: str) -> bool:
    """
    Delete a user session by refresh token (signout).

    Args:
        db: Database session
        refresh_token: Refresh token to invalidate

    Returns:
        True if session was deleted, False if not found
    """
    stmt = select(UserSession).where(UserSession.refresh_token == refresh_token)
    session = db.execute(stmt).scalar_one_or_none()

    if session:
        db.delete(session)
        db.commit()
        return True

    return False


def refresh_user_session(
    db: Session,
    refresh_token: str,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> Optional[tuple[str, str]]:
    """
    Refresh access token using valid refresh token.

    Args:
        db: Database session
        refresh_token: Refresh token to validate
        user_agent: Optional user agent string
        ip_address: Optional IP address

    Returns:
        Tuple of (new_access_token, new_refresh_token) if successful, None if invalid
    """
    # Find existing session
    stmt = select(UserSession).where(UserSession.refresh_token == refresh_token)
    session = db.execute(stmt).scalar_one_or_none()

    if not session:
        return None

    # Check if refresh token has expired
    if session.expires_at < datetime.now(timezone.utc):
        # Delete expired session
        db.delete(session)
        db.commit()
        return None

    # Get user
    user = db.get(User, session.user_id)
    if not user or not user.is_active:
        return None

    # Create new tokens
    new_access_token = create_access_token(str(user.id))
    new_refresh_token, new_expires_at = create_refresh_token()

    # Update session with new refresh token and expiration
    session.refresh_token = new_refresh_token
    session.expires_at = new_expires_at
    session.user_agent = user_agent
    session.ip_address = ip_address

    # Update user's last login time
    user.last_login_at = datetime.now(timezone.utc)

    db.commit()

    return new_access_token, new_refresh_token


def update_user_profile(
    db: Session,
    user_id: UUID,
    software_experience: Optional[str] = None,
    hardware_experience: Optional[str] = None,
    interests: Optional[list[str]] = None,
) -> UserProfile:
    """
    Update user profile fields.

    Args:
        db: Database session
        user_id: User's UUID
        software_experience: Optional new software experience level
        hardware_experience: Optional new hardware experience level
        interests: Optional new interests list

    Returns:
        Updated UserProfile object

    Raises:
        UserNotFoundError: If user or profile not found
    """
    # Get profile
    stmt = select(UserProfile).where(UserProfile.user_id == user_id)
    profile = db.execute(stmt).scalar_one_or_none()

    if not profile:
        raise UserNotFoundError(f"Profile not found for user {user_id}")

    # Update fields if provided
    if software_experience is not None:
        profile.software_experience = SoftwareExperience(software_experience)
    if hardware_experience is not None:
        profile.hardware_experience = HardwareExperience(hardware_experience)
    if interests is not None:
        profile.interests = interests

    db.commit()
    db.refresh(profile)

    return profile
