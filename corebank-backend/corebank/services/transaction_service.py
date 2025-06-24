"""
Transaction service for CoreBank.

This module provides business logic for transaction operations.
It coordinates between the API layer and the repository layer, implementing
business rules, transaction limits, and ensuring ACID properties.
"""

import logging
from decimal import Decimal
from typing import Optional, Tuple
from uuid import UUID

from corebank.models.transaction import (
    DepositRequest, WithdrawalRequest, TransferRequest,
    TransactionResponse, TransactionHistory, TransactionSummary,
    TransactionType
)
from corebank.models.common import PaginationParams, PaginatedResponse
from corebank.repositories.postgres_repo import PostgresRepository

logger = logging.getLogger(__name__)


class TransactionService:
    """
    Service class for transaction operations.
    
    This class implements business logic for all transaction types including
    deposits, withdrawals, and transfers with proper validation and limits.
    """
    
    # Business rule constants
    MAX_DAILY_WITHDRAWAL = Decimal("10000.00")  # $10,000 daily withdrawal limit
    MAX_SINGLE_TRANSFER = Decimal("50000.00")   # $50,000 single transfer limit
    MIN_TRANSACTION_AMOUNT = Decimal("0.01")    # Minimum transaction amount
    
    def __init__(self, repository: PostgresRepository) -> None:
        """
        Initialize the transaction service.
        
        Args:
            repository: PostgreSQL repository instance
        """
        self.repository = repository
    
    async def deposit(
        self, 
        user_id: UUID, 
        deposit_request: DepositRequest
    ) -> TransactionResponse:
        """
        Process a deposit transaction.
        
        Args:
            user_id: User ID making the deposit
            deposit_request: Deposit request data
            
        Returns:
            TransactionResponse: Transaction details
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If transaction fails
        """
        # Validate amount
        if deposit_request.amount < self.MIN_TRANSACTION_AMOUNT:
            raise ValueError(f"Minimum deposit amount is {self.MIN_TRANSACTION_AMOUNT}")
        
        # Verify account ownership
        if not await self.repository.verify_account_ownership(
            deposit_request.account_id, user_id
        ):
            raise ValueError("Account not found or access denied")
        
        try:
            # Execute deposit transaction
            transaction = await self.repository.execute_deposit(
                account_id=deposit_request.account_id,
                amount=deposit_request.amount,
                description=deposit_request.description
            )
            
            logger.info(
                f"Deposit successful: {deposit_request.amount} to account "
                f"{deposit_request.account_id} by user {user_id}"
            )
            
            return TransactionResponse(**transaction)
            
        except Exception as e:
            logger.error(f"Deposit failed for user {user_id}: {e}")
            raise RuntimeError(f"Deposit transaction failed: {str(e)}")
    
    async def withdraw(
        self, 
        user_id: UUID, 
        withdrawal_request: WithdrawalRequest
    ) -> TransactionResponse:
        """
        Process a withdrawal transaction.
        
        Args:
            user_id: User ID making the withdrawal
            withdrawal_request: Withdrawal request data
            
        Returns:
            TransactionResponse: Transaction details
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If transaction fails
        """
        # Validate amount
        if withdrawal_request.amount < self.MIN_TRANSACTION_AMOUNT:
            raise ValueError(f"Minimum withdrawal amount is {self.MIN_TRANSACTION_AMOUNT}")
        
        if withdrawal_request.amount > self.MAX_DAILY_WITHDRAWAL:
            raise ValueError(f"Maximum daily withdrawal limit is {self.MAX_DAILY_WITHDRAWAL}")
        
        # Verify account ownership and sufficient funds
        account = await self._validate_account_for_withdrawal(
            withdrawal_request.account_id, user_id, withdrawal_request.amount
        )
        
        # Check daily withdrawal limit
        await self._check_daily_withdrawal_limit(
            withdrawal_request.account_id, withdrawal_request.amount
        )
        
        try:
            # Execute withdrawal transaction
            transaction = await self.repository.execute_withdrawal(
                account_id=withdrawal_request.account_id,
                amount=withdrawal_request.amount,
                description=withdrawal_request.description
            )
            
            logger.info(
                f"Withdrawal successful: {withdrawal_request.amount} from account "
                f"{withdrawal_request.account_id} by user {user_id}"
            )
            
            return TransactionResponse(**transaction)
            
        except Exception as e:
            logger.error(f"Withdrawal failed for user {user_id}: {e}")
            raise RuntimeError(f"Withdrawal transaction failed: {str(e)}")
    
    async def transfer(
        self, 
        user_id: UUID, 
        transfer_request: TransferRequest
    ) -> Tuple[TransactionResponse, TransactionResponse]:
        """
        Process a transfer transaction between accounts.
        
        Args:
            user_id: User ID making the transfer
            transfer_request: Transfer request data
            
        Returns:
            Tuple[TransactionResponse, TransactionResponse]: Source and target transactions
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If transaction fails
        """
        # Validate amount
        if transfer_request.amount < self.MIN_TRANSACTION_AMOUNT:
            raise ValueError(f"Minimum transfer amount is {self.MIN_TRANSACTION_AMOUNT}")
        
        if transfer_request.amount > self.MAX_SINGLE_TRANSFER:
            raise ValueError(f"Maximum single transfer limit is {self.MAX_SINGLE_TRANSFER}")
        
        # Validate different accounts
        if transfer_request.from_account_id == transfer_request.to_account_id:
            raise ValueError("Cannot transfer to the same account")
        
        # Verify ownership of source account
        if not await self.repository.verify_account_ownership(
            transfer_request.from_account_id, user_id
        ):
            raise ValueError("Source account not found or access denied")
        
        # Verify ownership of target account (for now, only allow transfers between own accounts)
        if not await self.repository.verify_account_ownership(
            transfer_request.to_account_id, user_id
        ):
            raise ValueError("Target account not found or access denied")
        
        # Validate source account has sufficient funds
        await self._validate_account_for_withdrawal(
            transfer_request.from_account_id, user_id, transfer_request.amount
        )
        
        try:
            # Execute transfer transaction
            from_transaction, to_transaction = await self.repository.execute_transfer(
                from_account_id=transfer_request.from_account_id,
                to_account_id=transfer_request.to_account_id,
                amount=transfer_request.amount,
                description=transfer_request.description
            )
            
            logger.info(
                f"Transfer successful: {transfer_request.amount} from "
                f"{transfer_request.from_account_id} to {transfer_request.to_account_id} "
                f"by user {user_id}"
            )
            
            return (
                TransactionResponse(**from_transaction),
                TransactionResponse(**to_transaction)
            )
            
        except Exception as e:
            logger.error(f"Transfer failed for user {user_id}: {e}")
            raise RuntimeError(f"Transfer transaction failed: {str(e)}")

    async def get_transaction_history(
        self,
        user_id: UUID,
        account_id: UUID,
        pagination: PaginationParams
    ) -> PaginatedResponse[TransactionResponse]:
        """
        Get transaction history for an account.

        Args:
            user_id: User ID for ownership verification
            account_id: Account ID
            pagination: Pagination parameters

        Returns:
            PaginatedResponse[TransactionResponse]: Paginated transaction history

        Raises:
            ValueError: If account not found or access denied
        """
        # Verify account ownership
        if not await self.repository.verify_account_ownership(account_id, user_id):
            raise ValueError("Account not found or access denied")

        # Get transactions with pagination
        transactions = await self.repository.get_account_transactions(
            account_id=account_id,
            limit=pagination.page_size,
            offset=pagination.offset
        )

        # Get total count
        total_count = await self.repository.count_account_transactions(account_id)

        # Convert to response models
        transaction_responses = [
            TransactionResponse(**transaction) for transaction in transactions
        ]

        return PaginatedResponse.create(
            items=transaction_responses,
            total_count=total_count,
            pagination=pagination
        )

    async def get_transaction(
        self,
        user_id: UUID,
        transaction_id: UUID
    ) -> TransactionResponse:
        """
        Get a specific transaction.

        Args:
            user_id: User ID for ownership verification
            transaction_id: Transaction ID

        Returns:
            TransactionResponse: Transaction details

        Raises:
            ValueError: If transaction not found or access denied
        """
        transaction = await self.repository.get_transaction_by_id(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")

        # Verify user has access to the account
        if not await self.repository.verify_account_ownership(
            transaction['account_id'], user_id
        ):
            # Also check related account for transfers
            if (transaction.get('related_account_id') and
                not await self.repository.verify_account_ownership(
                    transaction['related_account_id'], user_id
                )):
                raise ValueError("Transaction not found or access denied")

        return TransactionResponse(**transaction)

    async def get_transaction_summary(
        self,
        user_id: UUID,
        account_id: UUID
    ) -> TransactionSummary:
        """
        Get transaction summary for an account.

        Args:
            user_id: User ID for ownership verification
            account_id: Account ID

        Returns:
            TransactionSummary: Transaction summary data

        Raises:
            ValueError: If account not found or access denied
        """
        # Verify account ownership
        if not await self.repository.verify_account_ownership(account_id, user_id):
            raise ValueError("Account not found or access denied")

        summary_data = await self.repository.get_transaction_summary(account_id)

        # Convert to the expected format
        transactions_by_type = {
            TransactionType.DEPOSIT: summary_data.get('deposits', 0),
            TransactionType.WITHDRAWAL: summary_data.get('withdrawals', 0),
            TransactionType.TRANSFER: summary_data.get('transfers', 0)
        }

        return TransactionSummary(
            total_transactions=summary_data.get('total_transactions', 0),
            total_deposits=summary_data.get('total_deposits', Decimal('0.00')),
            total_withdrawals=summary_data.get('total_withdrawals', Decimal('0.00')),
            total_transfers_in=summary_data.get('total_transfers_in', Decimal('0.00')),
            total_transfers_out=summary_data.get('total_transfers_out', Decimal('0.00')),
            transactions_by_type=transactions_by_type
        )

    # Private helper methods

    async def _validate_account_for_withdrawal(
        self,
        account_id: UUID,
        user_id: UUID,
        amount: Decimal
    ) -> dict:
        """
        Validate account for withdrawal operations.

        Args:
            account_id: Account ID
            user_id: User ID for ownership verification
            amount: Withdrawal amount

        Returns:
            dict: Account data if valid

        Raises:
            ValueError: If validation fails
        """
        # Verify account ownership
        if not await self.repository.verify_account_ownership(account_id, user_id):
            raise ValueError("Account not found or access denied")

        account = await self.repository.get_account_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        # Check sufficient funds
        if account['balance'] < amount:
            raise ValueError("Insufficient funds")

        return account

    async def _check_daily_withdrawal_limit(
        self,
        account_id: UUID,
        amount: Decimal
    ) -> None:
        """
        Check if withdrawal amount exceeds daily limit.

        Args:
            account_id: Account ID
            amount: Withdrawal amount

        Raises:
            ValueError: If daily limit would be exceeded
        """
        # For now, we'll implement a simple check against the maximum single withdrawal
        # In a real system, you would track daily withdrawal totals
        if amount > self.MAX_DAILY_WITHDRAWAL:
            raise ValueError(f"Amount exceeds daily withdrawal limit of {self.MAX_DAILY_WITHDRAWAL}")

        # TODO: Implement actual daily withdrawal tracking
        # This would involve:
        # 1. Getting all withdrawals for the account in the last 24 hours
        # 2. Summing the amounts
        # 3. Checking if current withdrawal + sum > daily limit
