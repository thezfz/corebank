"""
Custom exceptions for CoreBank application.

This module defines all custom exceptions used throughout the application
for better error handling and user feedback.
"""


class CoreBankException(Exception):
    """Base exception class for CoreBank application."""
    
    def __init__(self, message: str, error_code: str = None):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__


class ValidationError(CoreBankException):
    """Raised when input validation fails."""
    pass


class NotFoundError(CoreBankException):
    """Raised when a requested resource is not found."""
    pass


class DuplicateError(CoreBankException):
    """Raised when trying to create a resource that already exists."""
    pass


class InsufficientFundsError(CoreBankException):
    """Raised when an account has insufficient funds for a transaction."""
    pass


class BusinessRuleError(CoreBankException):
    """Raised when a business rule is violated."""
    pass


class AuthenticationError(CoreBankException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(CoreBankException):
    """Raised when authorization fails."""
    pass


class DatabaseError(CoreBankException):
    """Raised when a database operation fails."""
    pass


class ExternalServiceError(CoreBankException):
    """Raised when an external service call fails."""
    pass


class ConfigurationError(CoreBankException):
    """Raised when there's a configuration error."""
    pass


class RateLimitError(CoreBankException):
    """Raised when rate limit is exceeded."""
    pass


class MaintenanceError(CoreBankException):
    """Raised when the system is under maintenance."""
    pass


# Investment-specific exceptions

class InvestmentError(CoreBankException):
    """Base exception for investment-related errors."""
    pass


class ProductNotAvailableError(InvestmentError):
    """Raised when an investment product is not available."""
    pass


class RiskAssessmentRequiredError(InvestmentError):
    """Raised when a risk assessment is required but not found."""
    pass


class RiskAssessmentExpiredError(InvestmentError):
    """Raised when a risk assessment has expired."""
    pass


class InvestmentLimitExceededError(InvestmentError):
    """Raised when investment limits are exceeded."""
    pass


class RedemptionNotAllowedError(InvestmentError):
    """Raised when redemption is not allowed for a holding."""
    pass


class InsufficientHoldingError(InvestmentError):
    """Raised when trying to redeem more than held."""
    pass


class ProductRiskMismatchError(InvestmentError):
    """Raised when product risk doesn't match user's risk profile."""
    pass


class TransactionProcessingError(InvestmentError):
    """Raised when transaction processing fails."""
    pass


class NAVNotAvailableError(InvestmentError):
    """Raised when NAV data is not available."""
    pass
