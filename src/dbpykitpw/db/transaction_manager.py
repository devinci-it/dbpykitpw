"""
Transaction Manager - Handles database transactions.
"""

from peewee import SqliteDatabase
from contextlib import contextmanager
from typing import Optional


class TransactionManager:
    """
    Context manager for handling database transactions.
    Provides atomic transaction support with error handling.
    """

    def __init__(self, db: SqliteDatabase):
        """
        Initialize the TransactionManager.

        Args:
            db: SqliteDatabase instance
        """
        self.db = db

    @contextmanager
    def transaction(self):
        """
        Context manager for atomic database transactions.

        Yields:
            The database connection during the transaction

        Raises:
            Exception: If transaction fails, exception is re-raised
        """
        try:
            with self.db.atomic():
                yield self.db
        except Exception as e:
            raise

    @contextmanager
    def savepoint(self, name: str = "sp"):
        """
        Create a savepoint within a transaction.

        Args:
            name: Name for the savepoint

        Yields:
            The database connection
        """
        try:
            with self.db.savepoint(name):
                yield self.db
        except Exception as e:
            raise

    def __repr__(self) -> str:
        """String representation of TransactionManager."""
        db_file = self.db.database if self.db else "Not configured"
        return f"TransactionManager(db={db_file})"

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"TransactionManager for {self.db.database}"
