#!/usr/bin/env python3
"""
测试个人信息修改功能
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

def get_profile(token):
    """获取当前用户个人信息"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📋 获取当前个人信息...")
    response = requests.get(f"{BASE_URL}/auth/me/profile", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"  - 用户ID: {data['id']}")
        print(f"  - 用户名: {data['username']}")

        # Check if user has profile data (flattened structure)
        profile_fields = ['real_name', 'phone', 'email', 'id_number']
        has_profile = any(data.get(field) for field in profile_fields)

        if has_profile:
            print(f"  - 真实姓名: {data.get('real_name', '无')}")
            print(f"  - 手机号码: {data.get('phone', '无')}")
            print(f"  - 邮箱地址: {data.get('email', '无')}")
            print(f"  - 证件号码: {data.get('id_number', '无')}")
        else:
            print(f"  - 个人信息: 无")
        return data
    else:
        print(f"❌ 获取个人信息失败: {response.text}")
        return None

def update_profile(token):
    """更新个人信息"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n✏️ 更新个人信息...")
    
    # 测试数据
    profile_data = {
        "real_name": "测试用户四",
        "english_name": "Test User 4",
        "id_type": "居民身份证",
        "id_number": "123456789012345678",
        "country": "中国",
        "ethnicity": "汉族",
        "gender": "男",
        "birth_date": "1990-01-01",
        "birth_place": "北京市",
        "phone": "13800138004",
        "email": "testuser4@example.com",
        "address": "北京市朝阳区测试街道123号"
    }
    
    print(f"  发送数据: {json.dumps(profile_data, ensure_ascii=False, indent=2)}")
    
    response = requests.put(f"{BASE_URL}/auth/me/profile", json=profile_data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 个人信息更新成功")
        # Show updated profile fields
        profile_data = {
            'real_name': data.get('real_name'),
            'english_name': data.get('english_name'),
            'phone': data.get('phone'),
            'email': data.get('email'),
            'id_number': data.get('id_number'),
            'country': data.get('country'),
            'gender': data.get('gender')
        }
        print(f"  - 更新后的个人信息: {json.dumps(profile_data, ensure_ascii=False, indent=2)}")
        return data
    else:
        print(f"❌ 个人信息更新失败: {response.text}")
        return None

def test_partial_update(token):
    """测试部分字段更新"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔄 测试部分字段更新...")
    
    # 只更新部分字段
    partial_data = {
        "real_name": "测试用户四号",
        "phone": "13900139004"
    }
    
    print(f"  发送数据: {json.dumps(partial_data, ensure_ascii=False, indent=2)}")
    
    response = requests.put(f"{BASE_URL}/auth/me/profile", json=partial_data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 部分字段更新成功")
        # Show updated profile fields
        profile_data = {
            'real_name': data.get('real_name'),
            'english_name': data.get('english_name'),
            'phone': data.get('phone'),
            'email': data.get('email'),
            'id_number': data.get('id_number'),
            'country': data.get('country'),
            'gender': data.get('gender')
        }
        print(f"  - 更新后的个人信息: {json.dumps(profile_data, ensure_ascii=False, indent=2)}")
        return data
    else:
        print(f"❌ 部分字段更新失败: {response.text}")
        return None

def main():
    print("🧪 开始测试个人信息修改功能")
    
    # 登录用户
    token = login_user()
    if not token:
        return
    
    # 获取当前个人信息
    get_profile(token)
    
    # 更新个人信息
    update_profile(token)
    
    # 再次获取个人信息，验证更新是否生效
    print("\n🔍 验证更新结果...")
    get_profile(token)
    
    # 测试部分字段更新
    test_partial_update(token)
    
    # 最终验证
    print("\n🔍 最终验证...")
    get_profile(token)
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    main()
