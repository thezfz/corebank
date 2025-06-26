"""
User API models for CoreBank.

This module defines Pydantic models for user-related API requests and responses.
These models are used for request validation and response serialization.
"""

from datetime import datetime, date
from typing import Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class UserRole(str, Enum):
    """User role enumeration."""
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Base user model with common fields."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username (3-50 characters, alphanumeric, underscore, hyphen only)"
    )


class UserCreate(UserBase):
    """Model for user creation requests."""
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (8-128 characters)"
    )
    
    # Password validation is now handled in the endpoint to avoid JSON serialization issues


class UserLogin(BaseModel):
    """Model for user login requests."""
    
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class UserResponse(UserBase):
    """Model for user response data."""

    id: UUID = Field(..., description="User unique identifier")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    created_at: datetime = Field(..., description="User creation timestamp")
    is_active: bool = Field(default=True, description="User active status")
    deleted_at: Optional[datetime] = Field(None, description="User deletion timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class UserUpdate(BaseModel):
    """Model for user update requests."""
    
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="New username (optional)"
    )


class PasswordChange(BaseModel):
    """Model for password change requests."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password (8-128 characters)"
    )

    # Password validation is now handled in the endpoint to avoid JSON serialization issues


class UserProfile(BaseModel):
    """Model for user profile information."""

    real_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    english_name: Optional[str] = Field(None, max_length=100, description="英文/拼音姓名")
    id_type: Optional[str] = Field(None, max_length=50, description="证件类型")
    id_number: Optional[str] = Field(None, max_length=50, description="证件号码")
    country: Optional[str] = Field(None, max_length=50, description="国家/地区")
    ethnicity: Optional[str] = Field(None, max_length=50, description="民族")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    birth_date: Optional[date] = Field(None, description="出生日期")
    birth_place: Optional[str] = Field(None, max_length=200, description="出生地")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
    email: Optional[str] = Field(None, max_length=100, description="邮箱地址")
    address: Optional[str] = Field(None, max_length=500, description="联系地址")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Invalid phone number format')
        return v


class UserProfileUpdate(UserProfile):
    """Model for user profile update requests."""
    pass


class UserDetailResponse(UserResponse):
    """Model for detailed user response including profile."""

    real_name: Optional[str] = Field(None, description="真实姓名")
    english_name: Optional[str] = Field(None, description="英文/拼音姓名")
    id_type: Optional[str] = Field(None, description="证件类型")
    id_number: Optional[str] = Field(None, description="证件号码")
    country: Optional[str] = Field(None, description="国家/地区")
    ethnicity: Optional[str] = Field(None, description="民族")
    gender: Optional[str] = Field(None, description="性别")
    birth_date: Optional[date] = Field(None, description="出生日期")
    birth_place: Optional[str] = Field(None, description="出生地")
    phone: Optional[str] = Field(None, description="手机号码")
    email: Optional[str] = Field(None, description="邮箱地址")
    address: Optional[str] = Field(None, description="联系地址")

    # Additional fields for admin view
    account_count: Optional[int] = Field(None, description="账户数量")
    total_balance: Optional[str] = Field(None, description="总余额")
    investment_count: Optional[int] = Field(None, description="投资产品数量")




class UserSoftDelete(BaseModel):
    """Model for user soft delete requests."""

    reason: str = Field(..., max_length=500, description="Deletion reason")


class UserRestore(BaseModel):
    """Model for user restore requests."""

    reason: str = Field(..., max_length=500, description="Restoration reason")
    profile_created_at: Optional[datetime] = Field(None, description="Profile creation timestamp")
    profile_updated_at: Optional[datetime] = Field(None, description="Profile last update timestamp")

    class Config:
        """Pydantic configuration."""
        from_attributes = True
