"""
Admin endpoints for user and system management.
"""

import logging
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from corebank.models.user import UserRole, UserDetailResponse
from corebank.models.common import PaginatedResponse, PaginationParams
from corebank.core.permissions import get_current_user_role, verify_admin_access
from corebank.services.user_service import UserService
from corebank.api.v1.dependencies import get_user_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=PaginatedResponse[UserDetailResponse])
async def get_all_users(
    _: Annotated[None, Depends(verify_admin_access)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by user role")
) -> PaginatedResponse[UserDetailResponse]:
    """
    Get all users with pagination and optional role filtering.
    
    Args:
        _: Admin access verification
        user_service: User service dependency
        page: Page number
        page_size: Items per page
        role: Optional role filter
        
    Returns:
        PaginatedResponse[UserDetailResponse]: Paginated user list
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        pagination = PaginationParams(page=page, page_size=page_size)
        
        users = await user_service.get_all_users(
            pagination=pagination,
            role_filter=role
        )
        
        logger.debug(f"Retrieved {len(users.items)} users, page {page}")
        
        return users
        
    except Exception as e:
        logger.error(f"Failed to retrieve users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: UUID,
    _: Annotated[None, Depends(verify_admin_access)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserDetailResponse:
    """
    Get detailed information about a specific user.
    
    Args:
        user_id: User ID
        _: Admin access verification
        user_service: User service dependency
        
    Returns:
        UserDetailResponse: Detailed user information
        
    Raises:
        HTTPException: If user not found or retrieval fails
    """
    try:
        user = await user_service.get_user_detail_by_id(user_id)
        
        logger.debug(f"Retrieved user detail for {user_id}")
        
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to retrieve user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    new_role: UserRole,
    _: Annotated[None, Depends(verify_admin_access)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserDetailResponse:
    """
    Update a user's role.
    
    Args:
        user_id: User ID
        new_role: New role to assign
        _: Admin access verification
        user_service: User service dependency
        
    Returns:
        UserDetailResponse: Updated user information
        
    Raises:
        HTTPException: If user not found or update fails
    """
    try:
        updated_user = await user_service.update_user_role(user_id, new_role)
        
        logger.info(f"Updated user {user_id} role to {new_role}")
        
        # Return detailed user info
        return await user_service.get_user_detail_by_id(user_id)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update user {user_id} role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )


@router.get("/statistics")
async def get_system_statistics(
    _: Annotated[None, Depends(verify_admin_access)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> dict:
    """
    Get system statistics for admin dashboard.
    
    Args:
        _: Admin access verification
        user_service: User service dependency
        
    Returns:
        dict: System statistics
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        stats = await user_service.get_user_statistics()
        
        logger.debug("Retrieved system statistics")
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to retrieve system statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system statistics"
        )
