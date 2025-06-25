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

    async def get_recent_transactions_for_accounts(
        self,
        account_ids: list[UUID],
        limit: int = 5,
        offset: int = 0
    ) -> list[dict]:
        """
        Get recent transactions across multiple accounts.

        Args:
            account_ids: List of account IDs
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip

        Returns:
            list[dict]: List of recent transactions
        """
        if not account_ids:
            return []

        # Create placeholders for account IDs
        placeholders = ','.join(['%s'] * len(account_ids))

        query = f"""
            SELECT id, account_id, transaction_type, amount, related_account_id,
                   description, status, timestamp
            FROM transactions
            WHERE account_id IN ({placeholders}) OR related_account_id IN ({placeholders})
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
        """

        # Duplicate account_ids for both WHERE conditions
        params = account_ids + account_ids + [limit, offset]

        async with self.db_manager.get_connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, params)
                return await cur.fetchall()

    async def count_transactions_for_accounts(self, account_ids: list[UUID]) -> int:
        """
        Count total transactions across multiple accounts.

        Args:
            account_ids: List of account IDs

        Returns:
            int: Total number of transactions
        """
        if not account_ids:
            return 0

        # Create placeholders for account IDs
        placeholders = ','.join(['%s'] * len(account_ids))

        query = f"""
            SELECT COUNT(*)
            FROM transactions
            WHERE account_id IN ({placeholders}) OR related_account_id IN ({placeholders})
        """

        # Duplicate account_ids for both WHERE conditions
        params = account_ids + account_ids

        async with self.db_manager.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
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

    # Investment Product operations

    async def get_investment_products(self, filters: dict = None, skip: int = 0, limit: int = 100) -> list[dict]:
        """
        Get investment products with optional filtering.

        Args:
            filters: Optional filters (product_type, risk_level, is_active)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of investment product dictionaries
        """
        try:
            query = """
                SELECT id, product_code, name, product_type, risk_level,
                       expected_return_rate, min_investment_amount, max_investment_amount,
                       investment_period_days, is_active, description, features,
                       created_at, updated_at
                FROM investment_products
                WHERE 1=1
            """
            params = []

            if filters:
                if 'product_type' in filters:
                    query += " AND product_type = %s"
                    params.append(filters['product_type'])
                if 'risk_level' in filters:
                    query += " AND risk_level = %s"
                    params.append(filters['risk_level'])
                if 'is_active' in filters:
                    query += " AND is_active = %s"
                    params.append(filters['is_active'])

            query += " ORDER BY created_at DESC OFFSET %s LIMIT %s"
            params.extend([skip, limit])

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, params)
                    return await cur.fetchall()

        except Exception as e:
            logger.error(f"Failed to get investment products: {e}")
            raise

    async def get_investment_product(self, product_id: UUID) -> Optional[dict]:
        """
        Get a specific investment product by ID.

        Args:
            product_id: Product unique identifier

        Returns:
            Investment product dictionary or None if not found
        """
        try:
            query = """
                SELECT id, product_code, name, product_type, risk_level,
                       expected_return_rate, min_investment_amount, max_investment_amount,
                       investment_period_days, is_active, description, features,
                       created_at, updated_at
                FROM investment_products
                WHERE id = %s
            """

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, (product_id,))
                    return await cur.fetchone()

        except Exception as e:
            logger.error(f"Failed to get investment product {product_id}: {e}")
            raise

    async def get_investment_product_by_code(self, product_code: str) -> Optional[dict]:
        """
        Get an investment product by product code.

        Args:
            product_code: Product code

        Returns:
            Investment product dictionary or None if not found
        """
        try:
            query = """
                SELECT id, product_code, name, product_type, risk_level,
                       expected_return_rate, min_investment_amount, max_investment_amount,
                       investment_period_days, is_active, description, features,
                       created_at, updated_at
                FROM investment_products
                WHERE product_code = %s
            """

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, (product_code,))
                    return await cur.fetchone()

        except Exception as e:
            logger.error(f"Failed to get investment product by code {product_code}: {e}")
            raise

    async def create_investment_product(self, product_data: dict) -> dict:
        """
        Create a new investment product.

        Args:
            product_data: Product data dictionary

        Returns:
            Created investment product dictionary
        """
        try:
            import json

            query = """
                INSERT INTO investment_products (
                    product_code, name, product_type, risk_level, expected_return_rate,
                    min_investment_amount, max_investment_amount, investment_period_days,
                    is_active, description, features
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id, product_code, name, product_type, risk_level,
                          expected_return_rate, min_investment_amount, max_investment_amount,
                          investment_period_days, is_active, description, features,
                          created_at, updated_at
            """

            # Set defaults and prepare parameters
            product_data.setdefault('is_active', True)

            # Convert features dict to JSON string
            features_json = json.dumps(product_data.get('features')) if product_data.get('features') else None

            params = (
                product_data['product_code'],
                product_data['name'],
                product_data['product_type'],
                product_data['risk_level'],
                product_data.get('expected_return_rate'),
                product_data['min_investment_amount'],
                product_data.get('max_investment_amount'),
                product_data.get('investment_period_days'),
                product_data['is_active'],
                product_data.get('description'),
                features_json
            )

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, params)
                    result = await cur.fetchone()
                    await conn.commit()
                    return result

        except Exception as e:
            logger.error(f"Failed to create investment product: {e}")
            raise

    # Risk Assessment operations

    async def create_risk_assessment(self, assessment_data: dict) -> dict:
        """
        Create a new risk assessment for a user.

        Args:
            assessment_data: Risk assessment data dictionary

        Returns:
            Created risk assessment dictionary
        """
        try:
            import json

            query = """
                INSERT INTO user_risk_assessments (
                    user_id, risk_tolerance, investment_experience, investment_goal,
                    investment_horizon, monthly_income_range, assessment_score,
                    assessment_data, expires_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id, user_id, risk_tolerance, investment_experience, investment_goal,
                          investment_horizon, monthly_income_range, assessment_score,
                          assessment_data, expires_at, created_at
            """

            # Convert assessment_data dict to JSON string
            assessment_json = json.dumps(assessment_data.get('assessment_data')) if assessment_data.get('assessment_data') else None

            params = (
                assessment_data['user_id'],
                assessment_data['risk_tolerance'],
                assessment_data['investment_experience'],
                assessment_data['investment_goal'],
                assessment_data['investment_horizon'],
                assessment_data.get('monthly_income_range'),
                assessment_data['assessment_score'],
                assessment_json,
                assessment_data['expires_at']
            )

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, params)
                    result = await cur.fetchone()
                    await conn.commit()
                    return result

        except Exception as e:
            logger.error(f"Failed to create risk assessment: {e}")
            raise

    async def get_current_risk_assessment(self, user_id: UUID) -> Optional[dict]:
        """
        Get the current valid risk assessment for a user.

        Args:
            user_id: User unique identifier

        Returns:
            Risk assessment dictionary or None if not found/expired
        """
        try:
            query = """
                SELECT id, user_id, risk_tolerance, investment_experience, investment_goal,
                       investment_horizon, monthly_income_range, assessment_score,
                       assessment_data, expires_at, created_at
                FROM user_risk_assessments
                WHERE user_id = %s AND expires_at > CURRENT_TIMESTAMP
                ORDER BY created_at DESC
                LIMIT 1
            """

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, (user_id,))
                    return await cur.fetchone()

        except Exception as e:
            logger.error(f"Failed to get current risk assessment for user {user_id}: {e}")
            raise

    # Investment Holding operations

    async def get_user_investment_holdings(self, user_id: UUID) -> list[dict]:
        """
        Get all investment holdings for a user.

        Args:
            user_id: User unique identifier

        Returns:
            List of investment holding dictionaries with product info
        """
        try:
            query = """
                SELECT h.id, h.user_id, h.account_id, h.product_id, h.shares,
                       h.average_cost, h.total_invested, h.current_value,
                       h.unrealized_gain_loss, h.realized_gain_loss,
                       h.purchase_date, h.maturity_date, h.status,
                       h.created_at, h.updated_at,
                       p.name as product_name, p.product_type, p.product_code
                FROM investment_holdings h
                JOIN investment_products p ON h.product_id = p.id
                WHERE h.user_id = %s
                ORDER BY h.created_at DESC
            """

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, (user_id,))
                    return await cur.fetchall()

        except Exception as e:
            logger.error(f"Failed to get investment holdings for user {user_id}: {e}")
            raise

    async def get_investment_holding(self, holding_id: UUID) -> Optional[dict]:
        """
        Get a specific investment holding by ID.

        Args:
            holding_id: Holding unique identifier

        Returns:
            Investment holding dictionary or None if not found
        """
        try:
            query = """
                SELECT h.id, h.user_id, h.account_id, h.product_id, h.shares,
                       h.average_cost, h.total_invested, h.current_value,
                       h.unrealized_gain_loss, h.realized_gain_loss,
                       h.purchase_date, h.maturity_date, h.status,
                       h.created_at, h.updated_at,
                       p.name as product_name, p.product_type, p.product_code
                FROM investment_holdings h
                JOIN investment_products p ON h.product_id = p.id
                WHERE h.id = %s
            """

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, (holding_id,))
                    return await cur.fetchone()

        except Exception as e:
            logger.error(f"Failed to get investment holding {holding_id}: {e}")
            raise

    async def get_user_product_holding(self, user_id: UUID, product_id: UUID) -> Optional[dict]:
        """
        Get user's active holding for a specific product.

        Args:
            user_id: User unique identifier
            product_id: Product unique identifier

        Returns:
            Investment holding dictionary or None if not found
        """
        try:
            query = """
                SELECT h.id, h.user_id, h.account_id, h.product_id, h.shares,
                       h.average_cost, h.total_invested, h.current_value,
                       h.unrealized_gain_loss, h.realized_gain_loss,
                       h.purchase_date, h.maturity_date, h.status,
                       h.created_at, h.updated_at,
                       p.name as product_name, p.product_type, p.product_code
                FROM investment_holdings h
                JOIN investment_products p ON h.product_id = p.id
                WHERE h.user_id = %s AND h.product_id = %s AND h.status = 'active'
                ORDER BY h.created_at DESC
                LIMIT 1
            """

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, (user_id, product_id))
                    return await cur.fetchone()

        except Exception as e:
            logger.error(f"Failed to get user product holding: {e}")
            raise

    async def create_investment_holding(self, holding_data: dict) -> dict:
        """
        Create a new investment holding.

        Args:
            holding_data: Holding data dictionary

        Returns:
            Created investment holding dictionary
        """
        try:
            query = """
                INSERT INTO investment_holdings (
                    user_id, account_id, product_id, shares, average_cost,
                    total_invested, current_value, purchase_date, maturity_date, status
                ) VALUES (
                    %(user_id)s, %(account_id)s, %(product_id)s, %(shares)s, %(average_cost)s,
                    %(total_invested)s, %(current_value)s, %(purchase_date)s, %(maturity_date)s, %(status)s
                )
                RETURNING id, user_id, account_id, product_id, shares, average_cost,
                          total_invested, current_value, unrealized_gain_loss, realized_gain_loss,
                          purchase_date, maturity_date, status, created_at, updated_at
            """

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, holding_data)
                    result = await cur.fetchone()
                    await conn.commit()
                    return result

        except Exception as e:
            logger.error(f"Failed to create investment holding: {e}")
            raise

    async def update_investment_holding(self, holding_id: UUID, update_data: dict) -> dict:
        """
        Update an investment holding.

        Args:
            holding_id: Holding unique identifier
            update_data: Data to update

        Returns:
            Updated investment holding dictionary
        """
        try:
            # Build dynamic update query
            set_clauses = []
            params = []

            for field, value in update_data.items():
                if field in ['shares', 'average_cost', 'total_invested', 'current_value',
                           'unrealized_gain_loss', 'realized_gain_loss', 'status', 'updated_at']:
                    set_clauses.append(f"{field} = %s")
                    params.append(value)

            if not set_clauses:
                raise ValueError("No valid fields to update")

            params.append(holding_id)

            query = f"""
                UPDATE investment_holdings
                SET {', '.join(set_clauses)}
                WHERE id = %s
                RETURNING id, user_id, account_id, product_id, shares, average_cost,
                          total_invested, current_value, unrealized_gain_loss, realized_gain_loss,
                          purchase_date, maturity_date, status, created_at, updated_at
            """

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, params)
                    result = await cur.fetchone()
                    await conn.commit()
                    return result

        except Exception as e:
            logger.error(f"Failed to update investment holding {holding_id}: {e}")
            raise

    async def update_investment_holding_shares(self, holding_id: UUID, new_shares: Decimal) -> None:
        """
        Update the shares of an investment holding.

        Args:
            holding_id: Holding unique identifier
            new_shares: New shares amount
        """
        try:
            query = """
                UPDATE investment_holdings
                SET shares = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, (new_shares, holding_id))
                    await conn.commit()

        except Exception as e:
            logger.error(f"Failed to update holding shares {holding_id}: {e}")
            raise

    async def update_investment_holding_status(self, holding_id: UUID, status: str) -> None:
        """
        Update the status of an investment holding.

        Args:
            holding_id: Holding unique identifier
            status: New status
        """
        try:
            query = """
                UPDATE investment_holdings
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, (status, holding_id))
                    await conn.commit()

        except Exception as e:
            logger.error(f"Failed to update holding status {holding_id}: {e}")
            raise

    # Investment Transaction operations

    async def create_investment_transaction(self, transaction_data: dict) -> dict:
        """
        Create a new investment transaction.

        Args:
            transaction_data: Transaction data dictionary

        Returns:
            Created investment transaction dictionary
        """
        try:
            query = """
                INSERT INTO investment_transactions (
                    user_id, account_id, product_id, holding_id, transaction_type,
                    shares, unit_price, amount, fee, net_amount, status,
                    settlement_date, description
                ) VALUES (
                    %(user_id)s, %(account_id)s, %(product_id)s, %(holding_id)s, %(transaction_type)s,
                    %(shares)s, %(unit_price)s, %(amount)s, %(fee)s, %(net_amount)s, %(status)s,
                    %(settlement_date)s, %(description)s
                )
                RETURNING id, user_id, account_id, product_id, holding_id, transaction_type,
                          shares, unit_price, amount, fee, net_amount, status,
                          settlement_date, description, created_at, updated_at
            """

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, transaction_data)
                    result = await cur.fetchone()
                    await conn.commit()
                    return result

        except Exception as e:
            logger.error(f"Failed to create investment transaction: {e}")
            raise

    async def get_user_investment_transactions(
        self,
        user_id: UUID,
        product_id: Optional[UUID] = None,
        transaction_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[dict]:
        """
        Get investment transactions for a user with optional filtering.

        Args:
            user_id: User unique identifier
            product_id: Optional product ID filter
            transaction_type: Optional transaction type filter
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of investment transaction dictionaries with product info
        """
        try:
            query = """
                SELECT t.id, t.user_id, t.account_id, t.product_id, t.holding_id,
                       t.transaction_type, t.shares, t.unit_price, t.amount, t.fee,
                       t.net_amount, t.status, t.settlement_date, t.description,
                       t.created_at, t.updated_at,
                       p.name as product_name, p.product_code, p.product_type
                FROM investment_transactions t
                JOIN investment_products p ON t.product_id = p.id
                WHERE t.user_id = %s
            """
            params = [user_id]

            if product_id:
                query += " AND t.product_id = %s"
                params.append(product_id)

            if transaction_type:
                query += " AND t.transaction_type = %s"
                params.append(transaction_type)

            query += " ORDER BY t.created_at DESC OFFSET %s LIMIT %s"
            params.extend([skip, limit])

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, params)
                    return await cur.fetchall()

        except Exception as e:
            logger.error(f"Failed to get investment transactions for user {user_id}: {e}")
            raise

    # Product NAV operations

    async def get_latest_product_nav(self, product_id: UUID) -> Optional[dict]:
        """
        Get the latest NAV for a product.

        Args:
            product_id: Product unique identifier

        Returns:
            Latest NAV dictionary or None if not found
        """
        try:
            query = """
                SELECT id, product_id, nav_date, unit_nav, accumulated_nav,
                       daily_return_rate, created_at
                FROM product_nav_history
                WHERE product_id = %s
                ORDER BY nav_date DESC
                LIMIT 1
            """

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, (product_id,))
                    return await cur.fetchone()

        except Exception as e:
            logger.error(f"Failed to get latest NAV for product {product_id}: {e}")
            raise

    async def create_product_nav(self, nav_data: dict) -> dict:
        """
        Create a new product NAV record.

        Args:
            nav_data: NAV data dictionary

        Returns:
            Created NAV dictionary
        """
        try:
            query = """
                INSERT INTO product_nav_history (
                    product_id, nav_date, unit_nav, accumulated_nav, daily_return_rate
                ) VALUES (
                    %(product_id)s, %(nav_date)s, %(unit_nav)s, %(accumulated_nav)s, %(daily_return_rate)s
                )
                RETURNING id, product_id, nav_date, unit_nav, accumulated_nav,
                          daily_return_rate, created_at
            """

            async with self.db_manager.get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, nav_data)
                    result = await cur.fetchone()
                    await conn.commit()
                    return result

        except Exception as e:
            logger.error(f"Failed to create product NAV: {e}")
            raise

    # Helper methods for investment operations

    async def transaction(self):
        """
        Get a database transaction context manager.

        Returns:
            Database connection with transaction support
        """
        return self.db_manager.get_connection()
