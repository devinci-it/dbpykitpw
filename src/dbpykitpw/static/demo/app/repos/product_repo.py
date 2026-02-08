"""
ProductRepository - CRUD operations for Product model.

This repository handles all database operations for Product records.
It provides methods for create, read, update, delete, and soft delete operations.
"""

from dbpykitpw import BaseRepository, register_repository
from models.product import Product


@register_repository("product_repo")
class ProductRepository(BaseRepository):
    """
    Repository for Product CRUD operations.
    
    Provides:
    - Basic CRUD operations (inherited from BaseRepository)
    - Custom queries specific to Product
    - Soft delete and restore functionality
    - Data transformation utilities
    """
    
    model = Product
    soft_delete_enabled = True
    
    # Example custom query methods:
    
    # def get_by_name(self, name):
    #     """Get Product by name."""
    #     return self.get_by_field("name", name)
    # 
    # def get_active(self):
    #     """Get all active Product records."""
    #     active = self.get_all(include_deleted=False)
    #     active = [item for item in active if item.is_active]
    #     return active
    # 
    # def deactivate(self, product_id):
    #     """Mark Product as inactive."""
    #     return self.update(product_id, ("is_active", False))
    
    def __repr__(self):
        """Return detailed string representation."""
        return f"ProductRepository(model={self.model.__name__})"
    
    def __str__(self):
        """Return user-friendly string representation."""
        return f"Repository for {self.model.__name__}"
