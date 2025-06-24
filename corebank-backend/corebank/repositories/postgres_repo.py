"""
PostgreSQL repository implementation for CoreBank.

This module provides the data access layer for all CoreBank entities.
It implements CRUD operations and complex queries using psycopg3 with
proper transaction management and error handling.
"""

import logging
import secrets
import string
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from corebank.core.db import DatabaseManager
from corebank.models.account import AccountType
from corebank.models.transaction import TransactionType, TransactionStatus

logger = logging.getLogger(__name__)


class PostgresRepository:
    """
    PostgreSQL repository for CoreBank data access.
    
    This class provides all database operations for users, accounts, and transactions.
    It uses the database manager for connection pooling and transaction management.
    """
    
    def __init__(self, db_manager: DatabaseManager) -> None:
        """
        Initialize the repository with a database manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
    
    # User operations
    
    async def create_user(self, username: str, hashed_password: str) -> dict:
        """
        Create a new user.
        
        Args:
            username: User's username
            hashed_password: Hashed password
            
        Returns:
            dict: Created user data
            
        Raises:
            psycopg.IntegrityError: If username already exists
        """
        query = """
            INSERT INTO users (username, hashed_password)
            VALUES (%s, %s)
            RETURNING id, username, created_at
        """
        
        async with self.db_manager.get_connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, (username, hashed_password))
                result = await cur.fetchone()
                
                if not result:
                    raise RuntimeError("Failed to create user")
                
                logger.info(f"Created user: {username} (ID: {result['id']})")
                return result
    
    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            Optional[dict]: User data if found, None otherwise
        """
        query = """
            SELECT id, username, hashed_password, created_at
            FROM users
            WHERE username = %s
        """
        
        async with self.db_manager.get_connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, (username,))
                return await cur.fetchone()
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[dict]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            Optional[dict]: User data if found, None otherwise
        """
        query = """
            SELECT id, username, created_at
            FROM users
            WHERE id = %s
        """
        
        async with self.db_manager.get_connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, (user_id,))
                return await cur.fetchone()
    
    async def update_user_password(self, user_id: UUID, hashed_password: str) -> bool:
        """
        Update user password.
        
        Args:
            user_id: User ID
            hashed_password: New hashed password
            
        Returns:
            bool: True if password was updated, False otherwise
        """
        query = """
            UPDATE users
            SET hashed_password = %s
            WHERE id = %s
        """
        
        async with self.db_manager.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (hashed_password, user_id))
                return cur.rowcount > 0
    
    # Account operations
    
    def _generate_account_number(self) -> str:
        """
        Generate a unique account number.
        
        Returns:
            str: Generated account number
        """
        # Generate a 12-digit account number
        digits = ''.join(secrets.choice(string.digits) for _ in range(12))
        return f"ACC{digits}"
    
    async def create_account(
        self, 
        user_id: UUID, 
        account_type: AccountType, 
        initial_balance: Decimal = Decimal("0.00")
    ) -> dict:
        """
        Create a new account.
        
        Args:
            user_id: Owner user ID
            account_type: Type of account
            initial_balance: Initial account balance
            
        Returns:
            dict: Created account data
        """
        # Generate unique account number
        account_number = self._generate_account_number()
        
        # Ensure account number is unique
        while await self._account_number_exists(account_number):
            account_number = self._generate_account_number()
        
        query = """
            INSERT INTO accounts (account_number, user_id, account_type, balance)
            VALUES (%s, %s, %s, %s)
            RETURNING id, account_number, user_id, account_type, balance, created_at
        """
        
        async with self.db_manager.get_connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    query, 
                    (account_number, user_id, account_type.value, initial_balance)
                )
                result = await cur.fetchone()
                
                if not result:
                    raise RuntimeError("Failed to create account")
                
                logger.info(f"Created account: {account_number} for user {user_id}")
                return result
    
    async def _account_number_exists(self, account_number: str) -> bool:
        """Check if account number already exists."""
        query = "SELECT 1 FROM accounts WHERE account_number = %s"

        async with self.db_manager.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (account_number,))
                return await cur.fetchone() is not None

    async def get_account_by_id(self, account_id: UUID) -> Optional[dict]:
        """
        Get account by ID.

        Args:
            account_id: Account ID to search for

        Returns:
            Optional[dict]: Account data if found, None otherwise
        """
        query = """
            SELECT id, account_number, user_id, account_type, balance, created_at
            FROM accounts
            WHERE id = %s
        """

        async with self.db_manager.get_connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, (account_id,))
                return await cur.fetchone()

    async def get_account_by_number(self, account_number: str) -> Optional[dict]:
        """
        Get account by account number.

        Args:
            account_number: Account number to search for

        Returns:
            Optional[dict]: Account data if found, None otherwise
        """
        query = """
            SELECT id, account_number, user_id, account_type, balance, created_at
            FROM accounts
            WHERE account_number = %s
        """

        async with self.db_manager.get_connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, (account_number,))
                return await cur.fetchone()

    async def get_user_accounts(self, user_id: UUID) -> list[dict]:
        """
        Get all accounts for a user.

        Args:
            user_id: User ID

        Returns:
            list[dict]: List of user's accounts
        """
        query = """
            SELECT id, account_number, user_id, account_type, balance, created_at
            FROM accounts
            WHERE user_id = %s
            ORDER BY created_at DESC
        """

        async with self.db_manager.get_connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, (user_id,))
                return await cur.fetchall()

    async def update_account_balance(
        self,
        account_id: UUID,
        new_balance: Decimal,
        conn: Optional[psycopg.AsyncConnection] = None
    ) -> bool:
        """
        Update account balance.

        Args:
            account_id: Account ID
            new_balance: New balance amount
            conn: Optional database connection for transaction

        Returns:
            bool: True if balance was updated, False otherwise
        """
        query = """
            UPDATE accounts
            SET balance = %s
            WHERE id = %s AND balance >= 0
        """

        if conn:
            # Use provided connection (for transactions)
            async with conn.cursor() as cur:
                await cur.execute(query, (new_balance, account_id))
                return cur.rowcount > 0
        else:
            # Use new connection
            async with self.db_manager.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, (new_balance, account_id))
                    return cur.rowcount > 0

    # Transaction operations

    async def create_transaction(
        self,
        account_id: UUID,
        transaction_type: TransactionType,
        amount: Decimal,
        related_account_id: Optional[UUID] = None,
        description: Optional[str] = None,
        status: TransactionStatus = TransactionStatus.COMPLETED,
        conn: Optional[psycopg.AsyncConnection] = None
    ) -> dict:
        """
        Create a new transaction.

        Args:
            account_id: Primary account ID
            transaction_type: Type of transaction
            amount: Transaction amount
            related_account_id: Related account ID (for transfers)
            description: Transaction description
            status: Transaction status
            conn: Optional database connection for transaction

        Returns:
            dict: Created transaction data
        """
        query = """
            INSERT INTO transactions (
                account_id, transaction_type, amount, related_account_id,
                description, status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, account_id, transaction_type, amount, related_account_id,
                     description, status, timestamp
        """

        params = (
            account_id,
            transaction_type.value,
            amount,
            related_account_id,
            description,
            status.value
        )

        if conn:
            # Use provided connection (for transactions)
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, params)
                result = await cur.fetchone()
        else:
            # Use new connection
            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, params)
                    result = await cur.fetchone()

        if not result:
            raise RuntimeError("Failed to create transaction")

        logger.info(f"Created transaction: {result['id']} ({transaction_type.value})")
        return result

    async def get_transaction_by_id(self, transaction_id: UUID) -> Optional[dict]:
        """
        Get transaction by ID.

        Args:
            transaction_id: Transaction ID to search for

        Returns:
            Optional[dict]: Transaction data if found, None otherwise
        """
        query = """
            SELECT id, account_id, transaction_type, amount, related_account_id,
                   description, status, timestamp
            FROM transactions
            WHERE id = %s
        """

        async with self.db_manager.get_connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, (transaction_id,))
                return await cur.fetchone()

    async def get_account_transactions(
        self,
        account_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> list[dict]:
        """
        Get transactions for an account with pagination.

        Args:
            account_id: Account ID
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip

        Returns:
            list[dict]: List of transactions
        """
        query = """
            SELECT id, account_id, transaction_type, amount, related_account_id,
                   description, status, timestamp
            FROM transactions
            WHERE account_id = %s OR related_account_id = %s
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
        """

        async with self.db_manager.get_connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, (account_id, account_id, limit, offset))
                return await cur.fetchall()

    async def count_account_transactions(self, account_id: UUID) -> int:
        """
        Count total transactions for an account.

        Args:
            account_id: Account ID

        Returns:
            int: Total number of transactions
        """
        query = """
            SELECT COUNT(*)
            FROM transactions
            WHERE account_id = %s OR related_account_id = %s
        """

        async with self.db_manager.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (account_id, account_id))
                result = await cur.fetchone()
                return result[0] if result else 0

    # Complex transaction operations

    async def execute_deposit(
        self,
        account_id: UUID,
        amount: Decimal,
        description: Optional[str] = None
    ) -> dict:
        """
        Execute a deposit transaction atomically.

        Args:
            account_id: Target account ID
            amount: Deposit amount
            description: Transaction description

        Returns:
            dict: Transaction data

        Raises:
            RuntimeError: If account not found or transaction fails
        """
        async with self.db_manager.get_connection() as conn:
            async with conn.transaction():
                # Get current account balance
                account = await self._get_account_for_update(account_id, conn)
                if not account:
                    raise RuntimeError(f"Account {account_id} not found")

                # Calculate new balance
                new_balance = account['balance'] + amount

                # Update account balance
                success = await self.update_account_balance(account_id, new_balance, conn)
                if not success:
                    raise RuntimeError("Failed to update account balance")

                # Create transaction record
                transaction = await self.create_transaction(
                    account_id=account_id,
                    transaction_type=TransactionType.DEPOSIT,
                    amount=amount,
                    description=description,
                    conn=conn
                )

                logger.info(f"Deposit completed: {amount} to account {account_id}")
                return transaction

    async def execute_withdrawal(
        self,
        account_id: UUID,
        amount: Decimal,
        description: Optional[str] = None
    ) -> dict:
        """
        Execute a withdrawal transaction atomically.

        Args:
            account_id: Source account ID
            amount: Withdrawal amount
            description: Transaction description

        Returns:
            dict: Transaction data

        Raises:
            RuntimeError: If account not found, insufficient funds, or transaction fails
        """
        async with self.db_manager.get_connection() as conn:
            async with conn.transaction():
                # Get current account balance with row lock
                account = await self._get_account_for_update(account_id, conn)
                if not account:
                    raise RuntimeError(f"Account {account_id} not found")

                # Check sufficient funds
                if account['balance'] < amount:
                    raise RuntimeError("Insufficient funds")

                # Calculate new balance
                new_balance = account['balance'] - amount

                # Update account balance
                success = await self.update_account_balance(account_id, new_balance, conn)
                if not success:
                    raise RuntimeError("Failed to update account balance")

                # Create transaction record
                transaction = await self.create_transaction(
                    account_id=account_id,
                    transaction_type=TransactionType.WITHDRAWAL,
                    amount=amount,
                    description=description,
                    conn=conn
                )

                logger.info(f"Withdrawal completed: {amount} from account {account_id}")
                return transaction

    async def execute_transfer(
        self,
        from_account_id: UUID,
        to_account_id: UUID,
        amount: Decimal,
        description: Optional[str] = None
    ) -> tuple[dict, dict]:
        """
        Execute a transfer transaction atomically.

        Args:
            from_account_id: Source account ID
            to_account_id: Target account ID
            amount: Transfer amount
            description: Transaction description

        Returns:
            tuple[dict, dict]: Source and target transaction records

        Raises:
            RuntimeError: If accounts not found, insufficient funds, or transaction fails
        """
        if from_account_id == to_account_id:
            raise RuntimeError("Cannot transfer to the same account")

        async with self.db_manager.get_connection() as conn:
            async with conn.transaction():
                # Get both accounts with row locks (ordered by ID to prevent deadlock)
                account_ids = sorted([from_account_id, to_account_id])
                accounts = {}

                for account_id in account_ids:
                    account = await self._get_account_for_update(account_id, conn)
                    if not account:
                        raise RuntimeError(f"Account {account_id} not found")
                    accounts[account_id] = account

                from_account = accounts[from_account_id]
                to_account = accounts[to_account_id]

                # Check sufficient funds
                if from_account['balance'] < amount:
                    raise RuntimeError("Insufficient funds")

                # Calculate new balances
                from_new_balance = from_account['balance'] - amount
                to_new_balance = to_account['balance'] + amount

                # Update both account balances
                from_success = await self.update_account_balance(
                    from_account_id, from_new_balance, conn
                )
                to_success = await self.update_account_balance(
                    to_account_id, to_new_balance, conn
                )

                if not (from_success and to_success):
                    raise RuntimeError("Failed to update account balances")

                # Create transaction records for both accounts
                from_transaction = await self.create_transaction(
                    account_id=from_account_id,
                    transaction_type=TransactionType.TRANSFER,
                    amount=amount,
                    related_account_id=to_account_id,
                    description=description,
                    conn=conn
                )

                to_transaction = await self.create_transaction(
                    account_id=to_account_id,
                    transaction_type=TransactionType.TRANSFER,
                    amount=amount,
                    related_account_id=from_account_id,
                    description=description,
                    conn=conn
                )

                logger.info(
                    f"Transfer completed: {amount} from {from_account_id} to {to_account_id}"
                )
                return from_transaction, to_transaction

    async def _get_account_for_update(
        self,
        account_id: UUID,
        conn: psycopg.AsyncConnection
    ) -> Optional[dict]:
        """
        Get account with row lock for update.

        Args:
            account_id: Account ID
            conn: Database connection

        Returns:
            Optional[dict]: Account data if found, None otherwise
        """
        query = """
            SELECT id, account_number, user_id, account_type, balance, created_at
            FROM accounts
            WHERE id = %s
            FOR UPDATE
        """

        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, (account_id,))
            return await cur.fetchone()

    # Utility methods

    async def verify_account_ownership(self, account_id: UUID, user_id: UUID) -> bool:
        """
        Verify that an account belongs to a specific user.

        Args:
            account_id: Account ID
            user_id: User ID

        Returns:
            bool: True if account belongs to user, False otherwise
        """
        query = "SELECT 1 FROM accounts WHERE id = %s AND user_id = %s"

        async with self.db_manager.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (account_id, user_id))
                return await cur.fetchone() is not None

    async def get_account_summary(self, user_id: UUID) -> dict:
        """
        Get account summary for a user.

        Args:
            user_id: User ID

        Returns:
            dict: Account summary data
        """
        query = """
            SELECT
                COUNT(*) as total_accounts,
                COALESCE(SUM(balance), 0) as total_balance,
                COUNT(CASE WHEN account_type = 'checking' THEN 1 END) as checking_accounts,
                COUNT(CASE WHEN account_type = 'savings' THEN 1 END) as savings_accounts
            FROM accounts
            WHERE user_id = %s
        """

        async with self.db_manager.get_connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, (user_id,))
                result = await cur.fetchone()

                if not result:
                    return {
                        'total_accounts': 0,
                        'total_balance': Decimal('0.00'),
                        'checking_accounts': 0,
                        'savings_accounts': 0
                    }

                return result

    async def get_transaction_summary(self, account_id: UUID) -> dict:
        """
        Get transaction summary for an account.

        Args:
            account_id: Account ID

        Returns:
            dict: Transaction summary data
        """
        query = """
            SELECT
                COUNT(*) as total_transactions,
                COUNT(CASE WHEN transaction_type = 'deposit' THEN 1 END) as deposits,
                COUNT(CASE WHEN transaction_type = 'withdrawal' THEN 1 END) as withdrawals,
                COUNT(CASE WHEN transaction_type = 'transfer' THEN 1 END) as transfers,
                COALESCE(SUM(CASE WHEN transaction_type = 'deposit' THEN amount ELSE 0 END), 0) as total_deposits,
                COALESCE(SUM(CASE WHEN transaction_type = 'withdrawal' THEN amount ELSE 0 END), 0) as total_withdrawals,
                COALESCE(SUM(CASE WHEN transaction_type = 'transfer' AND account_id = %s THEN amount ELSE 0 END), 0) as total_transfers_out,
                COALESCE(SUM(CASE WHEN transaction_type = 'transfer' AND related_account_id = %s THEN amount ELSE 0 END), 0) as total_transfers_in
            FROM transactions
            WHERE account_id = %s OR related_account_id = %s
        """

        async with self.db_manager.get_connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, (account_id, account_id, account_id, account_id))
                result = await cur.fetchone()

                if not result:
                    return {
                        'total_transactions': 0,
                        'deposits': 0,
                        'withdrawals': 0,
                        'transfers': 0,
                        'total_deposits': Decimal('0.00'),
                        'total_withdrawals': Decimal('0.00'),
                        'total_transfers_out': Decimal('0.00'),
                        'total_transfers_in': Decimal('0.00')
                    }

                return result

    async def health_check(self) -> dict:
        """
        Perform a health check on the database.

        Returns:
            dict: Health check results
        """
        try:
            start_time = datetime.utcnow()

            # Test basic connectivity
            async with self.db_manager.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    result = await cur.fetchone()

                    if not result or result[0] != 1:
                        raise RuntimeError("Database connectivity test failed")

            # Test table existence
            async with self.db_manager.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                        SELECT COUNT(*) FROM information_schema.tables
                        WHERE table_name IN ('users', 'accounts', 'transactions')
                    """)
                    table_count = await cur.fetchone()

                    if not table_count or table_count[0] != 3:
                        raise RuntimeError("Required tables not found")

            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000

            return {
                'status': 'healthy',
                'response_time_ms': response_time,
                'timestamp': end_time.isoformat()
            }

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
