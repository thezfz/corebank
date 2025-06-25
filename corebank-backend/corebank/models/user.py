"""
User API models for CoreBank.

This module defines Pydantic models for user-related API requests and responses.
These models are used for request validation and response serialization.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


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
    created_at: datetime = Field(..., description="User creation timestamp")
    
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
