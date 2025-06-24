"""
CoreBank FastAPI application.

This module creates and configures the FastAPI application instance
with all necessary middleware, exception handlers, and routes.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from corebank.api.v1.api import api_router
from corebank.core.config import settings
from corebank.core.db import lifespan
from corebank.logging_config import get_logger

# Configure logging
logger = get_logger(__name__)


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    # Create FastAPI app with lifespan management
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="CoreBank - A secure and robust banking system backend",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )
    
    # Configure CORS
    configure_cors(app)
    
    # Add middleware
    add_middleware(app)
    
    # Add exception handlers
    add_exception_handlers(app)
    
    # Include routers
    app.include_router(api_router, prefix="/api")
    
    # Add root endpoint
    @app.get("/", tags=["Root"])
    async def root() -> dict:
        """Root endpoint with basic API information."""
        return {
            "message": "Welcome to CoreBank API",
            "version": settings.app_version,
            "environment": settings.environment,
            "api_docs": "/docs" if settings.is_development else "disabled",
            "health_check": "/api/v1/health"
        }
    
    logger.info(f"FastAPI application created - {settings.app_name} v{settings.app_version}")
    
    return app


def configure_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware.
    
    Args:
        app: FastAPI application instance
    """
    # CORS configuration
    origins = [
        "http://localhost:3000",  # React development server
        "http://localhost:5173",  # Vite development server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Add production origins if in production
    if settings.is_production:
        # Add your production frontend URLs here
        origins.extend([
            "https://your-frontend-domain.com",
        ])
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    logger.info("CORS middleware configured")


def add_middleware(app: FastAPI) -> None:
    """
    Add custom middleware to the application.
    
    Args:
        app: FastAPI application instance
    """
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all HTTP requests."""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} "
            f"({process_time:.3f}s)"
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    logger.info("Custom middleware added")


def add_exception_handlers(app: FastAPI) -> None:
    """
    Add custom exception handlers.
    
    Args:
        app: FastAPI application instance
    """
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        logger.warning(
            f"HTTP exception: {exc.status_code} - {exc.detail} "
            f"for {request.method} {request.url.path}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        logger.warning(
            f"Validation error for {request.method} {request.url.path}: {exc.errors()}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation error",
                "errors": exc.errors(),
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle Starlette HTTP exceptions."""
        logger.error(
            f"Starlette exception: {exc.status_code} - {exc.detail} "
            f"for {request.method} {request.url.path}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail or "Internal server error",
                "status_code": exc.status_code,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(
            f"Unhandled exception for {request.method} {request.url.path}: {exc}",
            exc_info=True
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "path": str(request.url.path)
            }
        )
    
    logger.info("Exception handlers added")


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting CoreBank application...")
    
    uvicorn.run(
        "corebank.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
