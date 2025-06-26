"""
Permission and role-based access control utilities.
"""

from functools import wraps
from typing import List, Callable
from fastapi import HTTPException, status, Depends
from uuid import UUID

from corebank.models.user import UserRole
from corebank.api.v1.dependencies import get_current_user_id, get_user_service
from corebank.services.user_service import UserService


async def get_current_user_role(
    current_user_id: UUID = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
) -> UserRole:
    """
    Get the role of the current authenticated user.
    
    Args:
        current_user_id: Current user ID from JWT token
        user_service: User service dependency
        
    Returns:
        UserRole: The user's role
        
    Raises:
        HTTPException: If user not found
    """
    try:
        user = await user_service.get_user_by_id(current_user_id)
        return user.role
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


def require_role(required_roles: List[UserRole]):
    """
    Decorator to require specific roles for accessing an endpoint.
    
    Args:
        required_roles: List of roles that are allowed to access the endpoint
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user_role from kwargs if it exists
            current_user_role = kwargs.get('current_user_role')
            
            if current_user_role is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="User role not provided"
                )
            
            if current_user_role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_admin(func: Callable) -> Callable:
    """
    Decorator to require admin role for accessing an endpoint.
    
    Args:
        func: The function to decorate
        
    Returns:
        Decorated function
    """
    return require_role([UserRole.ADMIN])(func)


async def verify_admin_access(
    current_user_role: UserRole = Depends(get_current_user_role)
) -> None:
    """
    Dependency to verify admin access.
    
    Args:
        current_user_role: Current user's role
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


async def verify_user_or_admin_access(
    target_user_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    current_user_role: UserRole = Depends(get_current_user_role)
) -> None:
    """
    Dependency to verify that user can access their own data or admin can access any data.
    
    Args:
        target_user_id: The user ID being accessed
        current_user_id: Current authenticated user ID
        current_user_role: Current user's role
        
    Raises:
        HTTPException: If access is not allowed
    """
    if current_user_role == UserRole.ADMIN:
        # Admin can access any user's data
        return
    
    if current_user_id == target_user_id:
        # User can access their own data
        return
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )
