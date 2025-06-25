"""
Dependency injection providers for CoreBank API v1.

This module provides all dependency injection functions for FastAPI endpoints.
It centralizes the creation and management of service instances and handles
authentication and authorization.
"""

import logging
from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from corebank.core.config import get_settings, Settings
from corebank.core.db import get_db_manager, DatabaseManager
from corebank.repositories.postgres_repo import PostgresRepository
from corebank.services.account_service import AccountService
from corebank.services.transaction_service import TransactionService
from corebank.services.investment_service import InvestmentService
from corebank.security.token import get_user_id_from_token, verify_token
from corebank.models.common import TokenData

logger = logging.getLogger(__name__)

# Security scheme for JWT authentication
security = HTTPBearer(auto_error=False)


# Core dependencies

def get_settings_dependency() -> Settings:
    """
    Get application settings.
    
    Returns:
        Settings: Application settings instance
    """
    return get_settings()


def get_database_manager() -> DatabaseManager:
    """
    Get database manager instance.
    
    Returns:
        DatabaseManager: Database manager instance
    """
    return get_db_manager()


def get_postgres_repository(
    db_manager: Annotated[DatabaseManager, Depends(get_database_manager)]
) -> PostgresRepository:
    """
    Get PostgreSQL repository instance.
    
    Args:
        db_manager: Database manager dependency
        
    Returns:
        PostgresRepository: Repository instance
    """
    return PostgresRepository(db_manager)


def get_account_service(
    repository: Annotated[PostgresRepository, Depends(get_postgres_repository)]
) -> AccountService:
    """
    Get account service instance.
    
    Args:
        repository: Repository dependency
        
    Returns:
        AccountService: Account service instance
    """
    return AccountService(repository)


def get_transaction_service(
    repository: Annotated[PostgresRepository, Depends(get_postgres_repository)]
) -> TransactionService:
    """
    Get transaction service instance.

    Args:
        repository: Repository dependency

    Returns:
        TransactionService: Transaction service instance
    """
    return TransactionService(repository)


def get_investment_service(
    repository: Annotated[PostgresRepository, Depends(get_postgres_repository)]
) -> InvestmentService:
    """
    Get investment service instance.

    Args:
        repository: Repository dependency

    Returns:
        InvestmentService: Investment service instance
    """
    return InvestmentService(repository)


# Authentication dependencies

async def get_token_from_header(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Optional[str]: JWT token if present, None otherwise
    """
    if credentials is None:
        return None
    
    if credentials.scheme.lower() != "bearer":
        return None
    
    return credentials.credentials


async def get_current_user_optional(
    token: Annotated[Optional[str], Depends(get_token_from_header)],
    repository: Annotated[PostgresRepository, Depends(get_postgres_repository)]
) -> Optional[dict]:
    """
    Get current user from JWT token (optional).
    
    Args:
        token: JWT token from header
        repository: Repository dependency
        
    Returns:
        Optional[dict]: User data if authenticated, None otherwise
    """
    if token is None:
        return None
    
    # Verify token and extract user ID
    user_id = get_user_id_from_token(token)
    if user_id is None:
        return None
    
    # Get user from database
    try:
        user = await repository.get_user_by_id(user_id)
        if user:
            logger.debug(f"Authenticated user: {user['username']}")
        return user
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}")
        return None


async def get_current_user(
    token: Annotated[Optional[str], Depends(get_token_from_header)],
    repository: Annotated[PostgresRepository, Depends(get_postgres_repository)]
) -> dict:
    """
    Get current user from JWT token (required).
    
    Args:
        token: JWT token from header
        repository: Repository dependency
        
    Returns:
        dict: User data
        
    Raises:
        HTTPException: If authentication fails
    """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token and extract user ID
    user_id = get_user_id_from_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    try:
        user = await repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"Authenticated user: {user['username']}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )


async def get_current_user_id(
    current_user: Annotated[dict, Depends(get_current_user)]
) -> UUID:
    """
    Get current user ID.
    
    Args:
        current_user: Current user dependency
        
    Returns:
        UUID: User ID
    """
    return current_user['id']


# Authorization helpers

async def verify_account_access(
    account_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    account_service: Annotated[AccountService, Depends(get_account_service)]
) -> None:
    """
    Verify that the current user has access to an account.
    
    Args:
        account_id: Account ID to check
        current_user_id: Current user ID
        account_service: Account service dependency
        
    Raises:
        HTTPException: If access is denied
    """
    try:
        has_access = await account_service.validate_account_access(
            account_id, current_user_id
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this account"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying account access: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authorization error"
        )


# Health check dependency

async def get_health_status(
    repository: Annotated[PostgresRepository, Depends(get_postgres_repository)]
) -> dict:
    """
    Get application health status.
    
    Args:
        repository: Repository dependency
        
    Returns:
        dict: Health status information
    """
    try:
        db_health = await repository.health_check()
        return {
            "status": "healthy" if db_health["status"] == "healthy" else "unhealthy",
            "database": db_health,
            "timestamp": db_health.get("timestamp")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": {"status": "unhealthy", "error": str(e)}
        }
