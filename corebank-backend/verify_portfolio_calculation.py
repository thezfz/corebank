#!/usr/bin/env python3
"""
Verify portfolio calculation logic.
"""

import asyncio
import httpx
import json


async def verify_portfolio_calculation():
    """Verify portfolio calculation."""
    
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
            
            # 2. Get investment holdings
            print("\n2. Getting investment holdings...")
            holdings_response = await client.get(
                f"{base_url}/api/v1/investments/holdings",
                headers=headers
            )
            
            if holdings_response.status_code != 200:
                print(f"❌ Failed to get holdings: {holdings_response.status_code}")
                return False
            
            holdings = holdings_response.json()
            print(f"✅ Retrieved {len(holdings)} holdings")
            
            # 3. Get portfolio summary
            print("\n3. Getting portfolio summary...")
            portfolio_response = await client.get(
                f"{base_url}/api/v1/investments/portfolio-summary",
                headers=headers
            )
            
            if portfolio_response.status_code != 200:
                print(f"❌ Failed to get portfolio summary: {portfolio_response.status_code}")
                return False
            
            portfolio = portfolio_response.json()
            print("✅ Retrieved portfolio summary")
            
            # 4. Manual calculation verification
            print("\n4. Verifying calculations...")
            print("=" * 60)
            
            # Calculate manually from holdings
            manual_total_assets = 0
            manual_total_invested = 0
            
            print("Individual holdings:")
            for i, holding in enumerate(holdings, 1):
                current_value = holding.get('current_value', 0)
                total_invested = holding.get('total_invested', 0)
                status = holding.get('status', 'unknown')
                
                print(f"  {i}. {holding.get('product_name', 'Unknown')}")
                print(f"     Status: {status}")
                print(f"     Current Value: ¥{current_value:,.2f}")
                print(f"     Total Invested: ¥{total_invested:,.2f}")
                print(f"     Gain/Loss: ¥{current_value - total_invested:,.2f}")
                
                # Only include active holdings in portfolio calculation
                if status == 'active':
                    manual_total_assets += current_value
                    manual_total_invested += total_invested
                    print(f"     ✅ Included in portfolio calculation")
                else:
                    print(f"     ❌ Excluded from portfolio (status: {status})")
                print()
            
            print("=" * 60)
            print("CALCULATION COMPARISON:")
            print(f"Manual calculation (active holdings only):")
            print(f"  Total Assets: ¥{manual_total_assets:,.2f}")
            print(f"  Total Invested: ¥{manual_total_invested:,.2f}")
            print(f"  Total Gain/Loss: ¥{manual_total_assets - manual_total_invested:,.2f}")
            
            print(f"\nAPI response:")
            print(f"  Total Assets: ¥{portfolio.get('total_assets', 0):,.2f}")
            print(f"  Total Invested: ¥{portfolio.get('total_invested', 0):,.2f}")
            print(f"  Total Gain/Loss: ¥{portfolio.get('total_gain_loss', 0):,.2f}")
            
            # Check if calculations match
            assets_match = abs(manual_total_assets - portfolio.get('total_assets', 0)) < 0.01
            invested_match = abs(manual_total_invested - portfolio.get('total_invested', 0)) < 0.01
            
            print(f"\nVERIFICATION RESULTS:")
            print(f"  Total Assets Match: {'✅' if assets_match else '❌'}")
            print(f"  Total Invested Match: {'✅' if invested_match else '❌'}")
            
            if not assets_match or not invested_match:
                print(f"\n⚠️  DISCREPANCY DETECTED!")
                print(f"  This suggests the portfolio calculation may include:")
                print(f"  - All holdings regardless of status, OR")
                print(f"  - Different calculation logic")
                
                # Check if including all holdings matches
                all_total_assets = sum(h.get('current_value', 0) for h in holdings)
                all_total_invested = sum(h.get('total_invested', 0) for h in holdings)
                
                print(f"\nIf including ALL holdings (regardless of status):")
                print(f"  Total Assets: ¥{all_total_assets:,.2f}")
                print(f"  Total Invested: ¥{all_total_invested:,.2f}")
                
                all_assets_match = abs(all_total_assets - portfolio.get('total_assets', 0)) < 0.01
                all_invested_match = abs(all_total_invested - portfolio.get('total_invested', 0)) < 0.01
                
                print(f"  All Holdings Assets Match: {'✅' if all_assets_match else '❌'}")
                print(f"  All Holdings Invested Match: {'✅' if all_invested_match else '❌'}")
                
                if all_assets_match and all_invested_match:
                    print(f"\n🔍 ISSUE IDENTIFIED: Portfolio calculation includes ALL holdings, not just active ones!")
                    print(f"   This may be incorrect behavior - typically only active holdings should be included.")
            else:
                print(f"\n✅ Calculations are correct!")
            
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"❌ Error during verification: {e}")
            return False


async def main():
    """Main verification function."""
    print("Verifying portfolio calculation logic...")
    print("=" * 60)
    
    success = await verify_portfolio_calculation()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Verification completed!")
    else:
        print("❌ Verification failed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
