"""
Logging configuration for CoreBank.

This module provides centralized logging configuration using loguru.
It sets up structured logging with appropriate formatters and handlers
for both development and production environments.
"""

import sys
from pathlib import Path
from typing import Dict, Any

from loguru import logger

from corebank.core.config import settings


def configure_logging() -> None:
    """
    Configure application logging.
    
    This function sets up loguru with appropriate configuration
    based on the application settings.
    """
    # Remove default handler
    logger.remove()
    
    # Configure console handler
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    logger.add(
        sys.stdout,
        format=console_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # Configure file handler if log file is specified
    if settings.log_file:
        log_file_path = Path(settings.log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} - "
            "{message}"
        )
        
        logger.add(
            log_file_path,
            format=file_format,
            level=settings.log_level,
            rotation="10 MB",
            retention="30 days",
            compression="gz",
            backtrace=True,
            diagnose=True,
        )
    
    # Add structured logging for production
    if settings.is_production:
        # Add JSON formatter for production logs
        logger.add(
            "logs/corebank.json",
            format="{time} {level} {name} {function} {line} {message}",
            level="INFO",
            rotation="100 MB",
            retention="90 days",
            compression="gz",
            serialize=True,  # JSON format
        )
    
    # Log configuration
    logger.info(f"Logging configured - Level: {settings.log_level}")
    if settings.log_file:
        logger.info(f"File logging enabled - Path: {settings.log_file}")


def get_logger(name: str) -> Any:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)


# Configure logging when module is imported
configure_logging()
