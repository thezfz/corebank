"""
Database connection and lifecycle management for CoreBank.

This module provides:
- PostgreSQL connection pool management
- Application lifespan management for FastAPI
- Database connection utilities
- Transaction context management

The connection pool is managed through the FastAPI lifespan context
to ensure proper initialization and cleanup.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import psycopg
from fastapi import FastAPI
from psycopg_pool import AsyncConnectionPool

from corebank.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database connection manager for CoreBank.
    
    This class manages the PostgreSQL connection pool and provides
    utilities for database operations.
    """
    
    def __init__(self) -> None:
        """Initialize the database manager."""
        self._pool: Optional[AsyncConnectionPool] = None
    
    async def initialize(self) -> None:
        """
        Initialize the database connection pool.
        
        This should be called during application startup.
        """
        try:
            logger.info("Initializing database connection pool...")
            
            # Create connection pool with configuration from settings
            self._pool = AsyncConnectionPool(
                conninfo=settings.database_url,
                min_size=settings.pool_min_size,
                max_size=settings.pool_max_size,
                timeout=settings.pool_timeout,
                # Additional pool configuration
                max_waiting=0,  # Don't queue connections
                max_lifetime=3600,  # Connection lifetime in seconds
                max_idle=300,  # Max idle time in seconds
            )
            
            # Wait for the pool to be ready
            await self._pool.wait()
            
            logger.info(
                f"Database connection pool initialized successfully. "
                f"Pool size: {settings.pool_min_size}-{settings.pool_max_size}"
            )
            
            # Test the connection
            await self._test_connection()
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    async def close(self) -> None:
        """
        Close the database connection pool.
        
        This should be called during application shutdown.
        """
        if self._pool:
            logger.info("Closing database connection pool...")
            await self._pool.close()
            self._pool = None
            logger.info("Database connection pool closed successfully")
    
    async def _test_connection(self) -> None:
        """Test the database connection."""
        if not self._pool:
            raise RuntimeError("Database pool not initialized")
        
        try:
            async with self._pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    result = await cur.fetchone()
                    if result and result[0] == 1:
                        logger.info("Database connection test successful")
                    else:
                        raise RuntimeError("Database connection test failed")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise
    
    @property
    def pool(self) -> AsyncConnectionPool:
        """
        Get the database connection pool.
        
        Returns:
            AsyncConnectionPool: The database connection pool
            
        Raises:
            RuntimeError: If the pool is not initialized
        """
        if not self._pool:
            raise RuntimeError("Database pool not initialized")
        return self._pool
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[psycopg.AsyncConnection, None]:
        """
        Get a database connection from the pool.

        This is an async context manager that yields a database connection
        and ensures it's properly returned to the pool.

        Yields:
            psycopg.AsyncConnection: Database connection
        """
        if not self._pool:
            raise RuntimeError("Database pool not initialized")

        async with self._pool.connection() as conn:
            yield conn
    
    async def execute_query(
        self, 
        query: str, 
        params: Optional[tuple] = None
    ) -> list[tuple]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            list[tuple]: Query results
        """
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                return await cur.fetchall()
    
    async def execute_command(
        self, 
        command: str, 
        params: Optional[tuple] = None
    ) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE command.
        
        Args:
            command: SQL command string
            params: Command parameters
            
        Returns:
            int: Number of affected rows
        """
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(command, params)
                return cur.rowcount


# Global database manager instance
db_manager = DatabaseManager()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan context manager.
    
    This manages the application lifecycle, including:
    - Database connection pool initialization
    - Application startup tasks
    - Cleanup on shutdown
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting CoreBank application...")
    
    try:
        # Initialize database
        await db_manager.initialize()
        
        # Store database manager in app state for dependency injection
        app.state.db_manager = db_manager
        
        logger.info("CoreBank application started successfully")
        
        # Yield control to the application
        yield
        
    except Exception as e:
        logger.error(f"Failed to start CoreBank application: {e}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down CoreBank application...")
        
        try:
            # Close database connections
            await db_manager.close()
            
            logger.info("CoreBank application shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during application shutdown: {e}")


def get_db_manager() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    This function can be used as a FastAPI dependency to inject
    the database manager into endpoint functions.
    
    Returns:
        DatabaseManager: The global database manager instance
    """
    return db_manager
