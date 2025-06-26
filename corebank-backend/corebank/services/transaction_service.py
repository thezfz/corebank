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
    DepositRequest, WithdrawalRequest, TransferRequest, TransferByAccountNumberRequest,
    TransactionResponse, TransactionHistory, TransactionSummary,
    TransactionType, EnhancedTransactionResponse
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
    MAX_CROSS_USER_TRANSFER = Decimal("10000.00")  # $10,000 cross-user transfer limit
    MAX_DAILY_CROSS_USER_TRANSFER = Decimal("20000.00")  # $20,000 daily cross-user transfer limit
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
        
        # Verify target account exists (allow transfers to any valid account)
        target_account = await self.repository.get_account_by_id(transfer_request.to_account_id)
        if not target_account:
            raise ValueError("Target account not found")
        
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
        Get transaction history for an account, including investment transactions.

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

        # Get regular transactions
        regular_transactions = await self.repository.get_account_transactions(
            account_id=account_id,
            limit=pagination.page_size * 2,  # Get more to ensure we have enough after merging
            offset=0
        )

        # Get investment transactions for this account
        all_investment_transactions = await self.repository.get_user_investment_transactions(
            user_id=user_id,
            limit=1000,  # Get all investment transactions
            skip=0
        )

        # Filter investment transactions for this specific account
        account_investment_transactions = [
            tx for tx in all_investment_transactions
            if tx['account_id'] == account_id
        ]

        # Convert investment transactions to regular transaction format
        converted_investment_transactions = []
        for inv_tx in account_investment_transactions:
            # Map investment transaction types to Chinese
            transaction_type_map = {
                'purchase': '理财申购',
                'redemption': '理财赎回'
            }
            chinese_type = transaction_type_map.get(inv_tx['transaction_type'], f"投资{inv_tx['transaction_type']}")

            converted_tx = {
                'id': inv_tx['id'],
                'account_id': inv_tx['account_id'],
                'transaction_type': chinese_type,
                'amount': inv_tx['amount'],
                'related_account_id': None,
                'description': inv_tx.get('description', chinese_type),
                'status': 'completed' if inv_tx['status'] == 'confirmed' else inv_tx['status'],
                'timestamp': inv_tx['created_at']
            }
            converted_investment_transactions.append(converted_tx)

        # Merge and sort all transactions by timestamp
        all_transactions = regular_transactions + converted_investment_transactions
        all_transactions.sort(key=lambda x: x['timestamp'], reverse=True)

        # Apply pagination
        start_idx = pagination.offset
        end_idx = start_idx + pagination.page_size
        paginated_transactions = all_transactions[start_idx:end_idx]

        # Convert to response models
        transaction_responses = [
            TransactionResponse(**transaction) for transaction in paginated_transactions
        ]

        # Calculate total count
        regular_count = await self.repository.count_account_transactions(account_id)
        investment_count = len(account_investment_transactions)
        total_count = regular_count + investment_count

        return PaginatedResponse.create(
            items=transaction_responses,
            total_count=total_count,
            pagination=pagination
        )

    async def get_enhanced_transaction_history(
        self,
        user_id: UUID,
        account_id: UUID,
        pagination: PaginationParams
    ) -> PaginatedResponse[EnhancedTransactionResponse]:
        """
        Get enhanced transaction history for an account with related user information.

        Args:
            user_id: User ID for ownership verification
            account_id: Account ID
            pagination: Pagination parameters

        Returns:
            PaginatedResponse[EnhancedTransactionResponse]: Paginated enhanced transaction history

        Raises:
            ValueError: If account not found or access denied
        """
        # Verify account ownership
        if not await self.repository.verify_account_ownership(account_id, user_id):
            raise ValueError("Account not found or access denied")

        # Get enhanced transactions
        enhanced_transactions = await self.repository.get_enhanced_account_transactions(
            account_id=account_id,
            limit=pagination.page_size,
            offset=pagination.offset
        )

        # Convert to response models
        transaction_responses = [
            EnhancedTransactionResponse(**transaction) for transaction in enhanced_transactions
        ]

        # Get total count
        total_count = await self.repository.count_account_transactions(account_id)

        return PaginatedResponse.create(
            items=transaction_responses,
            total_count=total_count,
            pagination=pagination
        )

    async def get_recent_transactions(
        self,
        user_id: UUID,
        pagination: PaginationParams
    ) -> PaginatedResponse[TransactionResponse]:
        """
        Get recent transactions across all user accounts, including investment transactions.

        Args:
            user_id: User ID
            pagination: Pagination parameters

        Returns:
            PaginatedResponse[TransactionResponse]: Recent transactions
        """
        # Get user's account IDs
        user_accounts = await self.repository.get_user_accounts(user_id)
        account_ids = [account['id'] for account in user_accounts]

        if not account_ids:
            # No accounts, return empty response
            return PaginatedResponse.create(
                items=[],
                total_count=0,
                pagination=pagination
            )

        # Get both regular and investment transactions
        regular_transactions = await self.repository.get_recent_transactions_for_accounts(
            account_ids=account_ids,
            limit=pagination.page_size * 2,  # Get more to ensure we have enough after merging
            offset=0
        )

        investment_transactions = await self.repository.get_user_investment_transactions(
            user_id=user_id,
            limit=pagination.page_size * 2,
            skip=0
        )

        # Convert investment transactions to regular transaction format
        converted_investment_transactions = []
        for inv_tx in investment_transactions:
            # Map investment transaction types to Chinese
            transaction_type_map = {
                'purchase': '理财申购',
                'redemption': '理财赎回'
            }
            chinese_type = transaction_type_map.get(inv_tx['transaction_type'], f"投资{inv_tx['transaction_type']}")

            converted_tx = {
                'id': inv_tx['id'],
                'account_id': inv_tx['account_id'],
                'transaction_type': chinese_type,
                'amount': inv_tx['amount'],
                'related_account_id': None,
                'description': inv_tx.get('description', chinese_type),
                'status': 'completed' if inv_tx['status'] == 'confirmed' else inv_tx['status'],
                'timestamp': inv_tx['created_at']
            }
            converted_investment_transactions.append(converted_tx)

        # Merge and sort all transactions by timestamp
        all_transactions = regular_transactions + converted_investment_transactions
        all_transactions.sort(key=lambda x: x['timestamp'], reverse=True)

        # Apply pagination
        start_idx = pagination.offset
        end_idx = start_idx + pagination.page_size
        paginated_transactions = all_transactions[start_idx:end_idx]

        # Convert to response models
        transaction_responses = [
            TransactionResponse(**transaction) for transaction in paginated_transactions
        ]

        # Calculate total count
        regular_count = await self.repository.count_transactions_for_accounts(account_ids)
        investment_count = len(investment_transactions)  # For simplicity, use current count
        total_count = regular_count + investment_count

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

    async def transfer_by_account_number(
        self,
        user_id: UUID,
        transfer_request: TransferByAccountNumberRequest
    ) -> Tuple[TransactionResponse, TransactionResponse]:
        """
        Process a transfer transaction using target account number.

        Args:
            user_id: User ID making the transfer
            transfer_request: Transfer request data with account number

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

        # Additional validation for cross-user transfers
        if transfer_request.amount > self.MAX_CROSS_USER_TRANSFER:
            raise ValueError(f"Maximum cross-user transfer limit is {self.MAX_CROSS_USER_TRANSFER}")

        # Verify ownership of source account
        if not await self.repository.verify_account_ownership(
            transfer_request.from_account_id, user_id
        ):
            raise ValueError("Source account not found or access denied")

        # Lookup target account by account number
        target_account = await self.repository.get_account_by_number(transfer_request.to_account_number)
        if not target_account:
            raise ValueError("Target account not found")

        # Validate different accounts
        if transfer_request.from_account_id == target_account['id']:
            raise ValueError("Cannot transfer to the same account")

        # Check if this is a cross-user transfer
        source_account = await self.repository.get_account_by_id(transfer_request.from_account_id)
        if not source_account:
            raise ValueError("Source account not found")

        is_cross_user_transfer = source_account['user_id'] != target_account['user_id']

        if is_cross_user_transfer:
            logger.info(f"Cross-user transfer detected: {source_account['user_id']} -> {target_account['user_id']}")
            # Additional security logging for cross-user transfers
            logger.warning(
                f"Cross-user transfer: {transfer_request.amount} from account "
                f"{transfer_request.from_account_id} to {transfer_request.to_account_number} "
                f"by user {user_id}"
            )

        # Validate source account has sufficient funds
        await self._validate_account_for_withdrawal(
            transfer_request.from_account_id, user_id, transfer_request.amount
        )

        try:
            # Execute transfer transaction
            from_transaction, to_transaction = await self.repository.execute_transfer(
                from_account_id=transfer_request.from_account_id,
                to_account_id=target_account['id'],
                amount=transfer_request.amount,
                description=transfer_request.description
            )

            logger.info(
                f"Transfer by account number successful: {transfer_request.amount} from "
                f"{transfer_request.from_account_id} to {transfer_request.to_account_number} "
                f"by user {user_id}"
            )

            # Convert to response models
            from_response = TransactionResponse(
                id=from_transaction['id'],
                account_id=from_transaction['account_id'],
                transaction_type=TransactionType(from_transaction['transaction_type']),
                amount=from_transaction['amount'],
                related_account_id=from_transaction.get('related_account_id'),
                description=from_transaction.get('description'),
                status=from_transaction['status'],
                timestamp=from_transaction['timestamp']
            )

            to_response = TransactionResponse(
                id=to_transaction['id'],
                account_id=to_transaction['account_id'],
                transaction_type=TransactionType(to_transaction['transaction_type']),
                amount=to_transaction['amount'],
                related_account_id=to_transaction.get('related_account_id'),
                description=to_transaction.get('description'),
                status=to_transaction['status'],
                timestamp=to_transaction['timestamp']
            )

            return from_response, to_response

        except Exception as e:
            logger.error(f"Transfer by account number failed for user {user_id}: {e}")
            raise RuntimeError(f"Transfer transaction failed: {str(e)}")

    # Admin-only methods

    async def get_all_transactions_for_admin(
        self,
        pagination: PaginationParams,
        account_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        user_search: Optional[str] = None
    ) -> PaginatedResponse[EnhancedTransactionResponse]:
        """
        Get all transactions in the system for admin monitoring.

        Args:
            pagination: Pagination parameters
            account_id: Optional account ID filter
            transaction_type: Optional transaction type filter
            user_search: Optional user search term

        Returns:
            PaginatedResponse[EnhancedTransactionResponse]: Paginated transaction list
        """
        transactions_data = await self.repository.get_all_transactions_for_admin(
            limit=pagination.page_size,
            offset=pagination.offset,
            account_id=account_id,
            transaction_type=transaction_type,
            user_search=user_search
        )

        transactions = [EnhancedTransactionResponse(**transaction) for transaction in transactions_data]

        # Get total count
        total_count = await self.repository.count_all_transactions_for_admin(
            account_id=account_id,
            transaction_type=transaction_type,
            user_search=user_search
        )

        return PaginatedResponse.create(
            items=transactions,
            total_count=total_count,
            pagination=pagination
        )

    async def get_transaction_statistics(self) -> dict:
        """
        Get transaction statistics for admin dashboard.

        Returns:
            dict: Transaction statistics
        """
        return await self.repository.get_transaction_statistics()
