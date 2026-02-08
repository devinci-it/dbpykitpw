"""
Demo User Repository - Repository for User model operations.
"""

from typing import List, Optional

import sys
import os

project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, project_root)

from dbpykitpw.repositories.base_repository import BaseRepository
from dbpykitpw.static.demo.user_model import User
from dbpykitpw.utils.decorators import register_repository


@register_repository("user_repo")
class UserRepository(BaseRepository):
    """
    Repository for User model providing specialized operations.
    Inherits all CRUD operations from BaseRepository.
    Demonstrates custom queries and business logic.
    """

    model = User
    soft_delete_enabled = True

    def get_by_username(self, username: str, include_deleted: bool = False) -> Optional[User]:
        """
        Get a user by username.

        Args:
            username: Username to search for
            include_deleted: Whether to include soft-deleted records

        Returns:
            User instance or None if not found
        """
        with self.transaction_manager.transaction():
            query = User.select().where(User.username == username)
            if not include_deleted and self.soft_delete_enabled:
                query = query.where(User.deleted_at.is_null())
            return query.first()

    def get_by_email(self, email: str, include_deleted: bool = False) -> Optional[User]:
        """
        Get a user by email.

        Args:
            email: Email to search for
            include_deleted: Whether to include soft-deleted records

        Returns:
            User instance or None if not found
        """
        with self.transaction_manager.transaction():
            query = User.select().where(User.email == email)
            if not include_deleted and self.soft_delete_enabled:
                query = query.where(User.deleted_at.is_null())
            return query.first()

    def get_active_users(self) -> List[User]:
        """
        Get all active (non-deleted and is_active=True) users.

        Returns:
            List of active User instances
        """
        with self.transaction_manager.transaction():
            query = (
                User.select()
                .where((User.deleted_at.is_null()) & (User.is_active == True))
            )
            return list(query)

    def deactivate_user(self, user_id: int) -> int:
        """
        Deactivate a user (set is_active to False).

        Args:
            user_id: ID of user to deactivate

        Returns:
            Number of rows affected
        """
        with self.transaction_manager.transaction():
            query = User.update({User.is_active: False}).where(User.id == user_id)
            return query.execute()

    def activate_user(self, user_id: int) -> int:
        """
        Activate a user (set is_active to True).

        Args:
            user_id: ID of user to activate

        Returns:
            Number of rows affected
        """
        with self.transaction_manager.transaction():
            query = User.update({User.is_active: True}).where(User.id == user_id)
            return query.execute()

    def get_deleted_users(self) -> List[User]:
        """
        Get all soft-deleted users.

        Returns:
            List of deleted User instances
        """
        with self.transaction_manager.transaction():
            query = User.select().where(User.deleted_at.is_null(False))
            return list(query)

    def __repr__(self) -> str:
        """Detailed string representation."""
        count = self.count()
        active = self.count()  # Count active users (non-deleted)
        return f"UserRepository(total_records={count}, active_users={active})"

    def __str__(self) -> str:
        """User-friendly string representation."""
        count = self.count()
        return f"User Repository with {count} records"
