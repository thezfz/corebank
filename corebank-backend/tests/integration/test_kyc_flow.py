#!/usr/bin/env python3
"""
测试KYC流程
"""

import requests
import json
import random
import string

BASE_URL = "http://localhost:8000/api/v1"

def generate_random_username():
    """生成随机用户名"""
    return 'kyctest_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def register_and_login():
    """注册并登录新用户"""
    username = generate_random_username()
    password = "MySecure123!"
    
    # 注册
    register_data = {
        "username": username,
        "password": password
    }
    
    print(f"📝 注册新用户: {username}")
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code != 201:
        print(f"❌ 用户注册失败: {response.text}")
        return None
    
    # 登录
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ 用户注册并登录成功")
        return token
    else:
        print(f"❌ 用户登录失败: {response.text}")
        return None

def check_kyc_status(token):
    """检查KYC状态"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/auth/me/profile", headers=headers)
    if response.status_code == 200:
        data = response.json()
        
        # 检查KYC必要字段
        required_fields = ['real_name', 'id_number', 'phone', 'email']
        kyc_completed = all(data.get(field) for field in required_fields)
        
        print(f"📋 KYC状态检查:")
        print(f"  - 真实姓名: {data.get('real_name', '未设置')}")
        print(f"  - 证件号码: {data.get('id_number', '未设置')}")
        print(f"  - 手机号码: {data.get('phone', '未设置')}")
        print(f"  - 邮箱地址: {data.get('email', '未设置')}")
        print(f"  - KYC状态: {'已完成' if kyc_completed else '未完成'}")
        
        return kyc_completed
    else:
        print(f"❌ 获取用户信息失败: {response.text}")
        return False

def complete_kyc(token):
    """完成KYC认证"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n✏️ 完成KYC认证...")
    
    # KYC数据
    kyc_data = {
        "real_name": "张三",
        "english_name": "Zhang San",
        "id_type": "居民身份证",
        "id_number": "110101199001011234",
        "country": "中国",
        "ethnicity": "汉族",
        "gender": "男",
        "birth_date": "1990-01-01",
        "birth_place": "北京市",
        "phone": "13800138000",
        "email": "zhangsan@example.com",
        "address": "北京市朝阳区测试街道456号"
    }
    
    print(f"  发送KYC数据: {json.dumps(kyc_data, ensure_ascii=False, indent=2)}")
    
    response = requests.put(f"{BASE_URL}/auth/me/profile", json=kyc_data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ KYC认证完成")
        
        # 验证数据
        print(f"  验证结果:")
        print(f"    - 真实姓名: {data.get('real_name')}")
        print(f"    - 证件号码: {data.get('id_number')}")
        print(f"    - 手机号码: {data.get('phone')}")
        print(f"    - 邮箱地址: {data.get('email')}")
        
        return True
    else:
        print(f"❌ KYC认证失败: {response.text}")
        return False

def main():
    print("🧪 测试KYC认证流程")
    
    # 注册并登录新用户
    token = register_and_login()
    if not token:
        return
    
    # 检查初始KYC状态
    print("\n🔍 检查初始KYC状态...")
    initial_kyc_status = check_kyc_status(token)
    
    if initial_kyc_status:
        print("⚠️ 新用户KYC状态异常，应该是未完成状态")
        return
    
    # 完成KYC认证
    kyc_success = complete_kyc(token)
    if not kyc_success:
        return
    
    # 再次检查KYC状态
    print("\n🔍 检查KYC完成后状态...")
    final_kyc_status = check_kyc_status(token)
    
    if final_kyc_status:
        print("✅ KYC认证流程测试成功")
    else:
        print("❌ KYC认证后状态检查失败")
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    main()
