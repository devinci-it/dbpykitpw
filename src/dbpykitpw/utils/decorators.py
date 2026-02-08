"""
Decorators - Utility decorators for repository registration.
"""

from typing import Type, Callable
from dbpykitpw.db.database_singleton import DatabaseSingleton


def register_repository(key: str) -> Callable:
    """
    Decorator to automatically register a repository and its model with DatabaseSingleton.

    This decorator extracts the model class from the repository and registers both
    the repository and model with the DatabaseSingleton for easy access.

    Args:
        key: Unique identifier key for the repository/model pair

    Returns:
        Decorator function

    Example:
        @register_repository('subcase_repo')
        class SubCaseRepository(BaseRepository):
            model = SubCase
            soft_delete_enabled = True
    """

    def wrapper(repo_class: Type) -> Type:
        """
        Wrap the repository class and register it with DatabaseSingleton.

        Args:
            repo_class: The repository class to register

        Returns:
            The original repository class (unchanged)

        Raises:
            ValueError: If repository class doesn't have a model attribute
        """
        # Verify the repository has a model attribute
        if not hasattr(repo_class, "model") or repo_class.model is None:
            raise ValueError(f"Repository {repo_class.__name__} must define a 'model' attribute")

        # Get the model from the repository class
        model_class = repo_class.model

        # Get the DatabaseSingleton instance
        db = DatabaseSingleton.get_instance()

        # Register both model and repository
        db.register_model(model_class, repo_class, key)

        # Return the repository class unchanged
        return repo_class

    return wrapper


def __repr__() -> str:
    """String representation of the decorators module."""
    return "decorators module with repository registration utilities"


def __str__() -> str:
    """User-friendly string representation."""
    return "Repository Registration Decorators"
