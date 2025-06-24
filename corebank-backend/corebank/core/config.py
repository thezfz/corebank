"""
Configuration management for CoreBank.

This module provides centralized configuration loading using Pydantic Settings.
All configuration values are loaded from environment variables or .env files.

The configuration is structured into logical groups for better organization
and includes validation to ensure all required values are present.
"""

import os
from typing import Optional

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    # PostgreSQL connection parameters
    postgres_user: str = Field(default="corebank_user", description="PostgreSQL username")
    postgres_password: str = Field(description="PostgreSQL password")
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_db: str = Field(default="corebank", description="PostgreSQL database name")
    
    # Connection pool settings
    pool_min_size: int = Field(default=5, description="Minimum connection pool size")
    pool_max_size: int = Field(default=20, description="Maximum connection pool size")
    pool_timeout: float = Field(default=30.0, description="Connection pool timeout in seconds")
    
    @property
    def database_url(self) -> str:
        """Construct the database URL from individual components."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    secret_key: str = Field(description="Secret key for JWT token signing")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, 
        description="Access token expiration time in minutes"
    )
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate that the secret key is sufficiently long."""
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v


class APISettings(BaseSettings):
    """API server configuration settings."""
    
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    reload: bool = Field(default=False, description="Enable auto-reload for development")
    debug: bool = Field(default=False, description="Enable debug mode")


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        description="Log message format"
    )
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application metadata
    app_name: str = Field(default="CoreBank", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: str = Field(default="development", description="Environment name")

    # Database settings (flattened)
    postgres_user: str = Field(default="corebank_user", description="PostgreSQL username")
    postgres_password: str = Field(description="PostgreSQL password")
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_db: str = Field(default="corebank", description="PostgreSQL database name")
    pool_min_size: int = Field(default=5, description="Minimum connection pool size")
    pool_max_size: int = Field(default=20, description="Maximum connection pool size")
    pool_timeout: float = Field(default=30.0, description="Connection pool timeout in seconds")

    # Security settings (flattened)
    secret_key: str = Field(description="Secret key for JWT token signing")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration time in minutes")

    # API settings (flattened)
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    reload: bool = Field(default=False, description="Enable auto-reload for development")
    debug: bool = Field(default=False, description="Enable debug mode")

    # Logging settings (flattened)
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        description="Log message format"
    )
    log_file: Optional[str] = Field(default=None, description="Log file path")

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate that the secret key is sufficiently long."""
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    @property
    def database_url(self) -> str:
        """Construct the database URL from individual components."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment.lower() == "testing"


# Global settings instance
# This will be imported and used throughout the application
settings = Settings()


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    This function can be used as a FastAPI dependency to inject
    settings into endpoint functions.
    
    Returns:
        Settings: The global settings instance
    """
    return settings
