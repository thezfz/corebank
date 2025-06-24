"""
Account management endpoints for CoreBank API v1.

This module provides endpoints for account creation, retrieval, and management.
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from corebank.api.v1.dependencies import (
    get_current_user_id, get_account_service, verify_account_access
)
from corebank.models.account import (
    AccountCreate, AccountResponse, AccountSummary, AccountBalance
)
from corebank.models.common import MessageResponse
from corebank.services.account_service import AccountService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    account_service: Annotated[AccountService, Depends(get_account_service)]
) -> AccountResponse:
    """
    Create a new account for the current user.
    
    Args:
        account_data: Account creation data
        current_user_id: Current user ID
        account_service: Account service dependency
        
    Returns:
        AccountResponse: Created account data
        
    Raises:
        HTTPException: If account creation fails
    """
    try:
        account = await account_service.create_account(current_user_id, account_data)
        
        logger.info(f"Account created: {account.account_number} for user {current_user_id}")
        
        return account
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Account creation failed for user {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account creation failed"
        )


@router.get("", response_model=list[AccountResponse])
async def get_user_accounts(
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    account_service: Annotated[AccountService, Depends(get_account_service)]
) -> list[AccountResponse]:
    """
    Get all accounts for the current user.
    
    Args:
        current_user_id: Current user ID
        account_service: Account service dependency
        
    Returns:
        list[AccountResponse]: List of user's accounts
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        accounts = await account_service.get_user_accounts(current_user_id)
        
        logger.debug(f"Retrieved {len(accounts)} accounts for user {current_user_id}")
        
        return accounts
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to retrieve accounts for user {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve accounts"
        )


@router.get("/summary", response_model=AccountSummary)
async def get_account_summary(
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    account_service: Annotated[AccountService, Depends(get_account_service)]
) -> AccountSummary:
    """
    Get account summary for the current user.
    
    Args:
        current_user_id: Current user ID
        account_service: Account service dependency
        
    Returns:
        AccountSummary: Account summary data
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        summary = await account_service.get_account_summary(current_user_id)
        
        logger.debug(f"Retrieved account summary for user {current_user_id}")
        
        return summary
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to retrieve account summary for user {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve account summary"
        )


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    account_service: Annotated[AccountService, Depends(get_account_service)]
) -> AccountResponse:
    """
    Get a specific account.
    
    Args:
        account_id: Account ID
        current_user_id: Current user ID
        account_service: Account service dependency
        
    Returns:
        AccountResponse: Account data
        
    Raises:
        HTTPException: If account not found or access denied
    """
    try:
        account = await account_service.get_account(account_id, current_user_id)
        
        logger.debug(f"Retrieved account {account_id} for user {current_user_id}")
        
        return account
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to retrieve account {account_id} for user {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve account"
        )


@router.get("/{account_id}/balance", response_model=AccountBalance)
async def get_account_balance(
    account_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    account_service: Annotated[AccountService, Depends(get_account_service)]
) -> AccountBalance:
    """
    Get account balance.
    
    Args:
        account_id: Account ID
        current_user_id: Current user ID
        account_service: Account service dependency
        
    Returns:
        AccountBalance: Account balance data
        
    Raises:
        HTTPException: If account not found or access denied
    """
    try:
        # Get account details
        account = await account_service.get_account(account_id, current_user_id)
        
        # Create balance response
        balance_response = AccountBalance(
            account_id=account.id,
            account_number=account.account_number,
            balance=account.balance,
            account_type=account.account_type
        )
        
        logger.debug(f"Retrieved balance for account {account_id}")
        
        return balance_response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to retrieve balance for account {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve account balance"
        )
