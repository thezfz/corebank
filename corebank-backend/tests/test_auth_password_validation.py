"""
Tests for authentication endpoints with password validation.

This module tests the API endpoints to ensure proper password validation
and error handling during user registration.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from corebank.main import create_application


@pytest.fixture
def client():
    """Create test client."""
    app = create_application()
    return TestClient(app)


@pytest.fixture
def mock_repository():
    """Create mock repository."""
    mock_repo = AsyncMock()
    mock_repo.get_user_by_username.return_value = None  # User doesn't exist
    mock_repo.create_user.return_value = {
        "id": "test-uuid",
        "username": "testuser",
        "created_at": "2024-01-01T00:00:00"
    }
    return mock_repo


class TestAuthPasswordValidation:
    """Test authentication endpoints with password validation."""

    @patch('corebank.api.v1.endpoints.auth.get_postgres_repository')
    def test_register_with_valid_password(self, mock_get_repo, client, mock_repository):
        """Test user registration with a valid strong password."""
        mock_get_repo.return_value = mock_repository
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "MySecure123!"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert "id" in data
        assert "created_at" in data

    @patch('corebank.api.v1.endpoints.auth.get_postgres_repository')
    def test_register_with_weak_password_too_short(self, mock_get_repo, client, mock_repository):
        """Test user registration with password too short."""
        mock_get_repo.return_value = mock_repository
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "weak"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "Validation error" in data["detail"]
        
        # Check that the error mentions minimum length
        errors = data["errors"]
        assert any("at least 8 characters" in error["msg"] for error in errors)

    @patch('corebank.api.v1.endpoints.auth.get_postgres_repository')
    def test_register_with_weak_password_missing_requirements(self, mock_get_repo, client, mock_repository):
        """Test user registration with password missing strength requirements."""
        mock_get_repo.return_value = mock_repository
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "weakpassword"  # No uppercase, no digit, no special char
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Password does not meet security requirements" in data["detail"]["message"]
        
        issues = data["detail"]["issues"]
        assert "Password must contain at least one uppercase letter" in issues
        assert "Password must contain at least one digit" in issues
        assert "Password should contain at least one special character" in issues

    @patch('corebank.api.v1.endpoints.auth.get_postgres_repository')
    def test_register_with_common_password(self, mock_get_repo, client, mock_repository):
        """Test user registration with common password pattern."""
        mock_get_repo.return_value = mock_repository
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "password"  # Common password
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Password does not meet security requirements" in data["detail"]["message"]
        
        issues = data["detail"]["issues"]
        assert any("too common" in issue for issue in issues)

    @patch('corebank.api.v1.endpoints.auth.get_postgres_repository')
    def test_register_with_sequential_characters(self, mock_get_repo, client, mock_repository):
        """Test user registration with sequential characters in password."""
        mock_get_repo.return_value = mock_repository
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "MyPass1234!"  # Contains "1234" sequence
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Password does not meet security requirements" in data["detail"]["message"]
        
        issues = data["detail"]["issues"]
        assert "Password should not contain long sequential characters" in issues

    @patch('corebank.api.v1.endpoints.auth.get_postgres_repository')
    def test_register_with_repeated_characters(self, mock_get_repo, client, mock_repository):
        """Test user registration with too many repeated characters."""
        mock_get_repo.return_value = mock_repository
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "MyPassssss1!"  # Contains "ssss" repetition
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Password does not meet security requirements" in data["detail"]["message"]
        
        issues = data["detail"]["issues"]
        assert "Password should not contain too many repeated characters" in issues

    @patch('corebank.api.v1.endpoints.auth.get_postgres_repository')
    def test_register_with_existing_username(self, mock_get_repo, client, mock_repository):
        """Test user registration with existing username."""
        # Mock that user already exists
        mock_repository.get_user_by_username.return_value = {
            "id": "existing-uuid",
            "username": "testuser"
        }
        mock_get_repo.return_value = mock_repository
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "MySecure123!"
            }
        )
        
        assert response.status_code == 409
        data = response.json()
        assert "Username already registered" in data["detail"]

    @patch('corebank.api.v1.endpoints.auth.get_postgres_repository')
    def test_register_with_invalid_username_format(self, mock_get_repo, client, mock_repository):
        """Test user registration with invalid username format."""
        mock_get_repo.return_value = mock_repository
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "test@user",  # Invalid character @
                "password": "MySecure123!"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "Validation error" in data["detail"]

    @patch('corebank.api.v1.endpoints.auth.get_postgres_repository')
    def test_register_with_username_too_short(self, mock_get_repo, client, mock_repository):
        """Test user registration with username too short."""
        mock_get_repo.return_value = mock_repository
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "ab",  # Too short (minimum 3)
                "password": "MySecure123!"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "Validation error" in data["detail"]

    @patch('corebank.api.v1.endpoints.auth.get_postgres_repository')
    def test_register_with_missing_fields(self, mock_get_repo, client, mock_repository):
        """Test user registration with missing required fields."""
        mock_get_repo.return_value = mock_repository
        
        # Missing password
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "Validation error" in data["detail"]

    @patch('corebank.api.v1.endpoints.auth.get_postgres_repository')
    def test_register_with_empty_request_body(self, mock_get_repo, client, mock_repository):
        """Test user registration with empty request body."""
        mock_get_repo.return_value = mock_repository
        
        response = client.post(
            "/api/v1/auth/register",
            json={}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "Validation error" in data["detail"]

    @patch('corebank.api.v1.endpoints.auth.get_postgres_repository')
    def test_register_with_malformed_json(self, mock_get_repo, client, mock_repository):
        """Test user registration with malformed JSON."""
        mock_get_repo.return_value = mock_repository
        
        response = client.post(
            "/api/v1/auth/register",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422

    def test_register_endpoint_exists(self, client):
        """Test that the register endpoint exists and accepts POST requests."""
        # This should return 422 for missing data, not 404 or 405
        response = client.post("/api/v1/auth/register")
        assert response.status_code != 404  # Endpoint exists
        assert response.status_code != 405  # POST method allowed


class TestPasswordValidationErrorHandling:
    """Test error handling in password validation."""

    @patch('corebank.api.v1.endpoints.auth.get_postgres_repository')
    def test_password_validation_error_format(self, mock_get_repo, client, mock_repository):
        """Test that password validation errors are properly formatted."""
        mock_get_repo.return_value = mock_repository
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "weak"  # Multiple validation issues
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        
        # Check error structure
        assert "detail" in data
        assert "errors" in data
        assert "status_code" in data
        assert "path" in data
        
        # Check that errors are properly serialized (no JSON serialization errors)
        assert isinstance(data["errors"], list)
        for error in data["errors"]:
            assert isinstance(error, dict)
            assert "type" in error
            assert "loc" in error
            assert "msg" in error

    @patch('corebank.api.v1.endpoints.auth.get_postgres_repository')
    def test_multiple_password_issues_reported(self, mock_get_repo, client, mock_repository):
        """Test that multiple password validation issues are all reported."""
        mock_get_repo.return_value = mock_repository
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "weakpassword"  # Missing uppercase, digit, special char
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        
        issues = data["detail"]["issues"]
        assert len(issues) >= 3  # Should have multiple issues
        
        # Check that all expected issues are present
        issue_text = " ".join(issues)
        assert "uppercase letter" in issue_text
        assert "digit" in issue_text
        assert "special character" in issue_text
