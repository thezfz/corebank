"""
Common API models for CoreBank.

This module defines common Pydantic models used across different API endpoints,
including authentication, error responses, and pagination models.
"""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field


# Generic type for data responses
T = TypeVar("T")


class Token(BaseModel):
    """Model for authentication token response."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenData(BaseModel):
    """Model for token payload data."""
    
    username: Optional[str] = Field(None, description="Username from token")
    user_id: Optional[str] = Field(None, description="User ID from token")


class ErrorDetail(BaseModel):
    """Model for error detail information."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused the error")


class ErrorResponse(BaseModel):
    """Model for error responses."""
    
    detail: str = Field(..., description="Error description")
    errors: Optional[list[ErrorDetail]] = Field(
        None,
        description="Detailed error information"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp"
    )


class SuccessResponse(BaseModel, Generic[T]):
    """Generic model for successful API responses."""
    
    success: bool = Field(default=True, description="Success indicator")
    data: T = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Success message")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )


class PaginationParams(BaseModel):
    """Model for pagination parameters."""
    
    page: int = Field(
        default=1,
        ge=1,
        description="Page number (starts from 1)"
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page (1-100)"
    )
    
    @property
    def offset(self) -> int:
        """Calculate the offset for database queries."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic model for paginated responses."""
    
    items: list[T] = Field(..., description="List of items")
    total_count: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    
    @classmethod
    def create(
        cls,
        items: list[T],
        total_count: int,
        pagination: PaginationParams
    ) -> "PaginatedResponse[T]":
        """
        Create a paginated response from items and pagination parameters.
        
        Args:
            items: List of items for current page
            total_count: Total number of items across all pages
            pagination: Pagination parameters
            
        Returns:
            PaginatedResponse: Paginated response object
        """
        total_pages = (total_count + pagination.page_size - 1) // pagination.page_size
        
        return cls(
            items=items,
            total_count=total_count,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_previous=pagination.page > 1,
        )


class HealthCheck(BaseModel):
    """Model for health check response."""
    
    status: str = Field(default="healthy", description="Service status")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp"
    )
    version: str = Field(..., description="Application version")
    database: str = Field(..., description="Database status")
    uptime: float = Field(..., description="Application uptime in seconds")


class MessageResponse(BaseModel):
    """Model for simple message responses."""
    
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )
