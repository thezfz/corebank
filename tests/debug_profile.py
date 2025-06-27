#!/usr/bin/env python3
"""
调试个人信息API
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def login_user():
    """登录测试用户"""
    login_data = {
        "username": "testuser4",
        "password": "MySecure123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ 用户登录成功")
        return token
    else:
        print(f"❌ 用户登录失败: {response.text}")
        return None

def debug_profile_api(token):
    """调试个人信息API"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔍 调试个人信息API...")
    response = requests.get(f"{BASE_URL}/auth/me/profile", headers=headers)
    
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"原始响应: {response.text}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"解析后的JSON: {json.dumps(data, ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"JSON解析失败: {e}")
    
    return response

def main():
    print("🔧 调试个人信息API")
    
    # 登录用户
    token = login_user()
    if not token:
        return
    
    # 调试API
    debug_profile_api(token)

if __name__ == "__main__":
    main()
