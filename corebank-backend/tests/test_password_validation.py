"""
Tests for password validation functionality.

This module tests the password strength validation logic to ensure
proper security requirements are enforced.
"""

import pytest
from corebank.security.password import validate_password_strength, PasswordManager


class TestPasswordValidation:
    """Test password validation functionality."""

    def test_valid_strong_password(self):
        """Test that a strong password passes validation."""
        password = "MySecure123!"
        result = validate_password_strength(password)
        
        assert result["is_valid"] is True
        assert len(result["issues"]) == 0

    def test_password_too_short(self):
        """Test that passwords shorter than 8 characters are rejected."""
        password = "Short1!"
        result = validate_password_strength(password)
        
        assert result["is_valid"] is False
        assert "Password must be at least 8 characters long" in result["issues"]

    def test_password_too_long(self):
        """Test that passwords longer than 128 characters are rejected."""
        password = "A" * 129 + "1!"
        result = validate_password_strength(password)
        
        assert result["is_valid"] is False
        assert "Password cannot be longer than 128 characters" in result["issues"]

    def test_password_missing_uppercase(self):
        """Test that passwords without uppercase letters are rejected."""
        password = "mysecure123!"
        result = validate_password_strength(password)
        
        assert result["is_valid"] is False
        assert "Password must contain at least one uppercase letter" in result["issues"]

    def test_password_missing_lowercase(self):
        """Test that passwords without lowercase letters are rejected."""
        password = "MYSECURE123!"
        result = validate_password_strength(password)
        
        assert result["is_valid"] is False
        assert "Password must contain at least one lowercase letter" in result["issues"]

    def test_password_missing_digit(self):
        """Test that passwords without digits are rejected."""
        password = "MySecurePass!"
        result = validate_password_strength(password)
        
        assert result["is_valid"] is False
        assert "Password must contain at least one digit" in result["issues"]

    def test_password_missing_special_character(self):
        """Test that passwords without special characters get a warning."""
        password = "MySecure123"
        result = validate_password_strength(password)
        
        assert result["is_valid"] is False
        assert "Password should contain at least one special character" in result["issues"]

    def test_common_password_patterns(self):
        """Test that common password patterns are rejected."""
        common_passwords = ["password", "123456", "qwerty", "admin", "user"]
        
        for pwd in common_passwords:
            result = validate_password_strength(pwd)
            assert result["is_valid"] is False
            assert any("too common" in issue for issue in result["issues"])

    def test_sequential_characters(self):
        """Test that long sequential characters are rejected."""
        password = "MyPass1234!"  # Contains "1234" sequence
        result = validate_password_strength(password)
        
        assert result["is_valid"] is False
        assert "Password should not contain long sequential characters" in result["issues"]

    def test_repeated_characters(self):
        """Test that too many repeated characters are rejected."""
        password = "MyPassssss1!"  # Contains "ssss" repetition
        result = validate_password_strength(password)
        
        assert result["is_valid"] is False
        assert "Password should not contain too many repeated characters" in result["issues"]

    def test_multiple_validation_issues(self):
        """Test that multiple validation issues are reported."""
        password = "weak"  # Too short, no uppercase, no digit, no special char
        result = validate_password_strength(password)
        
        assert result["is_valid"] is False
        assert len(result["issues"]) >= 3
        assert "Password must be at least 8 characters long" in result["issues"]
        assert "Password must contain at least one uppercase letter" in result["issues"]
        assert "Password must contain at least one digit" in result["issues"]

    def test_edge_case_minimum_valid_password(self):
        """Test minimum valid password that meets all requirements."""
        password = "Aa1!xyzw"  # 8 chars, has upper, lower, digit, special, no sequences
        result = validate_password_strength(password)

        assert result["is_valid"] is True
        assert len(result["issues"]) == 0

    def test_password_with_allowed_repetition(self):
        """Test that passwords with allowed repetition pass."""
        password = "MyPass11!"  # Only 2 repeated chars, should be OK
        result = validate_password_strength(password)
        
        assert result["is_valid"] is True
        assert len(result["issues"]) == 0

    def test_password_with_short_sequence(self):
        """Test that passwords with short sequences pass."""
        password = "MyPass12!"  # Only "12" sequence, should be OK
        result = validate_password_strength(password)
        
        assert result["is_valid"] is True
        assert len(result["issues"]) == 0


class TestPasswordManager:
    """Test PasswordManager class functionality."""

    def test_hash_password_success(self):
        """Test successful password hashing."""
        password = "MySecure123!"
        hashed = PasswordManager.hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are typically 60 chars

    def test_hash_password_empty(self):
        """Test that empty passwords raise ValueError."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            PasswordManager.hash_password("")

    def test_hash_password_too_short(self):
        """Test that short passwords raise ValueError."""
        with pytest.raises(ValueError, match="Password must be at least 8 characters long"):
            PasswordManager.hash_password("short")

    def test_hash_password_too_long(self):
        """Test that long passwords raise ValueError."""
        long_password = "A" * 129
        with pytest.raises(ValueError, match="Password cannot be longer than 128 characters"):
            PasswordManager.hash_password(long_password)

    def test_verify_password_success(self):
        """Test successful password verification."""
        password = "MySecure123!"
        hashed = PasswordManager.hash_password(password)
        
        assert PasswordManager.verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Test failed password verification."""
        password = "MySecure123!"
        wrong_password = "WrongPass123!"
        hashed = PasswordManager.hash_password(password)
        
        assert PasswordManager.verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_inputs(self):
        """Test password verification with empty inputs."""
        assert PasswordManager.verify_password("", "hash") is False
        assert PasswordManager.verify_password("password", "") is False
        assert PasswordManager.verify_password("", "") is False

    def test_needs_update(self):
        """Test password hash update checking."""
        password = "MySecure123!"
        hashed = PasswordManager.hash_password(password)
        
        # Fresh hash should not need update
        assert PasswordManager.needs_update(hashed) is False
        
        # Empty hash should need update
        assert PasswordManager.needs_update("") is True


class TestPasswordValidationIntegration:
    """Integration tests for password validation in API context."""

    def test_convenience_functions(self):
        """Test that convenience functions work correctly."""
        from corebank.security.password import hash_password, verify_password, validate_password_strength
        
        password = "MySecure123!"
        
        # Test validation
        validation = validate_password_strength(password)
        assert validation["is_valid"] is True
        
        # Test hashing
        hashed = hash_password(password)
        assert hashed is not None
        
        # Test verification
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_password_validation_consistency(self):
        """Test that validation is consistent across multiple calls."""
        password = "MySecure123!"
        
        result1 = validate_password_strength(password)
        result2 = validate_password_strength(password)
        
        assert result1["is_valid"] == result2["is_valid"]
        assert result1["issues"] == result2["issues"]

    def test_case_sensitivity_in_validation(self):
        """Test that password validation is case-sensitive where appropriate."""
        # These should be different validation results
        password_lower = "mysecure123!"
        password_upper = "MYSECURE123!"
        
        result_lower = validate_password_strength(password_lower)
        result_upper = validate_password_strength(password_upper)
        
        # Both should fail but for different reasons
        assert result_lower["is_valid"] is False
        assert result_upper["is_valid"] is False
        
        # Lower should miss uppercase
        assert "Password must contain at least one uppercase letter" in result_lower["issues"]
        # Upper should miss lowercase
        assert "Password must contain at least one lowercase letter" in result_upper["issues"]
