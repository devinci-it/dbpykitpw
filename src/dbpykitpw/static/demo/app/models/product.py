"""
Product Model - Product data model.

This model represents a Product record in the database.
"""

from dbpykitpw import BaseModel
from peewee import CharField, BooleanField, DateTimeField, IntegerField, ForeignKeyField
from datetime import datetime
from models.user import User


class Product(BaseModel):
    """
    Product model for database operations.
    
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
    name = CharField(max_length=255)
    description = CharField(max_length=500, null=True)
    price = IntegerField(default=0)
    user = ForeignKeyField(User, backref="products", null=True)  # FK to User, reverse relation: user.products
    
    class Meta:
        table_name = "product"
    
    def __repr__(self):
        """Return detailed string representation."""
        return f"Product(id={self.id}, created={self.created_at})"
    
    def __str__(self):
        """Return user-friendly string representation."""
        return f"Product #{self.id}"
    
    def is_deleted(self):
        """Check if record is soft deleted."""
        return self.deleted_at is not None
