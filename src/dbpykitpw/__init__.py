"""
dbpykitpw - Database Python Kit with Peewee and Workflows
A lightweight ORM toolkit providing database management, repositories, and data transformation utilities.
"""

from .db import DatabaseSingleton, TransactionManager
from .models import BaseModel
from .repositories import BaseRepository
from .utils import DataTransformer, register_repository
from .cli import DemoPublisher

__version__ = "1.0.0"
__author__ = "dbpykitpw"

__all__ = [
    # Database
    "DatabaseSingleton",
    "TransactionManager",
    # Models
    "BaseModel",
    # Repositories
    "BaseRepository",
    # Utils
    "DataTransformer",
    "register_repository",
    # CLI
    "DemoPublisher",
]
