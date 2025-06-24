"""
Transaction API models for CoreBank.

This module defines Pydantic models for transaction-related API requests and responses.
These models are used for request validation and response serialization.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TransactionType(str, Enum):
    """Enumeration of supported transaction types."""
    
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"


class TransactionStatus(str, Enum):
    """Enumeration of transaction statuses."""
    
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TransactionBase(BaseModel):
    """Base transaction model with common fields."""
    
    amount: Decimal = Field(
        ...,
        gt=Decimal("0.00"),
        max_digits=19,
        decimal_places=4,
        description="Transaction amount (must be positive)"
    )
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate transaction amount."""
        if v <= 0:
            raise ValueError("Transaction amount must be positive")
        return v


class DepositRequest(TransactionBase):
    """Model for deposit transaction requests."""
    
    account_id: UUID = Field(..., description="Target account ID")
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional transaction description"
    )


class WithdrawalRequest(TransactionBase):
    """Model for withdrawal transaction requests."""
    
    account_id: UUID = Field(..., description="Source account ID")
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional transaction description"
    )


class TransferRequest(TransactionBase):
    """Model for transfer transaction requests."""
    
    from_account_id: UUID = Field(..., description="Source account ID")
    to_account_id: UUID = Field(..., description="Target account ID")
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional transaction description"
    )
    
    @field_validator("to_account_id")
    @classmethod
    def validate_different_accounts(cls, v: UUID, info) -> UUID:
        """Validate that source and target accounts are different."""
        if hasattr(info.data, 'from_account_id') and v == info.data['from_account_id']:
            raise ValueError("Source and target accounts must be different")
        return v


class TransactionResponse(TransactionBase):
    """Model for transaction response data."""
    
    id: UUID = Field(..., description="Transaction unique identifier")
    account_id: UUID = Field(..., description="Primary account ID")
    transaction_type: TransactionType = Field(..., description="Transaction type")
    status: TransactionStatus = Field(..., description="Transaction status")
    related_account_id: Optional[UUID] = Field(
        None,
        description="Related account ID (for transfers)"
    )
    description: Optional[str] = Field(
        None,
        description="Transaction description"
    )
    timestamp: datetime = Field(..., description="Transaction timestamp")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class TransactionHistory(BaseModel):
    """Model for transaction history response."""
    
    transactions: list[TransactionResponse] = Field(
        ...,
        description="List of transactions"
    )
    total_count: int = Field(..., description="Total number of transactions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of transactions per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class TransactionSummary(BaseModel):
    """Model for transaction summary response."""
    
    total_transactions: int = Field(..., description="Total number of transactions")
    total_deposits: Decimal = Field(
        ...,
        max_digits=19,
        decimal_places=4,
        description="Total deposit amount"
    )
    total_withdrawals: Decimal = Field(
        ...,
        max_digits=19,
        decimal_places=4,
        description="Total withdrawal amount"
    )
    total_transfers_in: Decimal = Field(
        ...,
        max_digits=19,
        decimal_places=4,
        description="Total incoming transfer amount"
    )
    total_transfers_out: Decimal = Field(
        ...,
        max_digits=19,
        decimal_places=4,
        description="Total outgoing transfer amount"
    )
    transactions_by_type: dict[TransactionType, int] = Field(
        ...,
        description="Count of transactions by type"
    )
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
