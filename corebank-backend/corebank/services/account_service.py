"""
Account service for CoreBank.

This module provides business logic for account management operations.
It coordinates between the API layer and the repository layer, implementing
business rules and ensuring data consistency.
"""

import logging
from decimal import Decimal
from typing import Optional
from uuid import UUID

from corebank.models.account import AccountType, AccountCreate, AccountResponse, AccountSummary, AccountLookupResponse
from corebank.repositories.postgres_repo import PostgresRepository

logger = logging.getLogger(__name__)


class AccountService:
    """
    Service class for account management operations.
    
    This class implements business logic for account operations including
    creation, retrieval, and validation of business rules.
    """
    
    def __init__(self, repository: PostgresRepository) -> None:
        """
        Initialize the account service.
        
        Args:
            repository: PostgreSQL repository instance
        """
        self.repository = repository
    
    async def create_account(
        self, 
        user_id: UUID, 
        account_data: AccountCreate
    ) -> AccountResponse:
        """
        Create a new account for a user.
        
        Args:
            user_id: User ID who will own the account
            account_data: Account creation data
            
        Returns:
            AccountResponse: Created account data
            
        Raises:
            ValueError: If user doesn't exist or validation fails
            RuntimeError: If account creation fails
        """
        # Validate user exists
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Validate initial deposit
        initial_deposit = account_data.initial_deposit or Decimal("0.00")
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative")
        
        # Business rule: Check account limits per user
        user_accounts = await self.repository.get_user_accounts(user_id)
        
        # Limit: Maximum 5 accounts per user
        if len(user_accounts) >= 5:
            raise ValueError("Maximum number of accounts (5) reached for this user")
        
        # Limit: Only one savings account per user
        if account_data.account_type == AccountType.SAVINGS:
            savings_accounts = [
                acc for acc in user_accounts 
                if acc['account_type'] == AccountType.SAVINGS.value
            ]
            if savings_accounts:
                raise ValueError("User already has a savings account")
        
        try:
            # Create the account
            account = await self.repository.create_account(
                user_id=user_id,
                account_type=account_data.account_type,
                initial_balance=initial_deposit
            )
            
            logger.info(f"Account created successfully: {account['account_number']}")
            
            return AccountResponse(**account)
            
        except Exception as e:
            logger.error(f"Failed to create account for user {user_id}: {e}")
            raise RuntimeError(f"Account creation failed: {str(e)}")
    
    async def get_account(self, account_id: UUID, user_id: UUID) -> AccountResponse:
        """
        Get account details for a specific user.
        
        Args:
            account_id: Account ID to retrieve
            user_id: User ID for ownership verification
            
        Returns:
            AccountResponse: Account data
            
        Raises:
            ValueError: If account not found or doesn't belong to user
        """
        # Verify account ownership
        if not await self.repository.verify_account_ownership(account_id, user_id):
            raise ValueError("Account not found or access denied")
        
        account = await self.repository.get_account_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        
        return AccountResponse(**account)
    
    async def get_user_accounts(self, user_id: UUID) -> list[AccountResponse]:
        """
        Get all accounts for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            list[AccountResponse]: List of user's accounts
            
        Raises:
            ValueError: If user doesn't exist
        """
        # Validate user exists
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        accounts = await self.repository.get_user_accounts(user_id)
        return [AccountResponse(**account) for account in accounts]
    
    async def get_account_summary(self, user_id: UUID) -> AccountSummary:
        """
        Get account summary for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            AccountSummary: Account summary data
            
        Raises:
            ValueError: If user doesn't exist
        """
        # Validate user exists
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        summary_data = await self.repository.get_account_summary(user_id)
        
        # Convert to the expected format
        accounts_by_type = {
            AccountType.CHECKING: summary_data.get('checking_accounts', 0),
            AccountType.SAVINGS: summary_data.get('savings_accounts', 0)
        }
        
        return AccountSummary(
            total_accounts=summary_data.get('total_accounts', 0),
            total_balance=summary_data.get('total_balance', Decimal('0.00')),
            accounts_by_type=accounts_by_type
        )
    
    async def validate_account_access(self, account_id: UUID, user_id: UUID) -> bool:
        """
        Validate that a user has access to an account.
        
        Args:
            account_id: Account ID
            user_id: User ID
            
        Returns:
            bool: True if user has access, False otherwise
        """
        return await self.repository.verify_account_ownership(account_id, user_id)
    
    async def get_account_balance(self, account_id: UUID, user_id: UUID) -> Decimal:
        """
        Get current account balance.
        
        Args:
            account_id: Account ID
            user_id: User ID for ownership verification
            
        Returns:
            Decimal: Current account balance
            
        Raises:
            ValueError: If account not found or access denied
        """
        # Verify account ownership
        if not await self.repository.verify_account_ownership(account_id, user_id):
            raise ValueError("Account not found or access denied")
        
        account = await self.repository.get_account_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        
        return account['balance']
    
    async def validate_account_for_transaction(
        self, 
        account_id: UUID, 
        user_id: UUID,
        required_balance: Optional[Decimal] = None
    ) -> dict:
        """
        Validate account for transaction operations.
        
        Args:
            account_id: Account ID
            user_id: User ID for ownership verification
            required_balance: Minimum required balance (for withdrawals/transfers)
            
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
        
        # Check required balance if specified
        if required_balance is not None and account['balance'] < required_balance:
            raise ValueError("Insufficient funds")
        
        return account

    async def lookup_account_by_number(self, account_number: str) -> AccountLookupResponse:
        """
        Lookup account by account number for transfer purposes.

        Args:
            account_number: Account number to lookup

        Returns:
            AccountLookupResponse: Basic account information

        Raises:
            ValueError: If account not found
        """
        # Get account by account number
        account = await self.repository.get_account_by_number(account_number)
        if not account:
            raise ValueError("Account not found")

        # Get owner information (optional, for display purposes)
        owner_name = None
        try:
            user_profile = await self.repository.get_user_profile(account['user_id'])
            if user_profile:
                owner_name = user_profile.get('real_name')
        except Exception:
            # If we can't get owner name, it's not critical
            pass

        return AccountLookupResponse(
            account_id=account['id'],
            account_number=account['account_number'],
            account_type=AccountType(account['account_type']),
            owner_name=owner_name
        )

    async def get_all_accounts(self) -> list[AccountResponse]:
        """
        Get all accounts in the system (admin only).

        Returns:
            list[AccountResponse]: List of all accounts
        """
        accounts = await self.repository.get_all_accounts()
        return [AccountResponse(**account) for account in accounts]
