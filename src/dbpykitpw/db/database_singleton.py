"""
Database Singleton - Centralized database connection and lifecycle management.

This module provides the DatabaseSingleton class which implements the singleton pattern
to manage a single database instance, model/repository registration, table creation,
and transaction management.

Example:
    Basic usage:
    
    >>> from dbpykitpw import DatabaseSingleton
    >>> db = DatabaseSingleton.get_instance()
    >>> db.configure("app.db", soft_delete_enabled=True)
    >>> db.connect()
    >>> db.create_tables()
    
    Transaction example:
    
    >>> with db.transaction:
    ...     # Atomic operations
    ...     user = User(username="alice", email="alice@test.com")
    ...     user.save()
    
    Raw SQL example:
    
    >>> results = db.execute_sql("SELECT * FROM user WHERE id > ?", (10,))

Attributes:
    _instance (DatabaseSingleton): Singleton instance
    _db (Optional[SqliteDatabase]): Database connection
    _repositories (Dict[str, Type[BaseRepository]]): Registered repositories
    _models (Dict[str, Type[Model]]): Registered models
    _soft_delete_enabled (bool): Global soft delete flag
"""

from peewee import SqliteDatabase, Model
from typing import Type, Dict, Optional, List, Any, Iterator


class _TransactionContextManager:
    """
    Internal context manager for database transactions.
    
    Wraps Peewee's atomic() context manager to provide clean transaction handling
    without requiring () to invoke the transaction property.
    """
    
    def __init__(self, db: Optional[SqliteDatabase]):
        """Initialize transaction context manager."""
        self.db = db
        self._atomic = None
    
    def __enter__(self):
        """Enter transaction context."""
        if self.db:
            self._atomic = self.db.atomic()
            return self._atomic.__enter__()
        raise RuntimeError("Database not configured. Call db.configure() first.")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context."""
        if self._atomic:
            return self._atomic.__exit__(exc_type, exc_val, exc_tb)


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
    def get_instance(cls) -> "DatabaseSingleton":
        """
        Get the singleton instance of DatabaseSingleton.
        
        Returns only one instance throughout the application lifecycle.
        Safe to call multiple times.
        
        Returns:
            DatabaseSingleton: The singleton instance
            
        Example:
            >>> db = DatabaseSingleton.get_instance()
            >>> db2 = DatabaseSingleton.get_instance()
            >>> db is db2  # True - same instance
        """
        return cls()

    def configure(self, db_file: str, soft_delete_enabled: bool = False) -> "DatabaseSingleton":
        """
        Configure the database with a file path.
        
        Must be called before any database operations. Sets up SQLite database
        connection and configures soft delete behavior.
        
        Args:
            db_file (str): Path to the SQLite database file.
                          Example: "app.db" or "./databases/mydb.sqlite"
            soft_delete_enabled (bool): Enable soft delete (logical deletion) globally.
                                       Defaults to False.

        Returns:
            DatabaseSingleton: Self for method chaining

        Raises:
            Exception: If database file cannot be created/accessed
            
        Example:
            >>> db = DatabaseSingleton.get_instance()
            >>> db.configure("myapp.db", soft_delete_enabled=True)
            >>> db.connect()
        """
        self._db = SqliteDatabase(db_file)
        self._soft_delete_enabled = soft_delete_enabled
        return self

    def connect(self) -> "DatabaseSingleton":
        """
        Establish database connection.
        
        Opens connection to SQLite database. Automatically checks if connection
        is already active before reconnecting.
        
        Returns:
            DatabaseSingleton: Self for method chaining
            
        Example:
            >>> db.configure("app.db").connect().create_tables()
        """
        if self._db and not self._db.is_connection_usable():
            self._db.connect()
        return self

    def disconnect(self) -> None:
        """
        Close the database connection.
        
        Safely closes the database connection. Should be called when shutting down
        the application or when no longer needed.
        
        Example:
            >>> db.disconnect()
        """
        if self._db:
            self._db.close()

    def register_model(
        self, 
        model_class: Type[Model], 
        repo_class: Type["BaseRepository"], 
        key: str
    ) -> None:
        """
        Register a model and its associated repository.
        
        Usually called automatically via @register_repository decorator.
        Sets the database on the model if not already set.
        
        Args:
            model_class (Type[Model]): The Peewee Model class to register
            repo_class (Type[BaseRepository]): The BaseRepository subclass
            key (str): Unique identifier key for this model/repo pair.
                      Example: "user_repo", "product_repo"
                      
        Example:
            >>> from models.user import User
            >>> from repos.user_repo import UserRepository
            >>> db.register_model(User, UserRepository, "user_repo")
        """
        # Set database on model if not already set
        if self._db and (not hasattr(model_class._meta, 'database') or model_class._meta.database is None):
            model_class._meta.database = self._db
        
        self._models[key] = model_class
        self._repositories[key] = repo_class

    def create_tables(self) -> None:
        """
        Create all registered model tables in the database.
        
        Iterates through all registered models and creates their tables if they
        don't already exist. Must be called after registering models and before
        using them for database operations.
        
        Raises:
            Exception: If database is not configured or connected
            
        Example:
            >>> db.configure("app.db").connect()
            >>> db.create_tables()  # Creates all registered model tables
        """
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
        
        Returns the repository class (not an instance). Must be instantiated
        with database before use.
        
        Args:
            key (str): The registration key defining which repository to retrieve

        Returns:
            Type[BaseRepository] or None: The repository class or None if not found
            
        Example:
            >>> UserRepoClass = db.get_repository("user_repo")
            >>> user_repo = UserRepoClass(db._db)  # Instantiate
            >>> users = user_repo.get_all()
        """
        return self._repositories.get(key)

    def get_model(self, key: str) -> Optional[Type[Model]]:
        """
        Retrieve a registered model class by key.
        
        Args:
            key (str): The registration key

        Returns:
            Type[Model] or None: The model class or None if not found
            
        Example:
            >>> User = db.get_model("user")
            >>> user = User(username="alice", email="alice@test.com")
        """
        return self._models.get(key)

    def get_all_models(self) -> Dict[str, Type[Model]]:
        """
        Get all registered models.
        
        Returns:
            Dict[str, Type[Model]]: Dictionary of all registered models keyed by registration key
            
        Example:
            >>> all_models = db.get_all_models()
            >>> for key, model_class in all_models.items():
            ...     print(f"{key}: {model_class.__name__}")
        """
        return self._models.copy()

    def get_all_repositories(self) -> Dict[str, Type["BaseRepository"]]:
        """
        Get all registered repositories.
        
        Returns:
            Dict[str, Type[BaseRepository]]: Dictionary of all registered repository classes
        """
        return self._repositories.copy()

    @property
    def transaction(self) -> _TransactionContextManager:
        """
        Property for atomic transactions.
        
        Returns a context manager for atomic database transactions. Use without () 
        in the `with` statement.
        
        Ensures all database operations within the context are atomic.
        If any error occurs, all changes are rolled back.
        
        Returns:
            _TransactionContextManager: Context manager for transaction handling

        Raises:
            RuntimeError: If database is not configured
            Exception: Any exception in the with block causes rollback
            
        Example:
            >>> try:
            ...     with db.transaction as tx:
            ...         user1 = User(username="alice", email="alice@test.com")
            ...         user1.save()
            ...         user2 = User(username="bob", email="bob@test.com")
            ...         user2.save()
            ...         # Both users created atomically
            ... except Exception as e:
            ...     print(f"Transaction failed: {e}")
            ...     # Both creates are rolled back
        """
        return _TransactionContextManager(self._db)

    def execute_sql(self, sql: str, params: Optional[tuple] = None) -> List[Any]:
        """
        Execute raw SQL query and return all results.
        
        Allows direct SQL execution for complex queries not available through ORM.
        
        Args:
            sql (str): SQL query string with placeholders for parameters.
                      Example: "SELECT * FROM user WHERE id > ?"
            params (tuple, optional): Query parameters. Default is None.
                                     Example: (10,)

        Returns:
            List[Any]: List of query results. Empty list if no results.
            
        Raises:
            Exception: If SQL syntax is invalid or execution fails
            
        Example:
            >>> results = db.execute_sql(
            ...     "SELECT id, username FROM user WHERE active = ?",
            ...     (True,)
            ... )
            >>> for row in results:
            ...     print(row)
        """
        if self._db:
            with self._db.connection_context():
                result = self._db.execute_sql(sql, params or ())
                return result.fetchall()
        return []

    def execute_sql_single(self, sql: str, params: Optional[tuple] = None) -> Optional[Any]:
        """
        Execute raw SQL query and return only the first result.
        
        Convenience method when you expect a single row result.
        
        Args:
            sql (str): SQL query string
            params (tuple, optional): Query parameters. Default is None.

        Returns:
            Any or None: First result row or None if no results
            
        Example:
            >>> result = db.execute_sql_single(
            ...     "SELECT username FROM user WHERE id = ?",
            ...     (1,)
            ... )
            >>> if result:
            ...     print(f"Username: {result[0]}")
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
