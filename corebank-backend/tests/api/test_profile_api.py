#!/usr/bin/env python3
"""
Test script for user profile API endpoints.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

async def test_profile_api():
    """Test the user profile API endpoints."""
    
    async with aiohttp.ClientSession() as session:
        print("🔐 Testing User Profile API...")
        
        # Step 1: Login to get token
        print("\n1. Logging in...")
        login_data = {
            "username": "testuser",
            "password": "MySecure123!"
        }
        
        async with session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                login_result = await response.json()
                token = login_result["access_token"]
                print(f"✅ Login successful, token: {token[:20]}...")
            else:
                error_text = await response.text()
                print(f"❌ Login failed: {response.status} - {error_text}")
                return
        
        # Set authorization header
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Get current user profile
        print("\n2. Getting current user profile...")
        async with session.get(f"{BASE_URL}/auth/me/profile", headers=headers) as response:
            if response.status == 200:
                profile_data = await response.json()
                print(f"✅ Profile retrieved successfully:")
                print(json.dumps(profile_data, indent=2, ensure_ascii=False))
            else:
                error_text = await response.text()
                print(f"❌ Failed to get profile: {response.status} - {error_text}")
                return
        
        # Step 3: Update user profile
        print("\n3. Updating user profile...")
        update_data = {
            "real_name": "测试用户",
            "english_name": "Test User",
            "id_type": "居民身份证",
            "id_number": "123456789012345678",
            "country": "中国",
            "ethnicity": "汉族",
            "gender": "男",
            "birth_date": "1990-01-01",
            "birth_place": "北京市",
            "phone": "13800138000",
            "email": "testuser@example.com",
            "address": "北京市朝阳区测试街道123号"
        }
        
        async with session.put(f"{BASE_URL}/auth/me/profile", json=update_data, headers=headers) as response:
            if response.status == 200:
                updated_profile = await response.json()
                print(f"✅ Profile updated successfully:")
                print(json.dumps(updated_profile, indent=2, ensure_ascii=False))
            else:
                error_text = await response.text()
                print(f"❌ Failed to update profile: {response.status} - {error_text}")
                return
        
        # Step 4: Get updated profile to verify
        print("\n4. Verifying updated profile...")
        async with session.get(f"{BASE_URL}/auth/me/profile", headers=headers) as response:
            if response.status == 200:
                final_profile = await response.json()
                print(f"✅ Final profile verification:")
                print(json.dumps(final_profile, indent=2, ensure_ascii=False))
                
                # Check if update was successful
                if final_profile.get("profile", {}).get("real_name") == "测试用户":
                    print("\n🎉 Profile update test PASSED!")
                else:
                    print("\n❌ Profile update test FAILED - data not updated correctly")
            else:
                error_text = await response.text()
                print(f"❌ Failed to verify profile: {response.status} - {error_text}")

if __name__ == "__main__":
    asyncio.run(test_profile_api())
