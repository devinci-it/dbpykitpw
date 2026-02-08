"""
{{MODEL_CLASS}} Model - {{MODEL_CLASS}} data model.

This model represents a {{MODEL_CLASS}} record in the database.
"""

{{FK_IMPORTS}}from dbpykitpw import BaseModel
from peewee import CharField, BooleanField, DateTimeField, IntegerField{{FK_IMPORT_FK}}
from datetime import datetime


class {{MODEL_CLASS}}(BaseModel):
    """
    {{MODEL_CLASS}} model for database operations.
    
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
    {{FK_FIELDS}}
    # Soft delete support (allows logical deletion)
    deleted_at = DateTimeField(null=True)
    
    class Meta:
        table_name = "{{SNAKE_CASE}}"
    
    def __repr__(self):
        """Return detailed string representation."""
        return f"{{MODEL_CLASS}}(id={self.id}, created={self.created_at})"
    
    def __str__(self):
        """Return user-friendly string representation."""
        return f"{{MODEL_CLASS}} #{self.id}"
    
    def is_deleted(self):
        """Check if record is soft deleted."""
        return self.deleted_at is not None
