#!/usr/bin/env python3
"""
Test script for admin transaction monitoring API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def get_admin_token():
    """Get admin token for testing"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_get_all_accounts(token):
    """Test getting all accounts"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/admin/accounts", headers=headers)
    print(f"Get all accounts: {response.status_code}")
    if response.status_code == 200:
        accounts = response.json()
        print(f"Found {len(accounts)} accounts")
        for account in accounts[:3]:  # Show first 3
            real_name = account.get('real_name')
            username = account.get('username', 'Unknown')
            owner_name = real_name if real_name else username
            print(f"  - {account['account_number']} ({account['account_type']}) - {owner_name}")
        return accounts
    else:
        print(f"Error: {response.text}")
        return []

def test_get_all_transactions(token, account_id=None):
    """Test getting all transactions"""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": 1, "page_size": 10}
    
    if account_id:
        params["account_id"] = account_id
    
    response = requests.get(f"{BASE_URL}/admin/transactions", headers=headers, params=params)
    print(f"Get all transactions: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total_count']} total transactions, showing {len(data['items'])}")
        for transaction in data['items'][:3]:  # Show first 3
            real_name = transaction.get('real_name')
            username = transaction.get('username', 'Unknown')
            user_name = real_name if real_name else username
            print(f"  - {transaction['transaction_type']} ¥{transaction['amount']} - {user_name}")
        return data
    else:
        print(f"Error: {response.text}")
        return None

def test_get_transaction_statistics(token):
    """Test getting transaction statistics"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/admin/transaction-statistics", headers=headers)
    print(f"Get transaction statistics: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print("Transaction Statistics:")
        print(f"  - Total transactions: {stats.get('total_transactions', 0)}")
        print(f"  - Deposits: {stats.get('deposit_count', 0)}")
        print(f"  - Withdrawals: {stats.get('withdrawal_count', 0)}")
        print(f"  - Transfers: {stats.get('transfer_count', 0)}")
        print(f"  - Last 24h: {stats.get('transactions_24h', 0)}")
        return stats
    else:
        print(f"Error: {response.text}")
        return None

def test_search_transactions(token, search_term):
    """Test searching transactions by user"""
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "page": 1,
        "page_size": 5,
        "user_search": search_term
    }
    
    response = requests.get(f"{BASE_URL}/admin/transactions", headers=headers, params=params)
    print(f"Search transactions for '{search_term}': {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total_count']} matching transactions")
        for transaction in data['items']:
            real_name = transaction.get('real_name')
            username = transaction.get('username', 'Unknown')
            user_name = real_name if real_name else username
            print(f"  - {transaction['transaction_type']} ¥{transaction['amount']} - {user_name}")
        return data
    else:
        print(f"Error: {response.text}")
        return None

def main():
    print("Testing Admin Transaction Monitoring API endpoints...")
    
    # Get admin token
    token = get_admin_token()
    if not token:
        return
    
    print(f"Got admin token: {token[:50]}...")
    
    # Test get all accounts
    print("\n1. Testing get all accounts...")
    accounts = test_get_all_accounts(token)
    
    # Test get transaction statistics
    print("\n2. Testing get transaction statistics...")
    test_get_transaction_statistics(token)
    
    # Test get all transactions
    print("\n3. Testing get all transactions...")
    test_get_all_transactions(token)
    
    # Test get transactions for specific account
    if accounts:
        print(f"\n4. Testing get transactions for specific account...")
        test_get_all_transactions(token, accounts[0]['id'])
    
    # Test search transactions
    print(f"\n5. Testing search transactions...")
    test_search_transactions(token, "test")

if __name__ == "__main__":
    main()
