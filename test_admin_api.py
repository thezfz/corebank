#!/usr/bin/env python3
"""
Test script for admin API endpoints
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

def test_get_users(token, status='active'):
    """Test getting users list"""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"status": status}

    response = requests.get(f"{BASE_URL}/admin/users", headers=headers, params=params)
    print(f"Get {status} users: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['items'])} {status} users")
        for user in data['items']:
            deleted_status = " (DELETED)" if user.get('deleted_at') else ""
            print(f"  - {user['username']} ({user['role']}) - Active: {user.get('is_active', 'N/A')}{deleted_status}")
    else:
        print(f"Error: {response.text}")

def test_get_user_detail(token, user_id):
    """Test getting user detail"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/admin/users/{user_id}", headers=headers)
    print(f"Get user detail: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print(f"User detail: {user['username']} - Active: {user.get('is_active', 'N/A')}")
        print(f"  Accounts: {user.get('account_count', 0)}")
        print(f"  Balance: {user.get('total_balance', '0.00')}")
        print(f"  Investments: {user.get('investment_count', 0)}")
    else:
        print(f"Error: {response.text}")



def test_soft_delete_user(token, user_id):
    """Test soft deleting user"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "reason": "API测试 - 软删除测试"
    }

    response = requests.delete(f"{BASE_URL}/admin/users/{user_id}", headers=headers, json=data)
    print(f"Soft delete user: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Soft delete result: {result.get('message', 'Success')}")
    else:
        print(f"Error: {response.text}")

def test_restore_user(token, user_id):
    """Test restoring user"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "reason": "API测试 - 恢复测试"
    }

    response = requests.post(f"{BASE_URL}/admin/users/{user_id}/restore", headers=headers, json=data)
    print(f"Restore user: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print(f"Restored user: {user['username']} - Active: {user.get('is_active', 'N/A')}")
    else:
        print(f"Error: {response.text}")

def create_test_user():
    """Create a test user for deletion testing"""
    import time
    # First register a test user with timestamp to ensure uniqueness
    timestamp = int(time.time())
    register_data = {
        "username": f"test_delete_user_{timestamp}",
        "password": "TestPassword123!"
    }

    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code == 201:
        user = response.json()
        print(f"Created test user: {user['username']} (ID: {user['id']})")
        return user['id']
    else:
        print(f"Failed to create test user: {response.text}")
        return None

def main():
    print("Testing Admin API endpoints...")

    # Get admin token
    token = get_admin_token()
    if not token:
        return

    print(f"Got admin token: {token[:50]}...")

    # Test get users
    print("\n1. Testing get users...")
    test_get_users(token)
    
    # Get first user for testing
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    if response.status_code == 200:
        users = response.json()['items']
        if users:
            test_user = users[0]
            user_id = test_user['id']
            
            print(f"\n2. Testing get user detail for {test_user['username']}...")
            test_get_user_detail(token, user_id)
            
            # Find a non-admin user for testing
            test_user = None
            for user in users:
                if user['role'] != 'admin':
                    test_user = user
                    break

            if test_user:
                print(f"\n3. Found test user: {test_user['username']}")
            else:
                print(f"\n3. No non-admin users found for testing")

    # Test soft delete with a new user
    print(f"\n5. Testing soft delete functionality...")
    test_user_id = create_test_user()
    if test_user_id:
        print(f"\n6. Soft deleting test user...")
        test_soft_delete_user(token, test_user_id)

        # Verify user is no longer in active list
        print(f"\n7. Verifying user is deleted from active list...")
        test_get_users(token, 'active')

        # Check deleted users list
        print(f"\n8. Checking deleted users list...")
        test_get_users(token, 'deleted')

        # Test restore functionality
        print(f"\n9. Testing restore functionality...")
        test_restore_user(token, test_user_id)

        # Verify user is back in active list
        print(f"\n10. Verifying user is restored to active list...")
        test_get_users(token, 'active')

if __name__ == "__main__":
    main()
