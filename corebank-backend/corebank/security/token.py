"""
JWT token management for CoreBank.

This module provides JWT token creation, validation, and management
for user authentication and authorization.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from uuid import UUID

from jose import JWTError, jwt
from pydantic import ValidationError

from corebank.core.config import settings
from corebank.models.common import TokenData

logger = logging.getLogger(__name__)


class TokenManager:
    """
    JWT token management utility class.
    
    This class provides methods for creating, validating, and managing
    JWT tokens for user authentication.
    """
    
    def __init__(self) -> None:
        """Initialize token manager with configuration."""
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def create_access_token(
        self, 
        data: dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Custom expiration time (optional)
            
        Returns:
            str: Encoded JWT token
            
        Raises:
            RuntimeError: If token creation fails
        """
        to_encode = data.copy()
        
        # Set expiration time
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.access_token_expire_minutes
            )
        
        # Add standard claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access_token"
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.debug("Access token created successfully")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise RuntimeError("Token creation failed")
    
    def create_user_token(
        self, 
        user_id: UUID, 
        username: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create an access token for a user.
        
        Args:
            user_id: User ID
            username: Username
            expires_delta: Custom expiration time (optional)
            
        Returns:
            str: Encoded JWT token
        """
        token_data = {
            "sub": str(user_id),  # Subject (user ID)
            "username": username,
            "user_id": str(user_id)
        }
        
        return self.create_access_token(token_data, expires_delta)
    
    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Optional[dict]: Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Verify token type
            if payload.get("type") != "access_token":
                logger.warning("Invalid token type")
                return None
            
            # Verify expiration
            exp = payload.get("exp")
            if exp is None:
                logger.warning("Token missing expiration")
                return None
            
            if datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                logger.debug("Token has expired")
                return None
            
            logger.debug("Token verified successfully")
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def get_token_data(self, token: str) -> Optional[TokenData]:
        """
        Extract token data from a JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Optional[TokenData]: Token data if valid, None otherwise
        """
        payload = self.verify_token(token)
        if payload is None:
            return None
        
        try:
            username = payload.get("username")
            user_id = payload.get("user_id")
            
            return TokenData(username=username, user_id=user_id)
            
        except ValidationError as e:
            logger.warning(f"Invalid token data: {e}")
            return None
    
    def get_user_id_from_token(self, token: str) -> Optional[UUID]:
        """
        Extract user ID from a JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Optional[UUID]: User ID if valid, None otherwise
        """
        token_data = self.get_token_data(token)
        if token_data and token_data.user_id:
            try:
                return UUID(token_data.user_id)
            except ValueError:
                logger.warning("Invalid user ID format in token")
                return None
        return None
    
    def is_token_expired(self, token: str) -> bool:
        """
        Check if a token is expired without full verification.
        
        Args:
            token: JWT token
            
        Returns:
            bool: True if token is expired, False otherwise
        """
        try:
            # Decode without verification to check expiration
            payload = jwt.decode(
                token, 
                options={"verify_signature": False, "verify_exp": False}
            )
            
            exp = payload.get("exp")
            if exp is None:
                return True
            
            return datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc)
            
        except Exception:
            return True
    
    def refresh_token(self, token: str) -> Optional[str]:
        """
        Refresh an access token if it's still valid.
        
        Args:
            token: Current JWT token
            
        Returns:
            Optional[str]: New token if refresh successful, None otherwise
        """
        payload = self.verify_token(token)
        if payload is None:
            return None
        
        # Extract user data
        user_id = payload.get("user_id")
        username = payload.get("username")
        
        if not user_id or not username:
            logger.warning("Missing user data in token for refresh")
            return None
        
        try:
            # Create new token with same user data
            return self.create_user_token(UUID(user_id), username)
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None
    
    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """
        Get the expiration time of a token.
        
        Args:
            token: JWT token
            
        Returns:
            Optional[datetime]: Expiration time if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token, 
                options={"verify_signature": False, "verify_exp": False}
            )
            
            exp = payload.get("exp")
            if exp is None:
                return None
            
            return datetime.fromtimestamp(exp, tz=timezone.utc)
            
        except Exception:
            return None


# Global token manager instance
token_manager = TokenManager()


# Convenience functions for direct use
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create an access token. Convenience function."""
    return token_manager.create_access_token(data, expires_delta)


def create_user_token(
    user_id: UUID, 
    username: str, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a user token. Convenience function."""
    return token_manager.create_user_token(user_id, username, expires_delta)


def verify_token(token: str) -> Optional[dict]:
    """Verify a token. Convenience function."""
    return token_manager.verify_token(token)


def get_token_data(token: str) -> Optional[TokenData]:
    """Get token data. Convenience function."""
    return token_manager.get_token_data(token)


def get_user_id_from_token(token: str) -> Optional[UUID]:
    """Get user ID from token. Convenience function."""
    return token_manager.get_user_id_from_token(token)
