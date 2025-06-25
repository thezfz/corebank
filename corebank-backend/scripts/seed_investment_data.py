#!/usr/bin/env python3
"""
Seed script for investment data.

This script creates sample investment products for testing and development.
"""

import asyncio
import os
import sys
from decimal import Decimal
from datetime import datetime, date

# Add the parent directory to the path so we can import corebank modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from corebank.core.db import DatabaseManager
from corebank.repositories.postgres_repo import PostgresRepository


async def create_sample_products(repository: PostgresRepository):
    """Create sample investment products."""
    
    products = [
        {
            "product_code": "MMF001",
            "name": "数脉货币基金A",
            "product_type": "money_fund",
            "risk_level": 1,
            "expected_return_rate": Decimal("0.0250"),  # 2.5%
            "min_investment_amount": Decimal("1.00"),
            "max_investment_amount": None,
            "investment_period_days": None,  # Demand product
            "is_active": True,
            "description": "低风险货币基金，适合短期资金管理，随时申购赎回",
            "features": {
                "liquidity": "T+0",
                "risk_rating": "极低风险",
                "management_fee": "0.30%",
                "custodian_fee": "0.05%"
            }
        },
        {
            "product_code": "FT001",
            "name": "数脉稳健理财30天",
            "product_type": "fixed_term",
            "risk_level": 2,
            "expected_return_rate": Decimal("0.0380"),  # 3.8%
            "min_investment_amount": Decimal("1000.00"),
            "max_investment_amount": Decimal("1000000.00"),
            "investment_period_days": 30,
            "is_active": True,
            "description": "30天期固定收益理财产品，本金保障，收益稳定",
            "features": {
                "principal_protection": True,
                "risk_rating": "低风险",
                "early_redemption": False,
                "interest_payment": "到期一次性支付"
            }
        },
        {
            "product_code": "FT002",
            "name": "数脉稳健理财90天",
            "product_type": "fixed_term",
            "risk_level": 2,
            "expected_return_rate": Decimal("0.0420"),  # 4.2%
            "min_investment_amount": Decimal("5000.00"),
            "max_investment_amount": Decimal("5000000.00"),
            "investment_period_days": 90,
            "is_active": True,
            "description": "90天期固定收益理财产品，收益率更高，适合中期投资",
            "features": {
                "principal_protection": True,
                "risk_rating": "低风险",
                "early_redemption": False,
                "interest_payment": "到期一次性支付"
            }
        },
        {
            "product_code": "MF001",
            "name": "数脉成长混合基金",
            "product_type": "mutual_fund",
            "risk_level": 3,
            "expected_return_rate": Decimal("0.0680"),  # 6.8%
            "min_investment_amount": Decimal("100.00"),
            "max_investment_amount": None,
            "investment_period_days": None,
            "is_active": True,
            "description": "混合型基金，投资股票和债券，追求长期稳健增长",
            "features": {
                "asset_allocation": "股票60%-80%, 债券20%-40%",
                "risk_rating": "中等风险",
                "management_fee": "1.50%",
                "redemption_fee": "0.50%",
                "min_holding_period": "7天"
            }
        },
        {
            "product_code": "MF002",
            "name": "数脉价值股票基金",
            "product_type": "mutual_fund",
            "risk_level": 4,
            "expected_return_rate": Decimal("0.0850"),  # 8.5%
            "min_investment_amount": Decimal("100.00"),
            "max_investment_amount": None,
            "investment_period_days": None,
            "is_active": True,
            "description": "股票型基金，专注价值投资，适合风险承受能力较强的投资者",
            "features": {
                "asset_allocation": "股票≥80%",
                "risk_rating": "高风险",
                "management_fee": "1.80%",
                "redemption_fee": "0.75%",
                "investment_style": "价值投资"
            }
        },
        {
            "product_code": "INS001",
            "name": "数脉安心保险理财",
            "product_type": "insurance",
            "risk_level": 2,
            "expected_return_rate": Decimal("0.0450"),  # 4.5%
            "min_investment_amount": Decimal("10000.00"),
            "max_investment_amount": Decimal("1000000.00"),
            "investment_period_days": 365,  # 1 year
            "is_active": True,
            "description": "保险理财产品，提供保险保障的同时获得稳定收益",
            "features": {
                "insurance_coverage": "意外身故保障",
                "risk_rating": "低风险",
                "surrender_penalty": "前3年有退保费用",
                "guaranteed_return": "3.5%"
            }
        }
    ]
    
    created_products = []
    for product_data in products:
        try:
            product = await repository.create_investment_product(product_data)
            created_products.append(product)
            print(f"Created product: {product['name']} ({product['product_code']})")
        except Exception as e:
            print(f"Failed to create product {product_data['product_code']}: {e}")
    
    return created_products


async def create_sample_nav_data(repository: PostgresRepository, products):
    """Create sample NAV data for products."""
    
    from datetime import timedelta
    
    # Create NAV data for the last 30 days
    base_date = date.today() - timedelta(days=30)
    
    for product in products:
        if product['product_type'] in ['money_fund', 'mutual_fund']:
            # These products have daily NAV
            current_nav = Decimal("1.0000")
            
            for i in range(31):  # 31 days including today
                nav_date = base_date + timedelta(days=i)
                
                # Simulate some price movement
                if product['product_type'] == 'money_fund':
                    # Money fund NAV grows slowly and steadily
                    daily_return = Decimal("0.0001")  # 0.01% daily
                else:
                    # Mutual fund has more volatility
                    import random
                    daily_return = Decimal(str(random.uniform(-0.02, 0.03)))  # -2% to +3%
                
                current_nav = current_nav * (1 + daily_return)
                
                nav_data = {
                    "product_id": product['id'],
                    "nav_date": nav_date,
                    "unit_nav": current_nav,
                    "accumulated_nav": current_nav,
                    "daily_return_rate": daily_return
                }
                
                try:
                    await repository.create_product_nav(nav_data)
                except Exception as e:
                    # Skip if already exists
                    pass
            
            print(f"Created NAV data for {product['name']}")


async def main():
    """Main function to seed investment data."""
    
    # Initialize database manager
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    try:
        # Create repository
        repository = PostgresRepository(db_manager)
        
        print("Creating sample investment products...")
        products = await create_sample_products(repository)
        
        print(f"\nCreated {len(products)} products")
        
        print("\nCreating sample NAV data...")
        await create_sample_nav_data(repository, products)
        
        print("\nSeed data creation completed successfully!")
        
    except Exception as e:
        print(f"Error creating seed data: {e}")
        raise
    finally:
        await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
