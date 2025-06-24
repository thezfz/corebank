"""
CoreBank - A secure and robust banking system backend.

This package provides a comprehensive banking system with the following features:
- User authentication and authorization
- Account management (savings, checking accounts)
- Core banking transactions (deposits, withdrawals, transfers)
- Secure API endpoints with JWT authentication
- PostgreSQL database with ACID transactions
- Comprehensive testing suite

The system follows a clean architecture pattern with clear separation of concerns:
- API layer: FastAPI endpoints and request/response models
- Service layer: Business logic and transaction management
- Repository layer: Data access and database operations
- Security layer: Authentication, authorization, and password management

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "CoreBank Team"
__email__ = "team@corebank.com"

# Package metadata
__all__ = [
    "__version__",
    "__author__",
    "__email__",
]
