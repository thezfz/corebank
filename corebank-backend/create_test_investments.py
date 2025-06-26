#!/usr/bin/env python3
"""
Create some test investments to verify portfolio calculations.
"""

import asyncio
import httpx
import json


async def create_test_investments():
    """Create test investments."""
    
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
            
            # 2. Get user accounts
            print("\n2. Getting user accounts...")
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
            
            account = accounts[0]  # Use first account
            balance = float(account['balance']) if isinstance(account['balance'], str) else account['balance']
            print(f"✅ Using account: {account['account_number']} (Balance: ¥{balance:,.2f})")
            
            # 3. Get investment products
            print("\n3. Getting investment products...")
            products_response = await client.get(
                f"{base_url}/api/v1/investments/products",
                headers=headers
            )
            
            if products_response.status_code != 200:
                print(f"❌ Failed to get products: {products_response.status_code}")
                return False
            
            products = products_response.json()
            if not products:
                print("❌ No products found")
                return False
            
            print(f"✅ Found {len(products)} investment products")
            
            # 4. Make some test purchases
            print("\n4. Making test purchases...")
            
            purchases = [
                {"product": products[0], "amount": 5000},
                {"product": products[1], "amount": 3000},
                {"product": products[2], "amount": 2000},
            ]
            
            for i, purchase in enumerate(purchases, 1):
                product = purchase["product"]
                amount = purchase["amount"]
                
                print(f"\n   Purchase {i}: {product['name']}")
                print(f"   Amount: ¥{amount:,.2f}")
                
                # Check if we have enough balance
                current_balance = float(account['balance']) if isinstance(account['balance'], str) else account['balance']
                if current_balance < amount:
                    print(f"   ❌ Insufficient balance (need ¥{amount:,.2f}, have ¥{current_balance:,.2f})")
                    continue
                
                # Make purchase
                purchase_response = await client.post(
                    f"{base_url}/api/v1/investments/purchase",
                    headers=headers,
                    json={
                        "product_id": product["id"],
                        "account_id": account["id"],
                        "amount": amount
                    }
                )
                
                if purchase_response.status_code == 200:
                    print(f"   ✅ Purchase successful")
                    # Update account balance for next purchase
                    account['balance'] = current_balance - amount
                else:
                    print(f"   ❌ Purchase failed: {purchase_response.status_code}")
                    if purchase_response.status_code != 500:
                        error_detail = purchase_response.json().get('detail', 'Unknown error')
                        print(f"      Error: {error_detail}")
            
            # 5. Verify new portfolio
            print("\n5. Verifying updated portfolio...")
            portfolio_response = await client.get(
                f"{base_url}/api/v1/investments/portfolio-summary",
                headers=headers
            )
            
            if portfolio_response.status_code == 200:
                portfolio = portfolio_response.json()
                print(f"✅ Updated Portfolio:")
                print(f"   Total Assets: ¥{portfolio.get('total_assets', 0):,.2f}")
                print(f"   Total Invested: ¥{portfolio.get('total_invested', 0):,.2f}")
                print(f"   Total Gain/Loss: ¥{portfolio.get('total_gain_loss', 0):,.2f}")
                print(f"   Active Holdings: {portfolio.get('active_products_count', 0)}")
            else:
                print(f"❌ Failed to get updated portfolio: {portfolio_response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False


async def main():
    """Main test function."""
    print("Creating test investments...")
    print("=" * 60)
    
    success = await create_test_investments()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Test investments created successfully!")
        print("💡 You can now check the frontend to see updated portfolio values.")
    else:
        print("❌ Failed to create test investments!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
