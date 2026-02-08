"""
Base Repository - Generic repository for CRUD operations with transaction support.
"""

from peewee import Model
from datetime import datetime
from typing import Type, Union, Optional, List, Tuple, Any, Dict

from dbpykitpw.db.transaction_manager import TransactionManager
from dbpykitpw.utils.data_transformer import DataTransformer


class BaseRepository:
    """
    Base repository class providing generic CRUD operations.
    Supports soft delete, transactions, and data transformations.
    """

    model: Optional[Type[Model]] = None
    soft_delete_field: Optional[str] = "deleted_at"
    soft_delete_enabled: bool = False

    def __init__(self, database):
        """
        Initialize the repository.

        Args:
            database: SqliteDatabase instance from DatabaseSingleton
        """
        self.db = database
        self.transaction_manager = TransactionManager(database)

    def create(self, model_instance: Model) -> Model:
        """
        Create a new record in the database.

        Args:
            model_instance: Instance of the model to create

        Returns:
            The created model instance
        """
        with self.transaction_manager.transaction():
            model_instance.save()
            return model_instance

    def create_many(self, model_instances: List[Model]) -> List[Model]:
        """
        Create multiple records in the database.

        Args:
            model_instances: List of model instances to create

        Returns:
            List of created model instances
        """
        with self.transaction_manager.transaction():
            for instance in model_instances:
                instance.save()
            return model_instances

    def get_by_id(
        self, primary_key: Union[int, str], include_deleted: bool = False
    ) -> Optional[Model]:
        """
        Retrieve a record by primary key.

        Args:
            primary_key: The primary key value
            include_deleted: Whether to include soft-deleted records

        Returns:
            The model instance or None if not found
        """
        with self.transaction_manager.transaction():
            query = self.model.select().where(self.model.id == primary_key)
            if not include_deleted and self.soft_delete_enabled:
                query = query.where(self.model.deleted_at.is_null())
            return query.first()

    def get_all(self, include_deleted: bool = False) -> List[Model]:
        """
        Retrieve all records.

        Args:
            include_deleted: Whether to include soft-deleted records

        Returns:
            List of all model instances
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

        Args:
            domain_object: Model instance

        Returns:
            JSON string representation
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
