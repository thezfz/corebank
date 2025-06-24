"""
Password security utilities for CoreBank.

This module provides secure password hashing and verification using bcrypt.
All password operations should use these utilities to ensure consistent
and secure password handling across the application.
"""

import logging
from typing import Union

from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Configure password context with bcrypt
# Using bcrypt with a reasonable number of rounds for security vs performance
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Good balance between security and performance
)


class PasswordManager:
    """
    Password management utility class.
    
    This class provides methods for hashing passwords and verifying
    password hashes using bcrypt with secure defaults.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            str: Hashed password
            
        Raises:
            ValueError: If password is empty or invalid
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if len(password) > 128:
            raise ValueError("Password cannot be longer than 128 characters")
        
        try:
            hashed = pwd_context.hash(password)
            logger.debug("Password hashed successfully")
            return hashed
        except Exception as e:
            logger.error(f"Failed to hash password: {e}")
            raise RuntimeError("Password hashing failed")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored password hash
            
        Returns:
            bool: True if password matches, False otherwise
        """
        if not plain_password or not hashed_password:
            return False
        
        try:
            is_valid = pwd_context.verify(plain_password, hashed_password)
            if is_valid:
                logger.debug("Password verification successful")
            else:
                logger.debug("Password verification failed")
            return is_valid
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def needs_update(hashed_password: str) -> bool:
        """
        Check if a password hash needs to be updated.
        
        This can happen when the hashing algorithm or parameters change.
        
        Args:
            hashed_password: Stored password hash
            
        Returns:
            bool: True if hash needs updating, False otherwise
        """
        if not hashed_password:
            return True
        
        try:
            return pwd_context.needs_update(hashed_password)
        except Exception as e:
            logger.error(f"Error checking if password needs update: {e}")
            return True
    
    @staticmethod
    def validate_password_strength(password: str) -> dict[str, Union[bool, list[str]]]:
        """
        Validate password strength according to security requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            dict: Validation result with is_valid flag and list of issues
        """
        issues = []
        
        # Length check
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        
        if len(password) > 128:
            issues.append("Password cannot be longer than 128 characters")
        
        # Character type checks
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one digit")
        
        # Special character check (optional but recommended)
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            issues.append("Password should contain at least one special character")
        
        # Common password patterns (basic check)
        common_patterns = [
            "password", "123456", "qwerty", "abc123", "admin", "user",
            "login", "welcome", "monkey", "dragon"
        ]
        
        password_lower = password.lower()
        for pattern in common_patterns:
            if pattern in password_lower:
                issues.append(f"Password contains common pattern: {pattern}")
                break
        
        # Sequential characters check
        if _has_sequential_chars(password):
            issues.append("Password should not contain sequential characters")
        
        # Repeated characters check
        if _has_repeated_chars(password):
            issues.append("Password should not contain too many repeated characters")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }


def _has_sequential_chars(password: str, min_length: int = 3) -> bool:
    """
    Check if password contains sequential characters.
    
    Args:
        password: Password to check
        min_length: Minimum length of sequential characters to flag
        
    Returns:
        bool: True if sequential characters found
    """
    password_lower = password.lower()
    
    for i in range(len(password_lower) - min_length + 1):
        # Check for ascending sequences
        is_ascending = True
        for j in range(min_length - 1):
            if ord(password_lower[i + j + 1]) != ord(password_lower[i + j]) + 1:
                is_ascending = False
                break
        
        if is_ascending:
            return True
        
        # Check for descending sequences
        is_descending = True
        for j in range(min_length - 1):
            if ord(password_lower[i + j + 1]) != ord(password_lower[i + j]) - 1:
                is_descending = False
                break
        
        if is_descending:
            return True
    
    return False


def _has_repeated_chars(password: str, max_repeats: int = 3) -> bool:
    """
    Check if password has too many repeated characters.
    
    Args:
        password: Password to check
        max_repeats: Maximum allowed consecutive repeated characters
        
    Returns:
        bool: True if too many repeated characters found
    """
    count = 1
    for i in range(1, len(password)):
        if password[i] == password[i - 1]:
            count += 1
            if count > max_repeats:
                return True
        else:
            count = 1
    
    return False


# Convenience functions for direct use
def hash_password(password: str) -> str:
    """Hash a password. Convenience function."""
    return PasswordManager.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password. Convenience function."""
    return PasswordManager.verify_password(plain_password, hashed_password)


def validate_password_strength(password: str) -> dict[str, Union[bool, list[str]]]:
    """Validate password strength. Convenience function."""
    return PasswordManager.validate_password_strength(password)
