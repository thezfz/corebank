"""
User service for managing user operations.
"""

from typing import Optional
from uuid import UUID

from corebank.models.user import UserResponse, UserDetailResponse, UserRole, UserSoftDelete
from corebank.models.common import PaginatedResponse, PaginationParams
from corebank.repositories.postgres_repo import PostgresRepository


class UserService:
    """Service for user management operations."""

    def __init__(self, repository: PostgresRepository):
        """
        Initialize user service.

        Args:
            repository: Database repository instance
        """
        self.repository = repository

    async def get_user_by_id(self, user_id: UUID) -> UserResponse:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            UserResponse: User information

        Raises:
            ValueError: If user not found
        """
        user_data = await self.repository.get_user_by_id(user_id)
        if not user_data:
            raise ValueError("User not found")
        
        return UserResponse(**user_data)

    async def get_user_detail_by_id(self, user_id: UUID) -> UserDetailResponse:
        """
        Get detailed user information by ID.

        Args:
            user_id: User ID

        Returns:
            UserDetailResponse: Detailed user information

        Raises:
            ValueError: If user not found
        """
        user_data = await self.repository.get_user_detail_by_id(user_id)
        if not user_data:
            raise ValueError("User not found")
        
        return UserDetailResponse(**user_data)

    async def get_all_users(
        self,
        pagination: PaginationParams,
        role_filter: Optional[UserRole] = None,
        include_deleted: bool = False,
        search_term: Optional[str] = None
    ) -> PaginatedResponse[UserDetailResponse]:
        """
        Get all users with pagination and optional role filtering.

        Args:
            pagination: Pagination parameters
            role_filter: Optional role filter
            include_deleted: Whether to include deleted users
            search_term: Optional search term for username, real name, or email

        Returns:
            PaginatedResponse[UserDetailResponse]: Paginated user list
        """
        users_data = await self.repository.get_all_users(
            limit=pagination.page_size,
            offset=pagination.offset,
            role_filter=role_filter.value if role_filter else None,
            include_deleted=include_deleted,
            search_term=search_term
        )

        users = [UserDetailResponse(**user) for user in users_data]

        # Get total count
        total_count = await self.repository.count_users(
            role_filter=role_filter.value if role_filter else None,
            include_deleted=include_deleted,
            search_term=search_term
        )
        
        return PaginatedResponse.create(
            items=users,
            total_count=total_count,
            pagination=pagination
        )

    async def update_user_role(self, user_id: UUID, new_role: UserRole) -> UserResponse:
        """
        Update user role.

        Args:
            user_id: User ID
            new_role: New role to assign

        Returns:
            UserResponse: Updated user information

        Raises:
            ValueError: If user not found
        """
        # Verify user exists
        existing_user = await self.repository.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError("User not found")
        
        # Update role
        updated_user = await self.repository.update_user_role(user_id, new_role.value)
        
        return UserResponse(**updated_user)



    async def soft_delete_user(self, user_id: UUID, delete_request: UserSoftDelete) -> UserResponse:
        """
        Soft delete a user.

        Args:
            user_id: User ID
            delete_request: Deletion request data

        Returns:
            UserResponse: Updated user information

        Raises:
            ValueError: If user not found
        """
        # Verify user exists
        existing_user = await self.repository.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError("User not found")

        # Soft delete user
        updated_user = await self.repository.soft_delete_user(user_id, delete_request.reason)

        return UserResponse(**updated_user)

    async def restore_user(self, user_id: UUID, reason: str) -> UserResponse:
        """
        Restore a soft deleted user.

        Args:
            user_id: User ID
            reason: Restoration reason

        Returns:
            UserResponse: Restored user information

        Raises:
            ValueError: If user not found or not deleted
        """
        # Restore user
        restored_user = await self.repository.restore_user(user_id, reason)

        return UserResponse(**restored_user)

    async def get_deleted_users(
        self,
        pagination: PaginationParams,
        role_filter: Optional[UserRole] = None
    ) -> PaginatedResponse[UserDetailResponse]:
        """
        Get deleted users with pagination and optional role filtering.

        Args:
            pagination: Pagination parameters
            role_filter: Optional role filter

        Returns:
            PaginatedResponse[UserDetailResponse]: Paginated deleted user list
        """
        users_data = await self.repository.get_deleted_users(
            limit=pagination.page_size,
            offset=pagination.offset,
            role_filter=role_filter.value if role_filter else None
        )

        users = [UserDetailResponse(**user) for user in users_data]

        # Get total count
        total_count = await self.repository.count_deleted_users(
            role_filter=role_filter.value if role_filter else None
        )

        return PaginatedResponse.create(
            items=users,
            total_count=total_count,
            pagination=pagination
        )

    async def get_user_detail_by_id(self, user_id: UUID) -> UserDetailResponse:
        """
        Get detailed user information by ID.

        Args:
            user_id: User ID

        Returns:
            UserDetailResponse: Detailed user information

        Raises:
            ValueError: If user not found
        """
        user_data = await self.repository.get_user_detail_by_id(user_id)
        if not user_data:
            raise ValueError("User not found")

        return UserDetailResponse(**user_data)

    async def get_user_statistics(self) -> dict:
        """
        Get user statistics for admin dashboard.

        Returns:
            dict: User statistics
        """
        stats = await self.repository.get_user_statistics()
        return stats
