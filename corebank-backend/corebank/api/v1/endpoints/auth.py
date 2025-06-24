"""
Authentication endpoints for CoreBank API v1.

This module provides endpoints for user registration, login, and token management.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from corebank.api.v1.dependencies import get_postgres_repository
from corebank.models.user import UserCreate, UserLogin, UserResponse
from corebank.models.common import Token, MessageResponse
from corebank.repositories.postgres_repo import PostgresRepository
from corebank.security.password import hash_password, verify_password, validate_password_strength
from corebank.security.token import create_user_token
from corebank.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    repository: Annotated[PostgresRepository, Depends(get_postgres_repository)]
) -> UserResponse:
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        repository: Repository dependency
        
    Returns:
        UserResponse: Created user data
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        # Validate password strength
        password_validation = validate_password_strength(user_data.password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet security requirements",
                    "issues": password_validation["issues"]
                }
            )
        
        # Check if username already exists
        existing_user = await repository.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already registered"
            )
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user
        user = await repository.create_user(
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        logger.info(f"User registered successfully: {user_data.username}")
        
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    repository: Annotated[PostgresRepository, Depends(get_postgres_repository)]
) -> Token:
    """
    Authenticate user and return access token.
    
    Args:
        user_credentials: User login credentials
        repository: Repository dependency
        
    Returns:
        Token: Access token and metadata
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Get user by username
        user = await repository.get_user_by_username(user_credentials.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password
        if not verify_password(user_credentials.password, user["hashed_password"]):
            logger.warning(f"Failed login attempt for user: {user_credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Create access token
        access_token = create_user_token(
            user_id=user["id"],
            username=user["username"]
        )
        
        logger.info(f"User logged in successfully: {user_credentials.username}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/login/form", response_model=Token)
async def login_user_form(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    repository: Annotated[PostgresRepository, Depends(get_postgres_repository)]
) -> Token:
    """
    Authenticate user using OAuth2 password flow (for compatibility).
    
    Args:
        form_data: OAuth2 form data
        repository: Repository dependency
        
    Returns:
        Token: Access token and metadata
        
    Raises:
        HTTPException: If authentication fails
    """
    # Convert form data to UserLogin model
    user_credentials = UserLogin(
        username=form_data.username,
        password=form_data.password
    )
    
    # Use the same login logic
    return await login_user(user_credentials, repository)


@router.post("/validate-token", response_model=MessageResponse)
async def validate_token(
    token: str,
    repository: Annotated[PostgresRepository, Depends(get_postgres_repository)]
) -> MessageResponse:
    """
    Validate a JWT token.
    
    Args:
        token: JWT token to validate
        repository: Repository dependency
        
    Returns:
        MessageResponse: Validation result
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        from corebank.security.token import get_user_id_from_token
        
        # Verify token and extract user ID
        user_id = get_user_id_from_token(token)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Verify user still exists
        user = await repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return MessageResponse(message="Token is valid")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token validation failed"
        )


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    token: str,
    repository: Annotated[PostgresRepository, Depends(get_postgres_repository)]
) -> Token:
    """
    Refresh an access token.
    
    Args:
        token: Current JWT token
        repository: Repository dependency
        
    Returns:
        Token: New access token and metadata
        
    Raises:
        HTTPException: If token refresh fails
    """
    try:
        from corebank.security.token import token_manager
        
        # Refresh the token
        new_token = token_manager.refresh_token(token)
        if new_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        logger.info("Token refreshed successfully")
        
        return Token(
            access_token=new_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )
