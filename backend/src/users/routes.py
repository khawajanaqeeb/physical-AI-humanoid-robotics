"""
User profile management routes.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.database.session import get_db
from src.users.schemas import UserProfileResponse, UpdateProfileRequest
from src.users.services import update_user_profile
from src.core.logging_config import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/profile", tags=["User Profile"])

@router.get(
    "/",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user profile",
    description="Retrieve the authenticated user's profile information including experience levels and interests.",
)
async def get_profile(
    current_user=Depends(get_current_user),
) -> UserProfileResponse:
    """
    Get authenticated user's profile.

    Args:
        current_user: Authenticated user from JWT token

    Returns:
        UserProfileResponse with user details and profile information

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 404: If user profile does not exist (should not happen for authenticated users)
    """
    if not current_user.profile:
        # This should not happen for users created through signup, but handle gracefully
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    # Return user profile response
    return UserProfileResponse(
        user_id=current_user.id,
        email=current_user.email,
        software_experience=current_user.profile.software_experience.value,
        hardware_experience=current_user.profile.hardware_experience.value,
        interests=current_user.profile.interests,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at,
    )


@router.put(
    "/",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user profile",
    description="Update the authenticated user's profile information including experience levels and interests.",
)
async def update_profile(
    profile_update: UpdateProfileRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    """
    Update authenticated user's profile.

    Args:
        profile_update: Request body with profile fields to update
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        UserProfileResponse with updated user details and profile information

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 404: If user profile does not exist
        HTTPException 422: If experience levels are invalid
    """
    if not current_user.profile:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    # Update profile using service
    updated_profile = update_user_profile(
        db=db,
        user_id=current_user.id,
        software_experience=profile_update.software_experience,
        hardware_experience=profile_update.hardware_experience,
        interests=profile_update.interests,
    )

    # Return updated profile response
    return UserProfileResponse(
        user_id=current_user.id,
        email=current_user.email,
        software_experience=updated_profile.software_experience.value,
        hardware_experience=updated_profile.hardware_experience.value,
        interests=updated_profile.interests,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at,
    )