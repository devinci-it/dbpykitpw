"""
Demo User Model - Example domain model for demonstration.
"""

import sys
import os

project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, project_root)

from peewee import AutoField, CharField, BooleanField, DateTimeField
from datetime import datetime

from dbpykitpw.models.base_model import BaseModel


class User(BaseModel):
    """
    User model representing a user in the system.

    Attributes:
        id: Unique identifier
        username: Unique username
        email: User email address (stored as CharField)
        full_name: Full name of the user
        is_active: Whether the user account is active
        deleted_at: Soft delete timestamp (null if not deleted)
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
    """

    id = AutoField(primary_key=True)
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=255, unique=True)
    full_name = CharField(max_length=255)
    is_active = BooleanField(default=True)
    deleted_at = DateTimeField(null=True)

    class Meta:
        """Meta configuration for User."""

        table_name = "user"

    def __repr__(self) -> str:
        """Detailed string representation of User."""
        return (
            f"User(id={self.id}, username='{self.username}', email='{self.email}', "
            f"full_name='{self.full_name}', is_active={self.is_active}, "
            f"deleted_at={self.deleted_at})"
        )

    def __str__(self) -> str:
        """User-friendly string representation of User."""
        status = "DELETED" if self.deleted_at else "ACTIVE"
        return f"User #{self.id} - {self.username} <{self.email}> ({status})"

    def is_deleted(self) -> bool:
        """Check if this user is soft deleted."""
        return self.deleted_at is not None

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
