"""
Test investment purchase and holdings functionality.

This test covers the complete investment purchase flow and holdings retrieval,
including decimal precision handling.
"""

import pytest
from decimal import Decimal
from uuid import uuid4
from datetime import datetime, timezone

from corebank.services.investment_service import InvestmentService
from corebank.models.investment import (
    InvestmentPurchaseRequest,
    ProductType,
    RiskLevel,
    HoldingStatus,
    TransactionStatus
)
from corebank.repositories.postgres_repo import PostgresRepository
from corebank.core.exceptions import NotFoundError, ValidationError


class TestInvestmentPurchase:
    """Test investment purchase functionality."""

    @pytest.fixture
    async def investment_service(self, db_manager):
        """Create investment service instance."""
        repository = PostgresRepository(db_manager)
        return InvestmentService(repository)

    @pytest.fixture
    async def test_user(self, db_manager):
        """Create a test user."""
        user_data = {
            "username": f"testuser_{uuid4().hex[:8]}",
            "email": f"test_{uuid4().hex[:8]}@example.com",
            "password_hash": "hashed_password",
            "full_name": "Test User",
            "phone": "1234567890"
        }
        
        query = """
            INSERT INTO users (username, email, password_hash, full_name, phone)
            VALUES (%(username)s, %(email)s, %(password_hash)s, %(full_name)s, %(phone)s)
            RETURNING id, username, email, full_name, phone, created_at, updated_at
        """
        
        async with db_manager.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, user_data)
                result = await cur.fetchone()
                await conn.commit()
                return dict(zip([desc[0] for desc in cur.description], result))

    @pytest.fixture
    async def test_account(self, db_manager, test_user):
        """Create a test account with sufficient balance."""
        account_data = {
            "user_id": test_user["id"],
            "account_number": f"ACC{uuid4().hex[:10].upper()}",
            "account_type": "savings",
            "balance": Decimal("10000.00"),
            "currency": "CNY",
            "status": "active"
        }
        
        query = """
            INSERT INTO accounts (user_id, account_number, account_type, balance, currency, status)
            VALUES (%(user_id)s, %(account_number)s, %(account_type)s, %(balance)s, %(currency)s, %(status)s)
            RETURNING id, user_id, account_number, account_type, balance, currency, status, created_at, updated_at
        """
        
        async with db_manager.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, account_data)
                result = await cur.fetchone()
                await conn.commit()
                return dict(zip([desc[0] for desc in cur.description], result))

    @pytest.fixture
    async def test_product(self, db_manager):
        """Create a test investment product."""
        product_data = {
            "product_code": f"TEST{uuid4().hex[:6].upper()}",
            "name": "测试理财产品",
            "product_type": ProductType.MONEY_MARKET.value,
            "risk_level": RiskLevel.LOW.value,
            "expected_return_rate": Decimal("4.50"),
            "min_investment_amount": Decimal("1000.00"),
            "max_investment_amount": Decimal("1000000.00"),
            "investment_period_days": 90,
            "is_active": True,
            "description": "测试用理财产品",
            "features": ["低风险", "稳健收益"]
        }
        
        query = """
            INSERT INTO investment_products (
                product_code, name, product_type, risk_level, expected_return_rate,
                min_investment_amount, max_investment_amount, investment_period_days,
                is_active, description, features
            ) VALUES (
                %(product_code)s, %(name)s, %(product_type)s, %(risk_level)s, %(expected_return_rate)s,
                %(min_investment_amount)s, %(max_investment_amount)s, %(investment_period_days)s,
                %(is_active)s, %(description)s, %(features)s
            )
            RETURNING id, product_code, name, product_type, risk_level, expected_return_rate,
                      min_investment_amount, max_investment_amount, investment_period_days,
                      is_active, description, features, created_at, updated_at
        """
        
        async with db_manager.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, product_data)
                result = await cur.fetchone()
                await conn.commit()
                return dict(zip([desc[0] for desc in cur.description], result))

    async def test_purchase_investment_success(self, investment_service, test_user, test_account, test_product):
        """Test successful investment purchase."""
        # Arrange
        purchase_request = InvestmentPurchaseRequest(
            account_id=test_account["id"],
            product_id=test_product["id"],
            amount=Decimal("5000.00")
        )
        
        # Act
        transaction = await investment_service.purchase_investment(
            user_id=test_user["id"],
            purchase_request=purchase_request
        )
        
        # Assert
        assert transaction is not None
        assert transaction.user_id == test_user["id"]
        assert transaction.account_id == test_account["id"]
        assert transaction.product_id == test_product["id"]
        assert transaction.amount == Decimal("5000.00")
        assert transaction.status == TransactionStatus.CONFIRMED
        assert transaction.fee >= 0
        assert transaction.net_amount == transaction.amount - transaction.fee
        assert transaction.shares > 0
        assert transaction.unit_price > 0

    async def test_get_holdings_after_purchase(self, investment_service, test_user, test_account, test_product):
        """Test getting holdings after purchase with proper decimal precision."""
        # Arrange - Purchase investment first
        purchase_request = InvestmentPurchaseRequest(
            account_id=test_account["id"],
            product_id=test_product["id"],
            amount=Decimal("5000.00")
        )
        
        await investment_service.purchase_investment(
            user_id=test_user["id"],
            purchase_request=purchase_request
        )
        
        # Act
        holdings = await investment_service.get_user_holdings(test_user["id"])
        
        # Assert
        assert len(holdings) == 1
        holding = holdings[0]
        
        # Check basic properties
        assert holding.user_id == test_user["id"]
        assert holding.account_id == test_account["id"]
        assert holding.product_id == test_product["id"]
        assert holding.status == HoldingStatus.ACTIVE
        
        # Check decimal precision - should not exceed model constraints
        assert holding.current_value.as_tuple().exponent >= -4  # max 4 decimal places
        assert holding.unrealized_gain_loss.as_tuple().exponent >= -4  # max 4 decimal places
        assert len(str(holding.return_rate).replace('.', '').replace('-', '')) <= 8  # max 8 digits total
        
        # Check calculated values are reasonable
        assert holding.shares > 0
        assert holding.average_cost > 0
        assert holding.total_invested > 0
        assert holding.current_value > 0

    async def test_portfolio_summary_after_purchase(self, investment_service, test_user, test_account, test_product):
        """Test portfolio summary after purchase."""
        # Arrange - Purchase investment first
        purchase_request = InvestmentPurchaseRequest(
            account_id=test_account["id"],
            product_id=test_product["id"],
            amount=Decimal("3000.00")
        )
        
        await investment_service.purchase_investment(
            user_id=test_user["id"],
            purchase_request=purchase_request
        )
        
        # Act
        summary = await investment_service.get_portfolio_summary(test_user["id"])
        
        # Assert
        assert summary is not None
        assert summary.holdings_count == 1
        assert summary.active_products_count == 1
        assert summary.total_invested > 0
        assert summary.total_assets > 0
        
        # Check decimal precision
        assert summary.total_assets.as_tuple().exponent >= -4
        assert summary.total_invested.as_tuple().exponent >= -4
        assert summary.total_gain_loss.as_tuple().exponent >= -4
        assert len(str(summary.total_return_rate).replace('.', '').replace('-', '')) <= 8

    async def test_purchase_insufficient_balance(self, investment_service, test_user, test_account, test_product):
        """Test purchase with insufficient account balance."""
        # Arrange
        purchase_request = InvestmentPurchaseRequest(
            account_id=test_account["id"],
            product_id=test_product["id"],
            amount=Decimal("15000.00")  # More than account balance
        )
        
        # Act & Assert
        with pytest.raises(ValidationError, match="insufficient"):
            await investment_service.purchase_investment(
                user_id=test_user["id"],
                purchase_request=purchase_request
            )

    async def test_purchase_nonexistent_product(self, investment_service, test_user, test_account):
        """Test purchase with non-existent product."""
        # Arrange
        purchase_request = InvestmentPurchaseRequest(
            account_id=test_account["id"],
            product_id=uuid4(),  # Non-existent product
            amount=Decimal("1000.00")
        )
        
        # Act & Assert
        with pytest.raises(NotFoundError, match="not found"):
            await investment_service.purchase_investment(
                user_id=test_user["id"],
                purchase_request=purchase_request
            )

    async def test_purchase_nonexistent_account(self, investment_service, test_user, test_product):
        """Test purchase with non-existent account."""
        # Arrange
        purchase_request = InvestmentPurchaseRequest(
            account_id=uuid4(),  # Non-existent account
            product_id=test_product["id"],
            amount=Decimal("1000.00")
        )
        
        # Act & Assert
        with pytest.raises(NotFoundError, match="not found"):
            await investment_service.purchase_investment(
                user_id=test_user["id"],
                purchase_request=purchase_request
            )
