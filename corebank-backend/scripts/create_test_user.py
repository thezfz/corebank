#!/usr/bin/env python3
"""
Create test user for investment testing.

This script creates a test user with accounts for testing investment functionality.
"""

import asyncio
import os
import sys
from decimal import Decimal

# Add the parent directory to the path so we can import corebank modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from corebank.core.db import DatabaseManager
from corebank.repositories.postgres_repo import PostgresRepository
from corebank.services.account_service import AccountService
from corebank.models.account import AccountCreate, AccountType
from corebank.security.password import hash_password


async def create_test_user():
    """Create a test user with accounts."""
    
    # Initialize database manager
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    try:
        # Create repository and services
        repository = PostgresRepository(db_manager)
        account_service = AccountService(repository)

        # Test user data
        test_user_data = {
            "username": "investor",
            "email": "investor@example.com",
            "password": "password123",
            "full_name": "投资测试用户"
        }

        print("Creating test user...")

        # Check if user already exists
        existing_user = await repository.get_user_by_username(test_user_data["username"])
        if existing_user:
            print(f"User {test_user_data['username']} already exists")
            user = existing_user
        else:
            # Create user directly with proper bcrypt hashing
            password_hash = hash_password(test_user_data["password"])

            user = await repository.create_user(
                username=test_user_data["username"],
                hashed_password=password_hash
            )
            print(f"Created user: {user['username']} (ID: {user['id']})")
        
        # Check if user has accounts
        existing_accounts = await repository.get_user_accounts(user['id'])
        if existing_accounts:
            print(f"User already has {len(existing_accounts)} accounts")
            for account in existing_accounts:
                print(f"  - {account['account_type']}: {account['account_number']} (Balance: ¥{account['balance']})")
        else:
            # Create accounts
            print("Creating accounts...")
            
            # Create checking account with balance
            checking_account_data = AccountCreate(
                account_type=AccountType.CHECKING,
                initial_deposit=Decimal("100000.00")  # 10万元用于测试
            )

            checking_account = await account_service.create_account(
                user_id=user['id'],
                account_data=checking_account_data
            )
            print(f"Created checking account: {checking_account.account_number} with balance ¥{checking_account.balance}")

            # Create savings account
            savings_account_data = AccountCreate(
                account_type=AccountType.SAVINGS,
                initial_deposit=Decimal("50000.00")  # 5万元
            )

            savings_account = await account_service.create_account(
                user_id=user['id'],
                account_data=savings_account_data
            )
            print(f"Created savings account: {savings_account.account_number} with balance ¥{savings_account.balance}")
        
        print("\nTest user setup completed!")
        print(f"Username: {test_user_data['username']}")
        print(f"Password: {test_user_data['password']}")
        print("You can now log in and test investment features.")
        
    except Exception as e:
        print(f"Error creating test user: {e}")
        raise
    finally:
        await db_manager.close()


if __name__ == "__main__":
    asyncio.run(create_test_user())
