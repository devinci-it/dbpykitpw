"""
{{REPO_CLASS}} - CRUD operations for {{MODEL_CLASS}} model.

This repository handles all database operations for {{MODEL_CLASS}} records.
It provides methods for create, read, update, delete, and soft delete operations.
"""

from dbpykitpw import BaseRepository, register_repository
from models.{{SNAKE_CASE}} import {{MODEL_CLASS}}{{FK_IMPORTS_REPO}}


@register_repository("{{SNAKE_CASE}}_repo")
class {{REPO_CLASS}}(BaseRepository):
    """
    Repository for {{MODEL_CLASS}} CRUD operations.
    
    Provides:
    - Basic CRUD operations (inherited from BaseRepository)
    - Custom queries specific to {{MODEL_CLASS}}
    - Soft delete and restore functionality
    - Data transformation utilities
    """
    
    model = {{MODEL_CLASS}}
    soft_delete_enabled = True
    
    # Example custom query methods:
    
    # def get_by_name(self, name):
    #     """Get {{MODEL_CLASS}} by name."""
    #     return self.get_by_field("name", name)
    # 
    # def get_active(self):
    #     """Get all active {{MODEL_CLASS}} records."""
    #     active = self.get_all(include_deleted=False)
    #     active = [item for item in active if item.is_active]
    #     return active
    # 
    # def deactivate(self, {{SNAKE_CASE}}_id):
    #     """Mark {{MODEL_CLASS}} as inactive."""
    #     return self.update({{SNAKE_CASE}}_id, ("is_active", False)){{FK_EXAMPLES}}
    
    def __repr__(self):
        """Return detailed string representation."""
        return f"{{REPO_CLASS}}(model={self.model.__name__})"
    
    def __str__(self):
        """Return user-friendly string representation."""
        return f"Repository for {self.model.__name__}"
