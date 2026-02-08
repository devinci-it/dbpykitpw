"""
UserRepository - CRUD operations for User model.

This repository handles all database operations for User records.
It provides methods for create, read, update, delete, and soft delete operations.
"""

from dbpykitpw import BaseRepository, register_repository
from dbpykitpw import BaseModel
from models.user import User


@register_repository("user_repo")
class UserRepository(BaseRepository):
    """
    Repository for User CRUD operations.
    
    Provides:
    - Basic CRUD operations (inherited from BaseRepository)
    - Custom queries specific to User
    - Soft delete and restore functionality
    - Data transformation utilities
    """
    
    model = User
    soft_delete_enabled = True

    def register_user(self, user_instance):
        """
        Register the user instance in the database.
        
        Args:
            user_instance: An instance of the User model to be saved
        """
        # This should save the instance to the database
        user_instance.save()  # or any database-saving logic depending on your ORM
        return user_instance    
    # Example custom query methods:
    
    # def get_by_name(self, name):
    #     """Get User by name."""
    #     return self.get_by_field("name", name)
    # 
    # def get_active(self):
    #     """Get all active User records."""
    #     active = self.get_all(include_deleted=False)
    #     active = [item for item in active if item.is_active]
    #     return active
    # 
    # def deactivate(self, user_id):
    #     """Mark User as inactive."""
    #     return self.update(user_id, ("is_active", False))
    
    def __repr__(self):
        """Return detailed string representation."""
        return f"UserRepository(model={self.model.__name__})"
    
    def __str__(self):
        """Return user-friendly string representation."""
        return f"Repository for {self.model.__name__}"
