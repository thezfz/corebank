"""
API v1 router aggregation for CoreBank.

This module aggregates all v1 API endpoints and provides
a single router for the FastAPI application.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from corebank.api.v1.dependencies import get_health_status
from corebank.api.v1.endpoints import auth, accounts, transactions
from corebank.models.common import HealthCheck
from corebank.core.config import settings

logger = logging.getLogger(__name__)

# Create the main v1 API router
api_router = APIRouter(prefix="/v1")

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(accounts.router)
api_router.include_router(transactions.router)


@api_router.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check(
    health_status: Annotated[dict, Depends(get_health_status)]
) -> HealthCheck:
    """
    Health check endpoint.
    
    Args:
        health_status: Health status dependency
        
    Returns:
        HealthCheck: Application health status
    """
    import time
    from datetime import datetime
    
    # Calculate uptime (simplified - in production you'd track actual start time)
    uptime = time.time() % 86400  # Uptime in seconds (mod 24 hours for demo)
    
    return HealthCheck(
        status=health_status["status"],
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        database=health_status["database"]["status"],
        uptime=uptime
    )


@api_router.get("/", tags=["Root"])
async def api_info() -> dict:
    """
    API information endpoint.
    
    Returns:
        dict: API information
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "api_version": "v1",
        "description": "CoreBank API - Secure banking system backend",
        "endpoints": {
            "authentication": "/v1/auth",
            "accounts": "/v1/accounts", 
            "transactions": "/v1/transactions",
            "health": "/v1/health"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }
