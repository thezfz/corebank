#!/usr/bin/env python3
"""
Test script to verify that total transaction records include investment transactions.
"""

import asyncio
import httpx


async def test_merged_transactions():
    """Test that total transactions include investment transactions."""
    
    base_url = "http://localhost:8000"
    
    # Test data
    test_user = {
        "username": "testuser",
        "password": "MySecure123!"
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
                return False
            
            token_data = login_response.json()
            token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            print("✅ Login successful")
            
            # 2. Get recent transactions (should include investment transactions)
            print("\n2. Getting recent transactions...")
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
            
            # Check for investment transactions (now in Chinese)
            investment_transactions = [
                tx for tx in recent_transactions
                if tx.get('transaction_type', '') in ['理财申购', '理财赎回']
            ]
            
            print(f"   - Regular transactions: {len(recent_transactions) - len(investment_transactions)}")
            print(f"   - Investment transactions: {len(investment_transactions)}")
            
            # Print some transaction details
            print("\n   Recent transactions:")
            for i, transaction in enumerate(recent_transactions[:5]):  # Show first 5
                tx_type = transaction.get('transaction_type', 'unknown')
                amount = transaction.get('amount', 0)
                description = transaction.get('description', 'No description')
                timestamp = transaction.get('timestamp', 'No timestamp')
                
                print(f"     {i+1}. Type: {tx_type}")
                print(f"        Amount: ¥{amount}")
                print(f"        Description: {description}")
                print(f"        Time: {timestamp}")
                print()
            
            # 3. Get accounts to test account-specific transactions
            print("3. Getting user accounts...")
            accounts_response = await client.get(
                f"{base_url}/api/v1/accounts",
                headers=headers
            )
            
            if accounts_response.status_code != 200:
                print(f"❌ Failed to get accounts: {accounts_response.status_code}")
                return False
            
            accounts = accounts_response.json()
            if not accounts:
                print("❌ No accounts found")
                return False
            
            account_id = accounts[0]['id']
            print(f"✅ Using account: {account_id}")
            
            # 4. Get account-specific transactions
            print("\n4. Getting account transactions...")
            account_tx_response = await client.get(
                f"{base_url}/api/v1/transactions/account/{account_id}",
                headers=headers
            )
            
            if account_tx_response.status_code != 200:
                print(f"❌ Failed to get account transactions: {account_tx_response.status_code}")
                print(f"Response: {account_tx_response.text}")
                return False
            
            account_tx_data = account_tx_response.json()
            account_transactions = account_tx_data.get('items', [])
            print(f"✅ Retrieved {len(account_transactions)} account transactions")
            
            # Check for investment transactions in account history (now in Chinese)
            account_investment_transactions = [
                tx for tx in account_transactions
                if tx.get('transaction_type', '') in ['理财申购', '理财赎回']
            ]
            
            print(f"   - Regular transactions: {len(account_transactions) - len(account_investment_transactions)}")
            print(f"   - Investment transactions: {len(account_investment_transactions)}")
            
            # 5. Compare with pure investment transactions
            print("\n5. Getting pure investment transactions for comparison...")
            investment_response = await client.get(
                f"{base_url}/api/v1/investments/transactions",
                headers=headers
            )
            
            if investment_response.status_code != 200:
                print(f"❌ Failed to get investment transactions: {investment_response.status_code}")
                return False
            
            pure_investment_transactions = investment_response.json()
            print(f"✅ Retrieved {len(pure_investment_transactions)} pure investment transactions")
            
            # Verify that investment transactions are included in total transactions
            success = True
            if len(investment_transactions) == 0 and len(pure_investment_transactions) > 0:
                print("❌ Investment transactions are missing from recent transactions!")
                success = False
            elif len(investment_transactions) > 0:
                print("✅ Investment transactions are included in recent transactions!")
            
            if len(account_investment_transactions) == 0 and len(pure_investment_transactions) > 0:
                print("❌ Investment transactions are missing from account transactions!")
                success = False
            elif len(account_investment_transactions) > 0:
                print("✅ Investment transactions are included in account transactions!")
            
            return success
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            return False


async def main():
    """Main test function."""
    print("Testing merged transaction functionality...")
    print("=" * 60)
    
    success = await test_merged_transactions()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS! Investment transactions are properly merged with total transactions.")
    else:
        print("❌ FAILED! Investment transactions are not properly merged.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
