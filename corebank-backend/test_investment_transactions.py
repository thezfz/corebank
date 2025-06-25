#!/usr/bin/env python3
"""
Simple test script to verify investment transaction functionality.
This script tests the investment transaction API endpoints.
"""

import asyncio
import httpx
import json
from decimal import Decimal


async def test_investment_transactions():
    """Test investment transaction endpoints."""
    
    base_url = "http://localhost:8000"
    
    # Test data
    test_user = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Login to get token
            print("1. Logging in...")
            login_response = await client.post(
                f"{base_url}/api/v1/auth/login",
                json={
                    "username": test_user["username"],
                    "password": test_user["password"]
                }
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Response: {login_response.text}")
                return False
            
            token_data = login_response.json()
            token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            print("✅ Login successful")
            
            # 2. Get investment transactions
            print("\n2. Getting investment transactions...")
            transactions_response = await client.get(
                f"{base_url}/api/v1/investments/transactions",
                headers=headers
            )
            
            if transactions_response.status_code != 200:
                print(f"❌ Failed to get investment transactions: {transactions_response.status_code}")
                print(f"Response: {transactions_response.text}")
                return False
            
            transactions = transactions_response.json()
            print(f"✅ Retrieved {len(transactions)} investment transactions")
            
            # Print transaction details
            for i, transaction in enumerate(transactions[:3]):  # Show first 3
                print(f"   Transaction {i+1}:")
                print(f"     Type: {transaction.get('transaction_type')}")
                print(f"     Amount: {transaction.get('amount')}")
                print(f"     Status: {transaction.get('status')}")
                print(f"     Date: {transaction.get('created_at')}")
            
            # 3. Get investment holdings
            print("\n3. Getting investment holdings...")
            holdings_response = await client.get(
                f"{base_url}/api/v1/investments/holdings",
                headers=headers
            )
            
            if holdings_response.status_code != 200:
                print(f"❌ Failed to get investment holdings: {holdings_response.status_code}")
                print(f"Response: {holdings_response.text}")
                return False
            
            holdings = holdings_response.json()
            print(f"✅ Retrieved {len(holdings)} investment holdings")
            
            # 4. Get portfolio summary
            print("\n4. Getting portfolio summary...")
            summary_response = await client.get(
                f"{base_url}/api/v1/investments/portfolio-summary",
                headers=headers
            )
            
            if summary_response.status_code != 200:
                print(f"❌ Failed to get portfolio summary: {summary_response.status_code}")
                print(f"Response: {summary_response.text}")
                return False
            
            summary = summary_response.json()
            print(f"✅ Portfolio summary retrieved")
            print(f"   Total assets: {summary.get('total_assets')}")
            print(f"   Total invested: {summary.get('total_invested')}")
            print(f"   Holdings count: {summary.get('holdings_count')}")
            
            # 5. Get regular transactions
            print("\n5. Getting recent transactions...")
            recent_response = await client.get(
                f"{base_url}/api/v1/transactions/recent",
                headers=headers
            )
            
            if recent_response.status_code != 200:
                print(f"❌ Failed to get recent transactions: {recent_response.status_code}")
                print(f"Response: {recent_response.text}")
                return False
            
            recent_data = recent_response.json()
            recent_transactions = recent_data.get('items', [])
            print(f"✅ Retrieved {len(recent_transactions)} recent transactions")
            
            # Print transaction details
            for i, transaction in enumerate(recent_transactions[:3]):  # Show first 3
                print(f"   Transaction {i+1}:")
                print(f"     Type: {transaction.get('transaction_type')}")
                print(f"     Amount: {transaction.get('amount')}")
                print(f"     Status: {transaction.get('status')}")
                print(f"     Date: {transaction.get('timestamp')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            return False


async def main():
    """Main test function."""
    print("Testing investment transaction functionality...")
    print("=" * 60)
    
    success = await test_investment_transactions()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! Investment transaction functionality is working.")
    else:
        print("❌ Some tests failed. Check the output above.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
