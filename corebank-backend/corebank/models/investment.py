"""
Investment-related Pydantic models for CoreBank API.

This module defines all the request/response models for investment
and wealth management functionality.
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


class ProductType(str, Enum):
    """Investment product types."""
    MONEY_FUND = "money_fund"
    FIXED_TERM = "fixed_term"
    MUTUAL_FUND = "mutual_fund"
    INSURANCE = "insurance"


class RiskLevel(int, Enum):
    """Risk levels for investment products."""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


class InvestmentExperience(str, Enum):
    """Investment experience levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class InvestmentGoal(str, Enum):
    """Investment goals."""
    WEALTH_PRESERVATION = "wealth_preservation"
    STEADY_GROWTH = "steady_growth"
    AGGRESSIVE_GROWTH = "aggressive_growth"


class InvestmentHorizon(str, Enum):
    """Investment time horizons."""
    SHORT_TERM = "short_term"    # < 1 year
    MEDIUM_TERM = "medium_term"  # 1-5 years
    LONG_TERM = "long_term"      # > 5 years


class TransactionType(str, Enum):
    """Investment transaction types."""
    PURCHASE = "purchase"
    REDEMPTION = "redemption"
    DIVIDEND = "dividend"
    INTEREST = "interest"


class TransactionStatus(str, Enum):
    """Investment transaction status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HoldingStatus(str, Enum):
    """Investment holding status."""
    ACTIVE = "active"
    MATURED = "matured"
    REDEEMED = "redeemed"


# Base models
class InvestmentProductBase(BaseModel):
    """Base model for investment products."""
    
    product_code: str = Field(..., max_length=50, description="Product code")
    name: str = Field(..., max_length=200, description="Product name")
    product_type: ProductType = Field(..., description="Product type")
    risk_level: RiskLevel = Field(..., description="Risk level (1-5)")
    expected_return_rate: Optional[Decimal] = Field(
        None, 
        max_digits=5, 
        decimal_places=4,
        description="Expected annual return rate"
    )
    min_investment_amount: Decimal = Field(
        default=Decimal("1.00"),
        max_digits=19,
        decimal_places=4,
        description="Minimum investment amount"
    )
    max_investment_amount: Optional[Decimal] = Field(
        None,
        max_digits=19,
        decimal_places=4,
        description="Maximum investment amount"
    )
    investment_period_days: Optional[int] = Field(
        None, 
        description="Investment period in days (NULL for demand products)"
    )
    description: Optional[str] = Field(None, description="Product description")
    features: Optional[Dict[str, Any]] = Field(None, description="Product features")


class InvestmentProductCreate(InvestmentProductBase):
    """Model for creating investment products."""
    pass


class InvestmentProductUpdate(BaseModel):
    """Model for updating investment products."""
    
    name: Optional[str] = Field(None, max_length=200)
    expected_return_rate: Optional[Decimal] = Field(None, max_digits=5, decimal_places=4)
    min_investment_amount: Optional[Decimal] = Field(None, max_digits=19, decimal_places=4)
    max_investment_amount: Optional[Decimal] = Field(None, max_digits=19, decimal_places=4)
    is_active: Optional[bool] = None
    description: Optional[str] = None
    features: Optional[Dict[str, Any]] = None


class InvestmentProductResponse(InvestmentProductBase):
    """Model for investment product responses."""

    id: UUID = Field(..., description="Product unique identifier")
    is_active: bool = Field(..., description="Whether product is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }


# Risk Assessment models
class RiskAssessmentCreate(BaseModel):
    """Model for creating risk assessments."""
    
    risk_tolerance: RiskLevel = Field(..., description="Risk tolerance level")
    investment_experience: InvestmentExperience = Field(..., description="Investment experience")
    investment_goal: InvestmentGoal = Field(..., description="Investment goal")
    investment_horizon: InvestmentHorizon = Field(..., description="Investment time horizon")
    monthly_income_range: Optional[str] = Field(None, description="Monthly income range")
    assessment_data: Optional[Dict[str, Any]] = Field(None, description="Detailed assessment data")


class RiskAssessmentResponse(RiskAssessmentCreate):
    """Model for risk assessment responses."""
    
    id: UUID = Field(..., description="Assessment unique identifier")
    user_id: UUID = Field(..., description="User ID")
    assessment_score: int = Field(..., description="Calculated assessment score")
    expires_at: datetime = Field(..., description="Assessment expiration date")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


# Investment Transaction models
class InvestmentPurchaseRequest(BaseModel):
    """Model for investment purchase requests."""
    
    account_id: UUID = Field(..., description="Source account ID")
    product_id: UUID = Field(..., description="Investment product ID")
    amount: Decimal = Field(
        ...,
        gt=0,
        max_digits=19,
        decimal_places=4,
        description="Investment amount"
    )
    
    @validator('amount')
    def validate_amount(cls, v):
        """Validate investment amount."""
        if v <= 0:
            raise ValueError('Investment amount must be positive')
        return v


class InvestmentRedemptionRequest(BaseModel):
    """Model for investment redemption requests."""
    
    holding_id: UUID = Field(..., description="Investment holding ID")
    shares: Optional[Decimal] = Field(
        None,
        gt=0,
        max_digits=19,
        decimal_places=8,
        description="Shares to redeem (NULL for full redemption)"
    )
    
    @validator('shares')
    def validate_shares(cls, v):
        """Validate redemption shares."""
        if v is not None and v <= 0:
            raise ValueError('Redemption shares must be positive')
        return v


class InvestmentTransactionResponse(BaseModel):
    """Model for investment transaction responses."""
    
    id: UUID = Field(..., description="Transaction unique identifier")
    user_id: UUID = Field(..., description="User ID")
    account_id: UUID = Field(..., description="Account ID")
    product_id: UUID = Field(..., description="Product ID")
    holding_id: Optional[UUID] = Field(None, description="Holding ID")
    transaction_type: TransactionType = Field(..., description="Transaction type")
    shares: Decimal = Field(..., max_digits=19, decimal_places=8, description="Transaction shares")
    unit_price: Decimal = Field(..., max_digits=19, decimal_places=4, description="Unit price")
    amount: Decimal = Field(..., max_digits=19, decimal_places=4, description="Transaction amount")
    fee: Decimal = Field(..., max_digits=19, decimal_places=4, description="Transaction fee")
    net_amount: Decimal = Field(..., max_digits=19, decimal_places=4, description="Net amount")
    status: TransactionStatus = Field(..., description="Transaction status")
    settlement_date: Optional[datetime] = Field(None, description="Settlement date")
    description: Optional[str] = Field(None, description="Transaction description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }


# Investment Holding models
class InvestmentHoldingResponse(BaseModel):
    """Model for investment holding responses."""
    
    id: UUID = Field(..., description="Holding unique identifier")
    user_id: UUID = Field(..., description="User ID")
    account_id: UUID = Field(..., description="Account ID")
    product_id: UUID = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    product_type: ProductType = Field(..., description="Product type")
    shares: Decimal = Field(..., max_digits=19, decimal_places=8, description="Holding shares")
    average_cost: Decimal = Field(..., max_digits=19, decimal_places=4, description="Average cost")
    total_invested: Decimal = Field(..., max_digits=19, decimal_places=4, description="Total invested")
    current_value: Decimal = Field(..., max_digits=19, decimal_places=4, description="Current value")
    unrealized_gain_loss: Decimal = Field(..., max_digits=19, decimal_places=4, description="Unrealized P&L")
    realized_gain_loss: Decimal = Field(..., max_digits=19, decimal_places=4, description="Realized P&L")
    return_rate: Decimal = Field(..., max_digits=8, decimal_places=4, description="Return rate")
    purchase_date: datetime = Field(..., description="Purchase date")
    maturity_date: Optional[datetime] = Field(None, description="Maturity date")
    status: HoldingStatus = Field(..., description="Holding status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }


# Portfolio Summary models
class PortfolioSummaryResponse(BaseModel):
    """Model for portfolio summary responses."""
    
    total_assets: Decimal = Field(..., max_digits=19, decimal_places=4, description="Total assets")
    total_invested: Decimal = Field(..., max_digits=19, decimal_places=4, description="Total invested")
    total_gain_loss: Decimal = Field(..., max_digits=19, decimal_places=4, description="Total P&L")
    total_return_rate: Decimal = Field(..., max_digits=8, decimal_places=4, description="Total return rate")
    asset_allocation: Dict[ProductType, Decimal] = Field(..., description="Asset allocation by type")
    holdings_count: int = Field(..., description="Number of holdings")
    active_products_count: int = Field(..., description="Number of active products")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }


# Product NAV models
class ProductNAVResponse(BaseModel):
    """Model for product NAV responses."""
    
    id: UUID = Field(..., description="NAV record unique identifier")
    product_id: UUID = Field(..., description="Product ID")
    nav_date: date = Field(..., description="NAV date")
    unit_nav: Decimal = Field(..., max_digits=19, decimal_places=4, description="Unit NAV")
    accumulated_nav: Optional[Decimal] = Field(None, max_digits=19, decimal_places=4, description="Accumulated NAV")
    daily_return_rate: Optional[Decimal] = Field(None, max_digits=8, decimal_places=6, description="Daily return rate")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }


# Product Recommendation models
class ProductRecommendationResponse(BaseModel):
    """Model for product recommendation responses."""
    
    product: InvestmentProductResponse = Field(..., description="Recommended product")
    recommendation_score: float = Field(..., description="Recommendation score (0-1)")
    recommendation_reason: str = Field(..., description="Recommendation reason")
    risk_match: bool = Field(..., description="Whether risk level matches user profile")
    suggested_allocation: Optional[Decimal] = Field(None, description="Suggested allocation percentage")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }
