"""
Authentication routes for signup, signin, signout, and token refresh.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from src.auth.schemas import (
    SignupRequest,
    SigninRequest,
    AuthResponse,
    TokenResponse,
    RefreshTokenRequest,
    SignoutRequest,
    MessageResponse,
)
from src.database.session import get_db
from src.users.services import (
    create_user,
    create_user_session,
    get_user_with_profile,
    UserAlreadyExistsError,
)
from src.core.config import get_settings

settings = get_settings()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Router
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Signup",
    description="Create a new user account with profile and receive authentication tokens",
)
@limiter.limit("5/minute")
async def signup(
    request: Request,
    signup_data: SignupRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:
    """
    Create a new user account.

    - **email**: Valid email address (must be unique)
    - **password**: Password with minimum 8 characters, must contain letter and number
    - **software_experience**: BEGINNER, INTERMEDIATE, or ADVANCED
    - **hardware_experience**: NONE, BASIC, or ADVANCED
    - **interests**: List of interest strings (e.g., ["robotics", "AI"])

    Returns authentication tokens (access token + refresh token).
    """
    try:
        # Create user with profile atomically
        user = create_user(
            db=db,
            email=signup_data.email,
            password=signup_data.password,
            software_experience=signup_data.software_experience,
            hardware_experience=signup_data.hardware_experience,
            interests=signup_data.interests,
        )

        # Create session and get tokens
        access_token, refresh_token = create_user_session(
            db=db,
            user_id=user.id,
            user_agent=request.headers.get("user-agent"),
            ip_address=get_remote_address(request),
        )

        # Prepare response
        return AuthResponse(
            user_id=user.id,
            email=user.email,
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.access_token_expire_minutes * 60,
            ),
        )

    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except ValueError as e:
        # Catch ENUM validation errors
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        # Log unexpected errors
        print(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during signup",
        )


@router.post(
    "/signin",
    response_model=AuthResponse,
    summary="User Signin",
    description="Authenticate with email and password to receive tokens",
)
@limiter.limit("5/minute")
async def signin(
    request: Request,
    signin_data: SigninRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:
    """
    Sign in with email and password.

    - **email**: User's email address
    - **password**: User's password

    Returns authentication tokens (access token + refresh token).
    """
    from src.users.services import authenticate_user

    # Authenticate user
    user = authenticate_user(db, signin_data.email, signin_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Create session and get tokens
    access_token, refresh_token = create_user_session(
        db=db,
        user_id=user.id,
        user_agent=request.headers.get("user-agent"),
        ip_address=get_remote_address(request),
    )

    # Prepare response
    return AuthResponse(
        user_id=user.id,
        email=user.email,
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        ),
    )


@router.post(
    "/signout",
    response_model=MessageResponse,
    summary="User Signout",
    description="Invalidate refresh token to sign out",
)
async def signout(
    signout_data: SignoutRequest,
    db: Session = Depends(get_db),
) -> MessageResponse:
    """
    Sign out by invalidating the refresh token.

    - **refresh_token**: The refresh token to invalidate
    """
    from src.users.services import delete_user_session

    # Delete session
    deleted = delete_user_session(db, signout_data.refresh_token)
    if not deleted:
        # Still return success even if token was already invalid/expired
        pass

    return MessageResponse(message="Successfully signed out")


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh Access Token",
    description="Use refresh token to get a new access token",
)
async def refresh_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Refresh access token using a valid refresh token.

    - **refresh_token**: Valid refresh token from signin/signup

    Returns new authentication tokens.
    """
    from src.users.services import refresh_user_session

    # Refresh session
    tokens = refresh_user_session(
        db=db,
        refresh_token=refresh_data.refresh_token,
        user_agent=request.headers.get("user-agent"),
        ip_address=get_remote_address(request),
    )

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    access_token, refresh_token = tokens

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )
