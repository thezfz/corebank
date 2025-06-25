"""
SQLAlchemy models for investment and wealth management.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean, DateTime, Date, 
    Text, JSON, ForeignKey, CheckConstraint, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from corebank.database.base import Base


class InvestmentProduct(Base):
    """Investment product model."""
    
    __tablename__ = "investment_products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    product_type = Column(String(50), nullable=False, index=True)  # money_fund, fixed_term, mutual_fund, insurance
    risk_level = Column(Integer, nullable=False, index=True)  # 1-5
    expected_return_rate = Column(Numeric(5, 4), nullable=True)  # Annual return rate
    min_investment_amount = Column(Numeric(19, 4), nullable=False, default=Decimal('1.00'))
    max_investment_amount = Column(Numeric(19, 4), nullable=True)
    investment_period_days = Column(Integer, nullable=True)  # NULL for demand products
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    description = Column(Text, nullable=True)
    features = Column(JSON, nullable=True)  # Product features as JSON
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('risk_level >= 1 AND risk_level <= 5', name='ck_risk_level'),
        CheckConstraint('min_investment_amount > 0', name='ck_min_investment_positive'),
        CheckConstraint('max_investment_amount IS NULL OR max_investment_amount >= min_investment_amount', 
                       name='ck_max_investment_valid'),
        CheckConstraint('investment_period_days IS NULL OR investment_period_days > 0', 
                       name='ck_investment_period_positive'),
        Index('idx_investment_products_type_risk', 'product_type', 'risk_level'),
        Index('idx_investment_products_active_type', 'is_active', 'product_type'),
    )
    
    # Relationships
    holdings = relationship("InvestmentHolding", back_populates="product")
    transactions = relationship("InvestmentTransaction", back_populates="product")
    nav_history = relationship("ProductNAVHistory", back_populates="product")


class UserRiskAssessment(Base):
    """User risk assessment model."""
    
    __tablename__ = "user_risk_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    risk_tolerance = Column(Integer, nullable=False)  # 1-5
    investment_experience = Column(String(50), nullable=False)  # beginner, intermediate, advanced
    investment_goal = Column(String(100), nullable=False)  # wealth_preservation, steady_growth, aggressive_growth
    investment_horizon = Column(String(50), nullable=False)  # short_term, medium_term, long_term
    monthly_income_range = Column(String(50), nullable=True)
    assessment_score = Column(Integer, nullable=False)
    assessment_data = Column(JSON, nullable=True)  # Detailed assessment data
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('risk_tolerance >= 1 AND risk_tolerance <= 5', name='ck_risk_tolerance'),
        CheckConstraint('assessment_score >= 0 AND assessment_score <= 100', name='ck_assessment_score'),
        UniqueConstraint('user_id', 'created_at', name='uq_user_assessment_date'),
        Index('idx_user_risk_assessments_expires', 'expires_at'),
        Index('idx_user_risk_assessments_user_expires', 'user_id', 'expires_at'),
    )
    
    # Relationships
    user = relationship("User", back_populates="risk_assessments")


class InvestmentHolding(Base):
    """Investment holding model."""
    
    __tablename__ = "investment_holdings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('investment_products.id'), nullable=False, index=True)
    shares = Column(Numeric(19, 8), nullable=False, default=Decimal('0'))  # Holding shares
    average_cost = Column(Numeric(19, 4), nullable=False)  # Average cost per share
    total_invested = Column(Numeric(19, 4), nullable=False, default=Decimal('0'))  # Total amount invested
    current_value = Column(Numeric(19, 4), nullable=False, default=Decimal('0'))  # Current market value
    unrealized_gain_loss = Column(Numeric(19, 4), nullable=False, default=Decimal('0'))  # Unrealized P&L
    realized_gain_loss = Column(Numeric(19, 4), nullable=False, default=Decimal('0'))  # Realized P&L
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    maturity_date = Column(DateTime(timezone=True), nullable=True)  # For fixed-term products
    status = Column(String(50), nullable=False, default='active', index=True)  # active, matured, redeemed
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('shares >= 0', name='ck_shares_non_negative'),
        CheckConstraint('average_cost > 0', name='ck_average_cost_positive'),
        CheckConstraint('total_invested >= 0', name='ck_total_invested_non_negative'),
        CheckConstraint('current_value >= 0', name='ck_current_value_non_negative'),
        UniqueConstraint('user_id', 'account_id', 'product_id', 'purchase_date', 
                        name='uq_user_account_product_purchase'),
        Index('idx_investment_holdings_user_status', 'user_id', 'status'),
        Index('idx_investment_holdings_product_status', 'product_id', 'status'),
        Index('idx_investment_holdings_maturity', 'maturity_date'),
    )
    
    # Relationships
    user = relationship("User", back_populates="investment_holdings")
    account = relationship("Account", back_populates="investment_holdings")
    product = relationship("InvestmentProduct", back_populates="holdings")
    transactions = relationship("InvestmentTransaction", back_populates="holding")


class InvestmentTransaction(Base):
    """Investment transaction model."""
    
    __tablename__ = "investment_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('investment_products.id'), nullable=False, index=True)
    holding_id = Column(UUID(as_uuid=True), ForeignKey('investment_holdings.id'), nullable=True, index=True)
    transaction_type = Column(String(50), nullable=False, index=True)  # purchase, redemption, dividend, interest
    shares = Column(Numeric(19, 8), nullable=False)  # Transaction shares
    unit_price = Column(Numeric(19, 4), nullable=False)  # Unit price at transaction
    amount = Column(Numeric(19, 4), nullable=False)  # Gross transaction amount
    fee = Column(Numeric(19, 4), nullable=False, default=Decimal('0'))  # Transaction fee
    net_amount = Column(Numeric(19, 4), nullable=False)  # Net amount after fees
    status = Column(String(50), nullable=False, default='pending', index=True)  # pending, confirmed, failed, cancelled
    settlement_date = Column(DateTime(timezone=True), nullable=True)  # Settlement date
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('shares != 0', name='ck_shares_not_zero'),
        CheckConstraint('unit_price > 0', name='ck_unit_price_positive'),
        CheckConstraint('amount > 0', name='ck_amount_positive'),
        CheckConstraint('fee >= 0', name='ck_fee_non_negative'),
        CheckConstraint('net_amount > 0', name='ck_net_amount_positive'),
        Index('idx_investment_transactions_user_type', 'user_id', 'transaction_type'),
        Index('idx_investment_transactions_product_type', 'product_id', 'transaction_type'),
        Index('idx_investment_transactions_status_date', 'status', 'created_at'),
        Index('idx_investment_transactions_settlement', 'settlement_date'),
    )
    
    # Relationships
    user = relationship("User", back_populates="investment_transactions")
    account = relationship("Account", back_populates="investment_transactions")
    product = relationship("InvestmentProduct", back_populates="transactions")
    holding = relationship("InvestmentHolding", back_populates="transactions")


class ProductNAVHistory(Base):
    """Product NAV (Net Asset Value) history model."""
    
    __tablename__ = "product_nav_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey('investment_products.id', ondelete='CASCADE'), 
                       nullable=False, index=True)
    nav_date = Column(Date, nullable=False, index=True)  # NAV date
    unit_nav = Column(Numeric(19, 4), nullable=False)  # Unit NAV
    accumulated_nav = Column(Numeric(19, 4), nullable=True)  # Accumulated NAV
    daily_return_rate = Column(Numeric(8, 6), nullable=True)  # Daily return rate
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('unit_nav > 0', name='ck_unit_nav_positive'),
        CheckConstraint('accumulated_nav IS NULL OR accumulated_nav > 0', name='ck_accumulated_nav_positive'),
        UniqueConstraint('product_id', 'nav_date', name='uq_product_nav_date'),
        Index('idx_product_nav_history_date', 'nav_date'),
        Index('idx_product_nav_history_product_date', 'product_id', 'nav_date'),
    )
    
    # Relationships
    product = relationship("InvestmentProduct", back_populates="nav_history")
