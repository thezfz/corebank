"""
Transaction endpoints for CoreBank API v1.

This module provides endpoints for transaction operations including
deposits, withdrawals, transfers, and transaction history.
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from corebank.api.v1.dependencies import get_current_user_id, get_transaction_service
from corebank.models.transaction import (
    DepositRequest, WithdrawalRequest, TransferRequest,
    TransactionResponse, TransactionSummary
)
from corebank.models.common import PaginationParams, PaginatedResponse
from corebank.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/deposit", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def deposit_funds(
    deposit_request: DepositRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    transaction_service: Annotated[TransactionService, Depends(get_transaction_service)]
) -> TransactionResponse:
    """
    Deposit funds to an account.
    
    Args:
        deposit_request: Deposit request data
        current_user_id: Current user ID
        transaction_service: Transaction service dependency
        
    Returns:
        TransactionResponse: Transaction details
        
    Raises:
        HTTPException: If deposit fails
    """
    try:
        transaction = await transaction_service.deposit(current_user_id, deposit_request)
        
        logger.info(
            f"Deposit successful: {deposit_request.amount} to account "
            f"{deposit_request.account_id} by user {current_user_id}"
        )
        
        return transaction
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Deposit failed for user {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Deposit transaction failed"
        )


@router.post("/withdraw", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def withdraw_funds(
    withdrawal_request: WithdrawalRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    transaction_service: Annotated[TransactionService, Depends(get_transaction_service)]
) -> TransactionResponse:
    """
    Withdraw funds from an account.
    
    Args:
        withdrawal_request: Withdrawal request data
        current_user_id: Current user ID
        transaction_service: Transaction service dependency
        
    Returns:
        TransactionResponse: Transaction details
        
    Raises:
        HTTPException: If withdrawal fails
    """
    try:
        transaction = await transaction_service.withdraw(current_user_id, withdrawal_request)
        
        logger.info(
            f"Withdrawal successful: {withdrawal_request.amount} from account "
            f"{withdrawal_request.account_id} by user {current_user_id}"
        )
        
        return transaction
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Withdrawal failed for user {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Withdrawal transaction failed"
        )


@router.post("/transfer", response_model=list[TransactionResponse], status_code=status.HTTP_201_CREATED)
async def transfer_funds(
    transfer_request: TransferRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    transaction_service: Annotated[TransactionService, Depends(get_transaction_service)]
) -> list[TransactionResponse]:
    """
    Transfer funds between accounts.
    
    Args:
        transfer_request: Transfer request data
        current_user_id: Current user ID
        transaction_service: Transaction service dependency
        
    Returns:
        list[TransactionResponse]: Source and target transaction details
        
    Raises:
        HTTPException: If transfer fails
    """
    try:
        from_transaction, to_transaction = await transaction_service.transfer(
            current_user_id, transfer_request
        )
        
        logger.info(
            f"Transfer successful: {transfer_request.amount} from "
            f"{transfer_request.from_account_id} to {transfer_request.to_account_id} "
            f"by user {current_user_id}"
        )
        
        return [from_transaction, to_transaction]
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Transfer failed for user {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transfer transaction failed"
        )


@router.get("/account/{account_id}", response_model=PaginatedResponse[TransactionResponse])
async def get_account_transactions(
    account_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    transaction_service: Annotated[TransactionService, Depends(get_transaction_service)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
) -> PaginatedResponse[TransactionResponse]:
    """
    Get transaction history for an account.
    
    Args:
        account_id: Account ID
        current_user_id: Current user ID
        transaction_service: Transaction service dependency
        page: Page number
        page_size: Items per page
        
    Returns:
        PaginatedResponse[TransactionResponse]: Paginated transaction history
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        pagination = PaginationParams(page=page, page_size=page_size)
        
        transactions = await transaction_service.get_transaction_history(
            current_user_id, account_id, pagination
        )
        
        logger.debug(
            f"Retrieved transaction history for account {account_id}, "
            f"page {page}, user {current_user_id}"
        )
        
        return transactions
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            f"Failed to retrieve transactions for account {account_id}, "
            f"user {current_user_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction history"
        )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    transaction_service: Annotated[TransactionService, Depends(get_transaction_service)]
) -> TransactionResponse:
    """
    Get a specific transaction.
    
    Args:
        transaction_id: Transaction ID
        current_user_id: Current user ID
        transaction_service: Transaction service dependency
        
    Returns:
        TransactionResponse: Transaction details
        
    Raises:
        HTTPException: If transaction not found or access denied
    """
    try:
        transaction = await transaction_service.get_transaction(
            current_user_id, transaction_id
        )
        
        logger.debug(f"Retrieved transaction {transaction_id} for user {current_user_id}")
        
        return transaction
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            f"Failed to retrieve transaction {transaction_id} for user {current_user_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction"
        )


@router.get("/account/{account_id}/summary", response_model=TransactionSummary)
async def get_transaction_summary(
    account_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    transaction_service: Annotated[TransactionService, Depends(get_transaction_service)]
) -> TransactionSummary:
    """
    Get transaction summary for an account.
    
    Args:
        account_id: Account ID
        current_user_id: Current user ID
        transaction_service: Transaction service dependency
        
    Returns:
        TransactionSummary: Transaction summary data
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        summary = await transaction_service.get_transaction_summary(
            current_user_id, account_id
        )
        
        logger.debug(f"Retrieved transaction summary for account {account_id}")
        
        return summary
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            f"Failed to retrieve transaction summary for account {account_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction summary"
        )
