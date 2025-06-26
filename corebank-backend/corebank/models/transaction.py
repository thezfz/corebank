"""
Transaction API models for CoreBank.

This module defines Pydantic models for transaction-related API requests and responses.
These models are used for request validation and response serialization.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TransactionType(str, Enum):
    """Enumeration of supported transaction types."""

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    INVESTMENT_PURCHASE = "理财申购"
    INVESTMENT_REDEMPTION = "理财赎回"


class TransactionStatus(str, Enum):
    """Enumeration of transaction statuses."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EntryType(str, Enum):
    """Enumeration of double-entry bookkeeping entry types."""

    DEBIT = "debit"   # 借方
    CREDIT = "credit" # 贷方


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


class TransferByAccountNumberRequest(TransactionBase):
    """Model for transfer transaction requests using account numbers."""

    from_account_id: UUID = Field(..., description="Source account ID")
    to_account_number: str = Field(..., description="Target account number")
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional transaction description"
    )


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


class EnhancedTransactionResponse(TransactionBase):
    """Enhanced model for transaction response data with related user info."""

    id: UUID = Field(..., description="Transaction unique identifier")
    account_id: UUID = Field(..., description="Primary account ID")
    account_number: str = Field(..., description="Primary account number")
    transaction_type: TransactionType = Field(..., description="Transaction type")
    status: TransactionStatus = Field(..., description="Transaction status")
    related_account_id: Optional[UUID] = Field(
        None,
        description="Related account ID (for transfers)"
    )
    related_account_number: Optional[str] = Field(
        None,
        description="Related account number (for transfers)"
    )
    related_user_name: Optional[str] = Field(
        None,
        description="Related user's real name (surname only for privacy)"
    )
    related_user_phone: Optional[str] = Field(
        None,
        description="Related user's phone (masked for privacy)"
    )
    description: Optional[str] = Field(
        None,
        description="Transaction description"
    )
    timestamp: datetime = Field(..., description="Transaction timestamp")
    is_outgoing: Optional[bool] = Field(
        None,
        description="Whether this is an outgoing transaction for the current user"
    )

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


# Double-Entry Bookkeeping Models

class TransactionGroupResponse(BaseModel):
    """Response model for transaction group data."""

    id: UUID = Field(..., description="Transaction group unique identifier")
    group_type: str = Field(..., description="Transaction group type")
    description: Optional[str] = Field(None, description="Transaction group description")
    total_amount: Decimal = Field(
        ...,
        max_digits=19,
        decimal_places=4,
        description="Total transaction amount"
    )
    status: TransactionStatus = Field(..., description="Transaction group status")
    reference_id: Optional[UUID] = Field(
        None,
        description="Reference to original transaction (for migration)"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class TransactionEntryResponse(BaseModel):
    """Response model for transaction entry data."""

    id: UUID = Field(..., description="Transaction entry unique identifier")
    transaction_group_id: UUID = Field(..., description="Parent transaction group ID")
    account_id: UUID = Field(..., description="Account ID")
    entry_type: EntryType = Field(..., description="Entry type (debit/credit)")
    amount: Decimal = Field(
        ...,
        max_digits=19,
        decimal_places=4,
        description="Entry amount"
    )
    balance_after: Optional[Decimal] = Field(
        None,
        max_digits=19,
        decimal_places=4,
        description="Account balance after this entry"
    )
    description: Optional[str] = Field(None, description="Entry description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class DoubleEntryTransactionResponse(BaseModel):
    """Response model for complete double-entry transaction."""

    transaction_group: TransactionGroupResponse = Field(
        ...,
        description="Transaction group information"
    )
    entries: List[TransactionEntryResponse] = Field(
        ...,
        description="List of transaction entries"
    )

    class Config:
        """Pydantic configuration."""
        from_attributes = True
