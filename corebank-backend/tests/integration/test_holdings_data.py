#!/usr/bin/env python3
"""
Test script to check holdings data structure.
"""

import asyncio
import httpx
import json


async def test_holdings_data():
    """Test holdings data structure."""
    
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
            
            if holdings:
                print("\n3. Analyzing first holding data structure:")
                first_holding = holdings[0]
                print(json.dumps(first_holding, indent=2, default=str))
                
                print("\n4. Checking required fields for redemption modal:")
                required_fields = [
                    'id', 'shares', 'current_value', 'total_invested', 
                    'unrealized_gain_loss', 'purchase_date', 'product_name', 'status'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in first_holding:
                        missing_fields.append(field)
                        print(f"   ❌ Missing field: {field}")
                    else:
                        value = first_holding[field]
                        print(f"   ✅ {field}: {value} (type: {type(value).__name__})")
                
                if missing_fields:
                    print(f"\n❌ Missing fields: {missing_fields}")
                    
                    # Check for alternative field names
                    print("\nChecking for alternative field names:")
                    all_fields = list(first_holding.keys())
                    print(f"Available fields: {all_fields}")
                    
                    # Look for similar field names
                    for missing_field in missing_fields:
                        similar_fields = [f for f in all_fields if missing_field.lower() in f.lower() or f.lower() in missing_field.lower()]
                        if similar_fields:
                            print(f"   Possible alternatives for '{missing_field}': {similar_fields}")
                else:
                    print("\n✅ All required fields are present!")
                
                return len(missing_fields) == 0
            else:
                print("ℹ️  No holdings found")
                return True
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            return False


async def main():
    """Main test function."""
    print("Testing holdings data structure...")
    print("=" * 60)
    
    success = await test_holdings_data()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS! Holdings data structure is compatible.")
    else:
        print("❌ FAILED! Holdings data structure needs adjustment.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
