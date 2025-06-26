"""
Admin endpoints for user and system management.
"""

import logging
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from corebank.models.user import UserRole, UserDetailResponse, UserSoftDelete, UserRestore
from corebank.models.common import PaginatedResponse, PaginationParams, MessageResponse
from corebank.models.account import AccountResponse
from corebank.models.transaction import EnhancedTransactionResponse
from corebank.core.permissions import get_current_user_role, verify_admin_access
from corebank.services.user_service import UserService
from corebank.services.account_service import AccountService
from corebank.services.transaction_service import TransactionService
from corebank.api.v1.dependencies import get_user_service, get_account_service, get_transaction_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=PaginatedResponse[UserDetailResponse])
async def get_all_users(
    _: Annotated[None, Depends(verify_admin_access)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    status: Optional[str] = Query("active", description="User status filter: active, deleted, all"),
    search: Optional[str] = Query(None, description="Search by username, real name, or email")
) -> PaginatedResponse[UserDetailResponse]:
    """
    Get all users with pagination and optional role filtering.

    Args:
        _: Admin access verification
        user_service: User service dependency
        page: Page number
        page_size: Items per page
        role: Optional role filter
        status: User status filter (active, deleted, all)
        search: Optional search term for username, real name, or email

    Returns:
        PaginatedResponse[UserDetailResponse]: Paginated user list

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        pagination = PaginationParams(page=page, page_size=page_size)

        # Determine include_deleted based on status parameter
        if status == "deleted":
            # Only deleted users
            users = await user_service.get_deleted_users(
                pagination=pagination,
                role_filter=role
            )
        elif status == "all":
            # All users (active and deleted)
            users = await user_service.get_all_users(
                pagination=pagination,
                role_filter=role,
                include_deleted=True,
                search_term=search
            )
        else:
            # Default: only active users
            users = await user_service.get_all_users(
                pagination=pagination,
                role_filter=role,
                include_deleted=False,
                search_term=search
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



@router.delete("/users/{user_id}", response_model=MessageResponse)
async def soft_delete_user(
    user_id: UUID,
    delete_request: UserSoftDelete,
    _: Annotated[None, Depends(verify_admin_access)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> MessageResponse:
    """
    Soft delete a user.

    Args:
        user_id: User ID
        delete_request: Deletion request data
        _: Admin access verification
        user_service: User service dependency

    Returns:
        MessageResponse: Deletion confirmation

    Raises:
        HTTPException: If user not found or deletion fails
    """
    try:
        await user_service.soft_delete_user(user_id, delete_request)

        logger.info(f"Soft deleted user {user_id}. Reason: {delete_request.reason}")

        return MessageResponse(message="用户已成功删除")

    except ValueError as e:
        logger.warning(f"User not found for deletion: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.post("/users/{user_id}/restore", response_model=UserDetailResponse)
async def restore_user(
    user_id: UUID,
    restore_request: UserRestore,
    _: Annotated[None, Depends(verify_admin_access)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserDetailResponse:
    """
    Restore a soft deleted user.

    Args:
        user_id: User ID
        restore_request: Restoration request data
        _: Admin access verification
        user_service: User service dependency

    Returns:
        UserDetailResponse: Restored user information

    Raises:
        HTTPException: If user not found or restoration fails
    """
    try:
        restored_user = await user_service.restore_user(user_id, restore_request.reason)

        logger.info(f"Restored user {user_id}. Reason: {restore_request.reason}")

        # Return detailed user info
        return await user_service.get_user_detail_by_id(user_id)

    except ValueError as e:
        logger.warning(f"User not found for restoration: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to restore user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restore user"
        )


@router.get("/accounts", response_model=list[AccountResponse])
async def get_all_accounts(
    _: Annotated[None, Depends(verify_admin_access)],
    account_service: Annotated[AccountService, Depends(get_account_service)]
) -> list[AccountResponse]:
    """
    Get all accounts in the system for admin monitoring.

    Args:
        _: Admin access verification
        account_service: Account service dependency

    Returns:
        list[AccountResponse]: List of all accounts

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        accounts = await account_service.get_all_accounts()

        logger.debug(f"Retrieved {len(accounts)} accounts for admin")

        return accounts

    except Exception as e:
        logger.error(f"Failed to retrieve all accounts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve accounts"
        )


@router.get("/transactions", response_model=PaginatedResponse[EnhancedTransactionResponse])
async def get_all_transactions(
    _: Annotated[None, Depends(verify_admin_access)],
    transaction_service: Annotated[TransactionService, Depends(get_transaction_service)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    user_search: Optional[str] = Query(None, description="Search by username or real name")
) -> PaginatedResponse[EnhancedTransactionResponse]:
    """
    Get all transactions in the system for admin monitoring.

    Args:
        _: Admin access verification
        transaction_service: Transaction service dependency
        page: Page number
        page_size: Items per page
        account_id: Optional account ID filter
        transaction_type: Optional transaction type filter
        user_search: Optional user search term

    Returns:
        PaginatedResponse[EnhancedTransactionResponse]: Paginated transaction list

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        pagination = PaginationParams(page=page, page_size=page_size)

        transactions = await transaction_service.get_all_transactions_for_admin(
            pagination=pagination,
            account_id=account_id,
            transaction_type=transaction_type,
            user_search=user_search
        )

        logger.debug(f"Retrieved {len(transactions.items)} transactions for admin, page {page}")

        return transactions

    except Exception as e:
        logger.error(f"Failed to retrieve all transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transactions"
        )


@router.get("/transaction-statistics")
async def get_transaction_statistics(
    _: Annotated[None, Depends(verify_admin_access)],
    transaction_service: Annotated[TransactionService, Depends(get_transaction_service)]
) -> dict:
    """
    Get transaction statistics for admin dashboard.

    Args:
        _: Admin access verification
        transaction_service: Transaction service dependency

    Returns:
        dict: Transaction statistics

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        stats = await transaction_service.get_transaction_statistics()

        logger.debug("Retrieved transaction statistics")

        return stats

    except Exception as e:
        logger.error(f"Failed to retrieve transaction statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction statistics"
        )
