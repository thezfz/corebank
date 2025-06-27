#!/usr/bin/env python3
"""
测试理财产品购买API的脚本
"""

import asyncio
import aiohttp
import json
from decimal import Decimal

# 配置
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {
    "username": "purchasetest",
    "password": "TestPass123!"
}

async def login(session):
    """登录并获取访问令牌"""
    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    
    async with session.post(login_url, json=login_data) as response:
        if response.status == 200:
            result = await response.json()
            return result.get("access_token")
        else:
            error = await response.text()
            print(f"登录失败: {response.status} - {error}")
            return None

async def get_user_accounts(session, token):
    """获取用户账户"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with session.get(f"{BASE_URL}/accounts", headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            error = await response.text()
            print(f"获取账户失败: {response.status} - {error}")
            return []

async def get_investment_products(session, token):
    """获取投资产品"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with session.get(f"{BASE_URL}/investments/products", headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            error = await response.text()
            print(f"获取产品失败: {response.status} - {error}")
            return []

async def purchase_investment(session, token, purchase_data):
    """购买投资产品"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with session.post(f"{BASE_URL}/investments/purchase", json=purchase_data, headers=headers) as response:
        result = await response.text()
        if response.status == 200:
            return json.loads(result)
        else:
            print(f"购买失败: {response.status} - {result}")
            return None

async def get_investment_holdings(session, token):
    """获取投资持仓"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with session.get(f"{BASE_URL}/investments/holdings", headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            error = await response.text()
            print(f"获取持仓失败: {response.status} - {error}")
            return []

async def main():
    """主测试函数"""
    print("🚀 开始测试理财产品购买功能")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # 1. 登录
        print("1. 正在登录...")
        token = await login(session)
        if not token:
            print("❌ 登录失败，测试终止")
            return
        print("✅ 登录成功")
        
        # 2. 获取用户账户
        print("\n2. 获取用户账户...")
        accounts = await get_user_accounts(session, token)
        if not accounts:
            print("❌ 没有可用账户，测试终止")
            return
        
        account = accounts[0]
        print(f"✅ 找到账户: {account['account_number']}")
        print(f"   账户类型: {account['account_type']}")
        print(f"   账户余额: ¥{float(account['balance']):,.2f}")
        
        # 3. 获取投资产品
        print("\n3. 获取投资产品...")
        products = await get_investment_products(session, token)
        if not products:
            print("❌ 没有可用产品，测试终止")
            return
        
        # 选择第一个产品进行测试
        product = products[0]
        print(f"✅ 选择产品: {product['name']}")
        print(f"   产品代码: {product['product_code']}")
        print(f"   起投金额: ¥{float(product['min_investment_amount']):,.2f}")
        print(f"   预期收益率: {float(product['expected_return_rate']) * 100:.2f}%")
        
        # 4. 测试购买
        print("\n4. 测试购买...")
        
        # 计算购买金额（使用起投金额的2倍）
        purchase_amount = float(product['min_investment_amount']) * 2
        
        if purchase_amount > float(account['balance']):
            purchase_amount = float(product['min_investment_amount'])
        
        purchase_data = {
            "account_id": account['id'],
            "product_id": product['id'],
            "amount": purchase_amount
        }
        
        print(f"   购买金额: ¥{purchase_amount:,.2f}")
        print(f"   购买数据: {purchase_data}")
        
        transaction = await purchase_investment(session, token, purchase_data)
        if transaction:
            print("✅ 购买成功！")
            print(f"   交易ID: {transaction['id']}")
            print(f"   交易类型: {transaction['transaction_type']}")
            print(f"   购买份额: {float(transaction['shares']):.4f}")
            print(f"   单位净值: ¥{float(transaction['unit_price']):.4f}")
            print(f"   交易金额: ¥{float(transaction['amount']):,.2f}")
            print(f"   手续费: ¥{float(transaction['fee']):,.2f}")
            print(f"   净投资额: ¥{float(transaction['net_amount']):,.2f}")
        else:
            print("❌ 购买失败")
            return
        
        # 5. 验证持仓
        print("\n5. 验证持仓...")
        holdings = await get_investment_holdings(session, token)
        if holdings:
            print(f"✅ 持仓创建成功，共 {len(holdings)} 个持仓")
            for holding in holdings:
                print(f"   产品: {holding['product_name']}")
                print(f"   持有份额: {float(holding['shares']):.4f}")
                print(f"   总投资额: ¥{float(holding['total_invested']):,.2f}")
                print(f"   当前价值: ¥{float(holding['current_value']):,.2f}")
        else:
            print("❌ 持仓验证失败")
        
        # 6. 再次获取账户余额验证扣款
        print("\n6. 验证账户余额...")
        updated_accounts = await get_user_accounts(session, token)
        if updated_accounts:
            updated_account = updated_accounts[0]
            original_balance = float(account['balance'])
            new_balance = float(updated_account['balance'])
            deducted = original_balance - new_balance
            
            print(f"✅ 账户余额更新")
            print(f"   原余额: ¥{original_balance:,.2f}")
            print(f"   新余额: ¥{new_balance:,.2f}")
            print(f"   扣除金额: ¥{deducted:,.2f}")
            
            if abs(deducted - purchase_amount) < 0.01:
                print("✅ 扣款金额正确")
            else:
                print(f"❌ 扣款金额不正确，预期: ¥{purchase_amount:,.2f}")
        
    print("\n" + "=" * 50)
    print("🎉 测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
