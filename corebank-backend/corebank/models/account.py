"""
Account API models for CoreBank.

This module defines Pydantic models for account-related API requests and responses.
These models are used for request validation and response serialization.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class AccountType(str, Enum):
    """Enumeration of supported account types."""
    
    CHECKING = "checking"
    SAVINGS = "savings"


class AccountBase(BaseModel):
    """Base account model with common fields."""
    
    account_type: AccountType = Field(
        ...,
        description="Type of account (checking or savings)"
    )


class AccountCreate(AccountBase):
    """Model for account creation requests."""
    
    initial_deposit: Optional[Decimal] = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        max_digits=19,
        decimal_places=4,
        description="Initial deposit amount (optional, defaults to 0.00)"
    )
    
    @field_validator("initial_deposit")
    @classmethod
    def validate_initial_deposit(cls, v: Optional[Decimal]) -> Decimal:
        """Validate initial deposit amount."""
        if v is None:
            return Decimal("0.00")
        if v < 0:
            raise ValueError("Initial deposit cannot be negative")
        return v


class AccountResponse(AccountBase):
    """Model for account response data."""
    
    id: UUID = Field(..., description="Account unique identifier")
    account_number: str = Field(..., description="Account number")
    user_id: UUID = Field(..., description="Owner user ID")
    balance: Decimal = Field(
        ...,
        max_digits=19,
        decimal_places=4,
        description="Current account balance"
    )
    created_at: datetime = Field(..., description="Account creation timestamp")
    username: Optional[str] = Field(None, description="Account owner username")
    real_name: Optional[str] = Field(None, description="Account owner real name")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class AccountUpdate(BaseModel):
    """Model for account update requests."""
    
    account_type: Optional[AccountType] = Field(
        None,
        description="New account type (optional)"
    )


class AccountBalance(BaseModel):
    """Model for account balance response."""
    
    account_id: UUID = Field(..., description="Account unique identifier")
    account_number: str = Field(..., description="Account number")
    balance: Decimal = Field(
        ...,
        max_digits=19,
        decimal_places=4,
        description="Current account balance"
    )
    account_type: AccountType = Field(..., description="Account type")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class AccountSummary(BaseModel):
    """Model for account summary response."""

    total_accounts: int = Field(..., description="Total number of accounts")
    total_balance: Decimal = Field(
        ...,
        max_digits=19,
        decimal_places=4,
        description="Total balance across all accounts"
    )
    accounts_by_type: dict[AccountType, int] = Field(
        ...,
        description="Count of accounts by type"
    )

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class AccountLookupResponse(BaseModel):
    """Model for account lookup response (for transfer purposes)."""

    account_id: UUID = Field(..., description="Account unique identifier")
    account_number: str = Field(..., description="Account number")
    account_type: AccountType = Field(..., description="Account type")
    owner_name: Optional[str] = Field(None, description="Account owner name (if available)")

    class Config:
        """Pydantic configuration."""
        from_attributes = True
