"""
Base Repository - Generic CRUD operations with transaction support.

Provides a base repository class for all models with common database operations
including Create, Read, Update, Delete, soft delete, restore, and data transformations.

The BaseRepository handles:
- Atomic CRUD operations wrapped in transactions
- Soft delete (logical deletion) with restore capability
- Flexible querying by primary key or any field
- Data transformations (model to dict/JSON and vice versa)
- Schema introspection (columns, primary keys, types)

Usage:
    Define a custom repository:
    
    >>> from dbpykitpw import BaseRepository, register_repository
    >>> from models.user import User
    >>>
    >>> @register_repository("user_repo")
    ... class UserRepository(BaseRepository):
    ...     model = User
    ...     soft_delete_enabled = True
    ...     
    ...     def get_by_email(self, email: str):
    ...         return self.get_by_field("email", email)
    
    Use in application:
    
    >>> repo = db.get_repository("user_repo")  # Get the registered repository class
    >>> # user_repo_instance = UserRepository(db._db)  # Instantiate the repository with database (OR)
    >>> user = User(username="alice", email="alice@test.com")
    >>> repo.create(user)
    >>> found = repo.get_by_id(user.id)
    >>> repo.update(user.id, ("username", "alice_smith"))
    >>> repo.delete(user.id)  # Soft delete
    >>> repo.restore(user.id)  # Restore soft deleted

Attributes:
    model (Type[Model]): The Peewee Model class for this repository
    soft_delete_field (str): Name of soft delete field, defaults to "deleted_at"
    soft_delete_enabled (bool): Enable soft delete functionality
"""

from peewee import Model
from datetime import datetime
from typing import Type, Union, Optional, List, Tuple, Any, Dict

from dbpykitpw.db.transaction_manager import TransactionManager
from dbpykitpw.utils.data_transformer import DataTransformer


class BaseRepository:
    """
    Generic repository class providing CRUD operations with transaction support.
    
    This is the base class for all repositories. It provides:
    - Atomic Create, Read, Update, Delete operations
    - Soft delete with restore capability
    - Data transformation utilities
    - Field-based and ID-based querying
    - Count and existence checking
    - Raw SQL query support
    """

    model: Optional[Type[Model]] = None
    soft_delete_field: Optional[str] = "deleted_at"
    soft_delete_enabled: bool = False

    def __init__(self, database: "SqliteDatabase") -> None:
        """
        Initialize the repository.

        Args:
            database (SqliteDatabase): SqliteDatabase instance from DatabaseSingleton
            
        Example:
            >>> from dbpykitpw import DatabaseSingleton
            >>> db = DatabaseSingleton.get_instance()
            >>> repo = UserRepository(db._db)
        """
        self.db = database
        self.transaction_manager = TransactionManager(database)

    def create(self, model_instance: Model) -> Model:
        """
        Create and persist a new record in the database.
        
        Wraps the save operation in an atomic transaction. Sets created_at and
        updated_at timestamps automatically.

        Args:
            model_instance (Model): Instance of the model to create with fields populated

        Returns:
            Model: The created model instance with ID populated
            
        Raises:
            Exception: If database constraint is violated (unique, not null, etc.)
            
        Example:
            >>> user = User(username="alice", email="alice@test.com")
            >>> created_user = repo.create(user)
            >>> print(created_user.id)  # ID auto-populated
        """
        with self.transaction_manager.transaction():
            model_instance.save()
            return model_instance

    def create_many(self, model_instances: List[Model]) -> List[Model]:
        """
        Create multiple records in a single atomic transaction.
        
        Ensures all records are created successfully or none at all (atomicity).

        Args:
            model_instances (List[Model]): List of model instances to create

        Returns:
            List[Model]: List of created model instances
            
        Raises:
            Exception: If any record fails to create, all are rolled back
            
        Example:
            >>> users = [
            ...     User(username="alice", email="alice@test.com"),
            ...     User(username="bob", email="bob@test.com"),
            ...     User(username="charlie", email="charlie@test.com"),
            ... ]
            >>> created = repo.create_many(users)
            >>> len(created)  # 3
        """
        with self.transaction_manager.transaction():
            for instance in model_instances:
                instance.save()
            return model_instances

    def get_by_id(
        self, primary_key: Union[int, str], include_deleted: bool = False
    ) -> Optional[Model]:
        """
        Retrieve a single record by primary key (ID).
        
        By default, excludes soft-deleted records unless include_deleted=True.

        Args:
            primary_key (Union[int, str]): The primary key value to search for
            include_deleted (bool): Include soft-deleted records. Defaults to False.

        Returns:
            Model or None: The model instance if found, None otherwise
            
        Example:
            >>> user = repo.get_by_id(1)
            >>> if user:
            ...     print(user.username)
            
            >>> # Include soft-deleted records
            >>> deleted_user = repo.get_by_id(1, include_deleted=True)
        """
        with self.transaction_manager.transaction():
            query = self.model.select().where(self.model.id == primary_key)
            if not include_deleted and self.soft_delete_enabled:
                query = query.where(self.model.deleted_at.is_null())
            return query.first()

    def get_all(self, include_deleted: bool = False) -> List[Model]:
        """
        Retrieve all records from the table.
        
        By default, excludes soft-deleted records. Use include_deleted=True
        to retrieve all records including soft-deleted ones.

        Args:
            include_deleted (bool): Include soft-deleted records. Defaults to False.

        Returns:
            List[Model]: List of all matching model instances
            
        Example:
            >>> all_active_users = repo.get_all()
            >>> for user in all_active_users:
            ...     print(user.username)
            
            >>> all_users = repo.get_all(include_deleted=True)
            >>> total = len(all_users)
        """
        with self.transaction_manager.transaction():
            query = self.model.select()
            if not include_deleted and self.soft_delete_enabled:
                query = query.where(self.model.deleted_at.is_null())
            return list(query)

    def get_by_field(
        self, field_name: str, value: Any, include_deleted: bool = False
    ) -> List[Model]:
        """
        Retrieve records by a specific field value.

        Args:
            field_name: Name of the field to filter by
            value: Value to match
            include_deleted: Whether to include soft-deleted records

        Returns:
            List of matching model instances
        """
        with self.transaction_manager.transaction():
            field = getattr(self.model, field_name)
            query = self.model.select().where(field == value)
            if not include_deleted and self.soft_delete_enabled:
                query = query.where(self.model.deleted_at.is_null())
            return list(query)

    def update(
        self, primary_key: Union[int, str], value: Union[Tuple[str, Any], Model, Dict[str, Any]]
    ) -> int:
        """
        Update a record in the database.

        Args:
            primary_key: Primary key of the record to update
            value: Either a tuple of (field, new_value), a Model instance, or a dict of updates

        Returns:
            Number of rows affected
        """
        with self.transaction_manager.transaction():
            if isinstance(value, tuple):
                column, new_value = value
                field = getattr(self.model, column)
                query = self.model.update({field: new_value}).where(self.model.id == primary_key)
                return query.execute()

            elif isinstance(value, dict):
                update_data = {}
                for key, val in value.items():
                    field = getattr(self.model, key)
                    update_data[field] = val
                query = self.model.update(update_data).where(self.model.id == primary_key)
                return query.execute()

            elif isinstance(value, Model):
                update_data = DataTransformer.model_to_dict(value)
                # Remove id and timestamps to avoid conflicts
                update_data.pop("id", None)
                update_data.pop("created_at", None)
                # Update timestamp
                if hasattr(self.model, "updated_at"):
                    update_data["updated_at"] = datetime.utcnow()
                query = self.model.update(update_data).where(self.model.id == primary_key)
                return query.execute()

        return 0

    def delete(self, primary_key: Union[int, str]) -> int:
        """
        Delete a record (soft delete if enabled, hard delete otherwise).

        Args:
            primary_key: Primary key of the record to delete

        Returns:
            Number of rows affected
        """
        with self.transaction_manager.transaction():
            if self.soft_delete_enabled:
                query = self.model.update({self.model.deleted_at: datetime.utcnow()}).where(
                    self.model.id == primary_key
                )
                return query.execute()
            else:
                query = self.model.delete().where(self.model.id == primary_key)
                return query.execute()

    def delete_hard(self, primary_key: Union[int, str]) -> int:
        """
        Permanently delete a record (hard delete).

        Args:
            primary_key: Primary key of the record to delete

        Returns:
            Number of rows affected
        """
        with self.transaction_manager.transaction():
            query = self.model.delete().where(self.model.id == primary_key)
            return query.execute()

    def restore(self, primary_key: Union[int, str]) -> int:
        """
        Restore a soft-deleted record.

        Args:
            primary_key: Primary key of the record to restore

        Returns:
            Number of rows affected
        """
        if not self.soft_delete_enabled:
            raise ValueError("Soft delete is not enabled for this repository")

        with self.transaction_manager.transaction():
            query = self.model.update({self.model.deleted_at: None}).where(
                self.model.id == primary_key
            )
            return query.execute()

    def delete_all(self, soft: bool = True) -> int:
        """
        Delete all records.

        Args:
            soft: Whether to use soft delete (if enabled)

        Returns:
            Number of rows affected
        """
        with self.transaction_manager.transaction():
            if soft and self.soft_delete_enabled:
                query = self.model.update({self.model.deleted_at: datetime.utcnow()})
                return query.execute()
            else:
                query = self.model.delete()
                return query.execute()

    def count(self, include_deleted: bool = False) -> int:
        """
        Count total records.

        Args:
            include_deleted: Whether to include soft-deleted records

        Returns:
            Number of records
        """
        with self.transaction_manager.transaction():
            query = self.model.select()
            if not include_deleted and self.soft_delete_enabled:
                query = query.where(self.model.deleted_at.is_null())
            return query.count()

    def exists(self, primary_key: Union[int, str]) -> bool:
        """
        Check if a record exists.

        Args:
            primary_key: Primary key to check

        Returns:
            True if record exists, False otherwise
        """
        with self.transaction_manager.transaction():
            return self.get_by_id(primary_key) is not None

    def row_to_domain(self, row: Model) -> Optional[Model]:
        """
        Convert a raw row to a domain model.

        Args:
            row: Raw Peewee model instance

        Returns:
            Domain model instance or None
        """
        return DataTransformer.row_to_domain(row, self.model)

    def domain_to_dict(self, domain_object: Model) -> Dict[str, Any]:
        """
        Convert a domain object to a dictionary.

        Args:
            domain_object: Model instance

        Returns:
            Dictionary representation
        """
        return DataTransformer.domain_to_dict(domain_object)

    def domain_to_json(self, domain_object: Model) -> str:
        """
        Convert a domain object to JSON.
        
        Serializes a model instance to a JSON string representation.
        All datetime fields are automatically converted to ISO format strings
        using the DateTimeEncoder from utils.

        Args:
            domain_object (Model): Model instance to convert

        Returns:
            str: JSON string representation with datetime objects as ISO strings

        Example:
            >>> user = repo.get_by_id(1)
            >>> user_json = repo.domain_to_json(user)
            >>> print(user_json)
            '{"id": 1, "username": "alice", "created_at": "2026-02-08T10:30:00", ...}'
            
            >>> # Parse back to dictionary
            >>> import json
            >>> data = json.loads(user_json)
            >>> print(data['created_at'])  # ISO format string, not a datetime object
            2026-02-08T10:30:00
            
            See Also:
                domain_to_dict: Convert to dictionary instead of JSON string
                DataTransformer.domain_to_json: The underlying implementation
                DateTimeEncoder: Custom JSON encoder that handles datetime objects
        """
        return DataTransformer.domain_to_json(domain_object)

    @staticmethod
    def get_columns(table_name: str, database) -> List[str]:
        """
        Get list of column names for a given table.
        
        Args:
            table_name: Name of the table
            database: SqliteDatabase instance
            
        Returns:
            List of column names
            
        Example:
            columns = BaseRepository.get_columns("user", db._db)
            # Returns: ['id', 'username', 'email', 'created_at', 'updated_at', 'deleted_at']
        """
        try:
            # Get table metadata from database
            cursor = database.execute_sql(
                f"PRAGMA table_info({table_name})"
            )
            columns = [row[1] for row in cursor.fetchall()]
            return columns
        except Exception as e:
            return []
    
    @staticmethod
    def get_column_info(table_name: str, database) -> List[Dict[str, Any]]:
        """
        Get detailed column information for a given table.
        
        Args:
            table_name: Name of the table
            database: SqliteDatabase instance
            
        Returns:
            List of dictionaries with column details (cid, name, type, notnull, default, pk)
            
        Example:
            info = BaseRepository.get_column_info("user", db._db)
            # Returns detailed info including column type and primary key status
        """
        try:
            cursor = database.execute_sql(
                f"PRAGMA table_info({table_name})"
            )
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    "cid": row[0],
                    "name": row[1],
                    "type": row[2],
                    "notnull": bool(row[3]),
                    "default": row[4],
                    "pk": bool(row[5])
                })
            return columns
        except Exception as e:
            return []
    
    @staticmethod
    def get_primary_key(table_name: str, database) -> Optional[str]:
        """
        Get the primary key column name for a table.
        
        Args:
            table_name: Name of the table
            database: SqliteDatabase instance
            
        Returns:
            Primary key column name or None if not found
        """
        try:
            columns = BaseRepository.get_column_info(table_name, database)
            for col in columns:
                if col["pk"]:
                    return col["name"]
            return None
        except Exception:
            return None

    def __repr__(self) -> str:
        """String representation of the repository."""
        model_name = self.model.__name__ if self.model else "Unknown"
        return f"{self.__class__.__name__}(model={model_name})"

    def __str__(self) -> str:
        """User-friendly string representation."""
        model_name = self.model.__name__ if self.model else "Unknown"
        return f"Repository for {model_name}"
