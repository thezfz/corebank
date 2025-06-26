#!/usr/bin/env python3
"""
测试用户管理分页功能
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def login_admin():
    """登录管理员账户"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ 管理员登录成功")
        return token
    else:
        print(f"❌ 管理员登录失败: {response.text}")
        return None

def test_pagination(token):
    """测试分页功能"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔍 测试分页功能...")
    
    # 测试第1页
    print("\n📄 测试第1页:")
    response = requests.get(f"{BASE_URL}/admin/users?page=1&page_size=5", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"  - 第1页用户数: {len(data['items'])}")
        print(f"  - 总用户数: {data['total_count']}")
        print(f"  - 总页数: {data['total_pages']}")
        print(f"  - 有下一页: {data['has_next']}")
        
        # 测试第2页
        if data['has_next']:
            print("\n📄 测试第2页:")
            response2 = requests.get(f"{BASE_URL}/admin/users?page=2&page_size=5", headers=headers)
            if response2.status_code == 200:
                data2 = response2.json()
                print(f"  - 第2页用户数: {len(data2['items'])}")
                print(f"  - 有上一页: {data2['has_previous']}")
                print(f"  - 有下一页: {data2['has_next']}")
            else:
                print(f"  ❌ 第2页请求失败: {response2.text}")
        
        # 测试第3页
        if data['total_pages'] >= 3:
            print("\n📄 测试第3页:")
            response3 = requests.get(f"{BASE_URL}/admin/users?page=3&page_size=5", headers=headers)
            if response3.status_code == 200:
                data3 = response3.json()
                print(f"  - 第3页用户数: {len(data3['items'])}")
                print(f"  - 有上一页: {data3['has_previous']}")
                print(f"  - 有下一页: {data3['has_next']}")
            else:
                print(f"  ❌ 第3页请求失败: {response3.text}")
    else:
        print(f"❌ 第1页请求失败: {response.text}")

def test_search(token):
    """测试搜索功能"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔍 测试搜索功能...")
    
    # 搜索 "test"
    print("\n🔎 搜索 'test':")
    response = requests.get(f"{BASE_URL}/admin/users?search=test&page=1&page_size=10", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"  - 搜索结果数: {len(data['items'])}")
        print(f"  - 总匹配数: {data['total_count']}")
        for user in data['items']:
            print(f"    - {user['username']}")
    else:
        print(f"❌ 搜索请求失败: {response.text}")
    
    # 搜索 "admin"
    print("\n🔎 搜索 'admin':")
    response = requests.get(f"{BASE_URL}/admin/users?search=admin&page=1&page_size=10", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"  - 搜索结果数: {len(data['items'])}")
        print(f"  - 总匹配数: {data['total_count']}")
        for user in data['items']:
            print(f"    - {user['username']}")
    else:
        print(f"❌ 搜索请求失败: {response.text}")

def main():
    print("🧪 开始测试用户管理分页功能")
    
    # 登录管理员
    token = login_admin()
    if not token:
        return
    
    # 测试分页
    test_pagination(token)
    
    # 测试搜索
    test_search(token)
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    main()
