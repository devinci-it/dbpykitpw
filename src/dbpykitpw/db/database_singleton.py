"""
Database Singleton - Manages database connection, repositories, and models.
"""

from peewee import SqliteDatabase
from contextlib import contextmanager
from typing import Type, Dict, Optional, List, Any


class DatabaseSingleton:
    """
    Singleton pattern implementation for database management.
    Handles database configuration, connection, model/repository registration,
    table creation, and custom SQL execution.
    """

    _instance = None
    _db: Optional[SqliteDatabase] = None
    _repositories: Dict[str, Type["BaseRepository"]] = {}
    _models: Dict[str, Type["BaseModel"]] = {}
    _soft_delete_enabled: bool = False

    def __new__(cls):
        """Ensure only one instance of DatabaseSingleton exists."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        """Get the singleton instance."""
        return cls()

    def configure(self, db_file: str, soft_delete_enabled: bool = False):
        """
        Configure the database with a file path.

        Args:
            db_file: Path to the SQLite database file
            soft_delete_enabled: Enable soft delete functionality globally

        Returns:
            self: For method chaining
        """
        self._db = SqliteDatabase(db_file)
        self._soft_delete_enabled = soft_delete_enabled
        return self

    def connect(self):
        """
        Establish database connection.

        Returns:
            self: For method chaining
        """
        if self._db and not self._db.is_connection_usable():
            self._db.connect()
        return self

    def disconnect(self):
        """Close the database connection."""
        if self._db:
            self._db.close()

    def register_model(
        self, model_class: Type["Model"], repo_class: Type["BaseRepository"], key: str
    ):
        """
        Register a model and its associated repository.
        Sets the database on the model if not already set.

        Args:
            model_class: The Peewee Model class
            repo_class: The BaseRepository subclass
            key: Unique identifier key for this model/repo pair
        """
        # Set database on model if not already set
        if self._db and (not hasattr(model_class._meta, 'database') or model_class._meta.database is None):
            model_class._meta.database = self._db
        
        self._models[key] = model_class
        self._repositories[key] = repo_class

    def create_tables(self):
        """Create all registered model tables in the database."""
        if self._db:
            # Ensure all models have the database set
            for model_class in self._models.values():
                if not hasattr(model_class._meta, 'database') or model_class._meta.database is None:
                    model_class._meta.database = self._db
            
            with self._db:
                self._db.create_tables(self._models.values())

    def get_repository(self, key: str) -> Optional[Type["BaseRepository"]]:
        """
        Retrieve a registered repository class by key.

        Args:
            key: The registration key

        Returns:
            The repository class or None if not found
        """
        return self._repositories.get(key)

    def get_model(self, key: str) -> Optional[Type["Model"]]:
        """
        Retrieve a registered model class by key.

        Args:
            key: The registration key

        Returns:
            The model class or None if not found
        """
        return self._models.get(key)

    def get_all_models(self) -> Dict[str, Type["Model"]]:
        """Get all registered models."""
        return self._models.copy()

    def get_all_repositories(self) -> Dict[str, Type["BaseRepository"]]:
        """Get all registered repositories."""
        return self._repositories.copy()

    @contextmanager
    def transaction(self):
        """
        Context manager for atomic transactions.

        Yields:
            The database connection for transaction use
        """
        if self._db:
            with self._db.atomic():
                yield self._db

    def execute_sql(self, sql: str, params: Optional[tuple] = None) -> List[Any]:
        """
        Execute raw SQL query.

        Args:
            sql: SQL query string
            params: Optional query parameters

        Returns:
            List of query results
        """
        if self._db:
            with self._db.connection_context():
                result = self._db.execute_sql(sql, params or ())
                return result.fetchall()
        return []

    def execute_sql_single(self, sql: str, params: Optional[tuple] = None) -> Optional[Any]:
        """
        Execute raw SQL query and return first result.

        Args:
            sql: SQL query string
            params: Optional query parameters

        Returns:
            First result or None
        """
        results = self.execute_sql(sql, params)
        return results[0] if results else None

    def __repr__(self) -> str:
        """String representation of DatabaseSingleton."""
        models_count = len(self._models)
        repos_count = len(self._repositories)
        db_file = self._db.database if self._db else "Not configured"
        return (
            f"DatabaseSingleton(db={db_file}, models={models_count}, "
            f"repositories={repos_count}, soft_delete={self._soft_delete_enabled})"
        )

    def __str__(self) -> str:
        """User-friendly string representation."""
        return (
            f"DatabaseSingleton with {len(self._models)} models, "
            f"{len(self._repositories)} repositories"
        )
