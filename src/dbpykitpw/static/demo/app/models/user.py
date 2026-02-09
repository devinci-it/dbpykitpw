"""
User Model - User data model.

This model represents a User record in the database.
"""

import email
from dbpykitpw import BaseModel
from peewee import CharField, BooleanField, DateTimeField, IntegerField
from datetime import datetime


class User(BaseModel):
    """
    User model for database operations.
    
    Fields:
        id (AutoField): Primary key
        created_at (DateTimeField): Auto-set creation timestamp
        updated_at (DateTimeField): Auto-updated modification timestamp
        deleted_at (DateTimeField): Soft delete timestamp (nullable)
    
    Add custom fields below as needed.
    """
    
    # Add your model fields here
    # Example fields:
    # name = CharField(max_length=255)
    # description = CharField(max_length=500, null=True)
    # is_active = BooleanField(default=True)
    # quantity = IntegerField(default=0)
    
    # Soft delete support (allows logical deletion)
    deleted_at = DateTimeField(null=True)
    email = CharField(max_length=255, unique=True)
    username = CharField(max_length=255, unique=True)
    is_active = BooleanField(default=True)
    first_name=CharField(max_length=255, null=True)
    last_name=CharField(max_length=255, null=True)
    full_name=CharField(max_length=255, null=True)
    birth_date=DateTimeField(null=True)
    phone_number=CharField(max_length=20, null=True)
    
    class Meta:
        table_name = "user"
    
    def __init__(self, **kwargs):
        """Initialize User with dynamic setter methods."""
        super().__init__(**kwargs)
    
    def __repr__(self):
        """Return detailed string representation."""
        return f"User(id={self.id}, created={self.created_at})"
    
    def __str__(self):
        """Return user-friendly string representation."""
        return f"User #{self.id}"
    
    def is_deleted(self):
        """Check if record is soft deleted."""
        return self.deleted_at is not None
