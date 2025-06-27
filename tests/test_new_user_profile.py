#!/usr/bin/env python3
"""
测试新用户的个人信息默认显示
"""

import requests
import json
import random
import string

BASE_URL = "http://localhost:8000/api/v1"

def generate_random_username():
    """生成随机用户名"""
    return 'testuser_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def register_new_user():
    """注册新用户"""
    username = generate_random_username()
    password = "MySecure123!"
    
    register_data = {
        "username": username,
        "password": password
    }
    
    print(f"📝 注册新用户: {username}")
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code == 201:
        print(f"✅ 用户注册成功")
        return username, password
    else:
        print(f"❌ 用户注册失败: {response.text}")
        return None, None

def login_user(username, password):
    """登录用户"""
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ 用户登录成功")
        return token
    else:
        print(f"❌ 用户登录失败: {response.text}")
        return None

def get_profile(token):
    """获取当前用户个人信息"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📋 获取新用户的个人信息...")
    response = requests.get(f"{BASE_URL}/auth/me/profile", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"  - 用户ID: {data['id']}")
        print(f"  - 用户名: {data['username']}")
        
        # Check profile fields
        profile_fields = {
            'real_name': '真实姓名',
            'english_name': '英文姓名',
            'id_type': '证件类型',
            'id_number': '证件号码',
            'country': '国家/地区',
            'ethnicity': '民族',
            'gender': '性别',
            'birth_date': '出生日期',
            'birth_place': '出生地',
            'phone': '手机号码',
            'email': '邮箱地址',
            'address': '联系地址'
        }
        
        print("\n  个人信息字段:")
        for field, label in profile_fields.items():
            value = data.get(field)
            if value is None:
                print(f"    - {label}: null (应显示为'未设置')")
            else:
                print(f"    - {label}: {value}")
        
        return data
    else:
        print(f"❌ 获取个人信息失败: {response.text}")
        return None

def main():
    print("🧪 测试新用户个人信息默认显示")
    
    # 注册新用户
    username, password = register_new_user()
    if not username:
        return
    
    # 登录用户
    token = login_user(username, password)
    if not token:
        return
    
    # 获取个人信息
    get_profile(token)
    
    print("\n✅ 测试完成")
    print("💡 请在前端页面检查个人信息是否显示为'未设置'")

if __name__ == "__main__":
    main()
