# dbpykitpw Wiki - Database Python Kit with Peewee and Workflows

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Core Concepts](#core-concepts)
6. [Detailed Flow](#detailed-flow)
7. [Usage Guide](#usage-guide)
8. [API Reference](#api-reference)
9. [Examples](#examples)
10. [Best Practices](#best-practices)

---

## Overview

**dbpykitpw** is a lightweight ORM toolkit built on top of Peewee that provides:
- **Singleton Database Management**: Centralized database connection and lifecycle management
- **Repository Pattern**: Generic CRUD operations with transaction support
- **Soft Delete Support**: Built-in soft delete (logical delete) with restore functionality
- **Data Transformation**: Seamless conversion between models, dictionaries, and JSON
- **Transaction Management**: Context managers for atomic database operations
- **Demo Templates**: Pre-built examples for quick project startup

### Key Features
- ✓ Zero-configuration database setup
- ✓ Automatic table creation for registered models
- ✓ Soft delete and restoration
- ✓ Type-safe repository operations
- ✓ Comprehensive string representations (`__repr__` and `__str__`)
- ✓ Built-in data transformation utilities
- ✓ Decorator-based model/repository registration

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Your Application                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ├─→ Repository Layer
                       │   ├─ UserRepository
                       │   └─ (Custom Repositories)
                       │
                       ├─→ Model Layer
                       │   ├─ User (BaseModel)
                       │   └─ (Custom Models)
                       │
                       └─→ Database Layer
                           │
                           ├─ DatabaseSingleton
                           │   ├─ Configuration
                           │   ├─ Connection Management
                           │   ├─ Model Registration
                           │   └─ Table Creation
                           │
                           ├─ TransactionManager
                           │   └─ Atomic Operations
                           │
                           └─ Peewee ORM
                               └─ SQLite Database
```

### Package Structure

```
dbpykitpw/
├── db/
│   ├── __init__.py
│   ├── database_singleton.py      # Core database management
│   └── transaction_manager.py      # Transaction context managers
├── models/
│   ├── __init__.py
│   ├── base_model.py              # Base model with common fields
│   └── (model implementations)
├── repositories/
│   ├── __init__.py
│   ├── base_repository.py         # Generic CRUD operations
│   └── (repository implementations)
├── utils/
│   ├── __init__.py
│   ├── data_transformer.py        # Model ↔ Dict ↔ JSON conversion
│   └── decorators.py              # @register_repository decorator
├── cli/
│   ├── __init__.py
│   └── demo_publisher.py          # CLI tool for demo distribution
├── static/
│   └── demo/
│       ├── __init__.py
│       ├── user_model.py          # Example User model
│       ├── user_repo.py           # Example UserRepository
│       └── demo.py                # Comprehensive feature demo
└── __init__.py
```

---

## Installation

### From Source (Development)

```bash
# Clone the repository
cd /opt/PyTools/dbpykitpw

# Install in development mode
pip install -e .

# Or using pipenv
pipenv install -e .
```

### Dependencies

```
peewee>=3.14.0
```

### CLI Tools

After installation, you get the `pykitdbdemo` command:

```bash
# Publish demo files to current directory
pykitdbdemo

# Publish to specific directory
pykitdbdemo -o /path/to/my/project

# Force overwrite existing demo
pykitdbdemo --force

# Verbose output
pykitdbdemo -v
```

---

## Quick Start

### 1. Initialize Database

```python
from dbpykitpw import DatabaseSingleton

# Get singleton instance
db = DatabaseSingleton.get_instance()

# Configure database
db.configure("myapp.db", soft_delete_enabled=True)

# Connect
db.connect()

# Create tables for registered models
db.create_tables()
```

### 2. Define a Model

```python
from dbpykitpw import BaseModel
from peewee import CharField, DateTimeField

class User(BaseModel):
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=255, unique=True)
    full_name = CharField(max_length=255)
    
    class Meta:
        table_name = "user"
```

### 3. Create a Repository

```python
from dbpykitpw import BaseRepository, register_repository

@register_repository("user_repo")
class UserRepository(BaseRepository):
    model = User
    soft_delete_enabled = True
    
    def get_by_email(self, email: str):
        return self.get_by_field("email", email)
```

### 4. Use in Your Application

```python
from dbpykitpw import DatabaseSingleton

# Initialize
db = DatabaseSingleton.get_instance()
db.configure("app.db", soft_delete_enabled=True)
db.connect()
db.create_tables()

# Get repository
user_repo = UserRepository(db._db)

# Create
user = User(username="alice", email="alice@example.com", full_name="Alice")
user_repo.create(user)

# Read
user = user_repo.get_by_email("alice@example.com")

# Update
user_repo.update(user.id, ("full_name", "Alice Smith"))

# Delete (soft)
user_repo.delete(user.id)

# Restore
user_repo.restore(user.id)
```

---

## Core Concepts

### 1. DatabaseSingleton

**Purpose**: Manages database connection, lifecycle, model/repository registration, and table creation.

**Key Methods**:
- `get_instance()` - Get singleton instance
- `configure(db_file, soft_delete_enabled)` - Configure database
- `connect()` - Establish connection
- `disconnect()` - Close connection
- `register_model(model_class, repo_class, key)` - Register model/repository pair
- `create_tables()` - Create tables for all registered models
- `transaction()` - Context manager for atomic operations

**Lifecycle**:
```
1. Get instance (singleton)
   ↓
2. Configure with database file
   ↓
3. Connect to database
   ↓
4. Register models (via @register_repository)
   ↓
5. Create tables
   ↓
6. Use repositories for CRUD
   ↓
7. Disconnect when done
```

### 2. BaseModel

**Purpose**: Base class for all models with common fields and functionality.

**Built-in Fields**:
- `created_at` - Auto-populated creation timestamp
- `updated_at` - Auto-populated update timestamp

**Method**:
- `save()` - Overridden to auto-update `updated_at`

### 3. BaseRepository

**Purpose**: Generic CRUD operations with transaction support.

**Methods**:
- `create(model_instance)` - Create single record
- `create_many(model_instances)` - Create multiple records
- `get_by_id(pk, include_deleted)` - Retrieve by primary key
- `get_all(include_deleted)` - Retrieve all records
- `get_by_field(field_name, value)` - Retrieve by any field
- `update(pk, update_value)` - Update record
- `delete(pk)` - Soft delete (or hard delete if not enabled)
- `delete_hard(pk)` - Force hard delete
- `restore(pk)` - Restore soft-deleted record
- `count(include_deleted)` - Count records

### 4. DataTransformer

**Purpose**: Convert between different data representations.

**Conversions**:
- Model ↔ Dictionary (`model_to_dict`, `dict_to_model`)
- Model ↔ JSON (`model_to_json`, `json_to_model`)
- Dict ↔ JSON (`dict_to_json`, `json_to_dict`)

### 5. TransactionManager

**Purpose**: Handle database transactions with ACID guarantees.

**Methods**:
- `transaction()` - Atomic transaction context manager
- `savepoint(name)` - Named savepoint within transaction

---

## Detailed Flow

### Flow 1: Application Startup

```
Application Start
    ↓
Import package
    ↓
DatabaseSingleton.__init__()
    ├─ _instance = None
    ├─ _db = None
    ├─ _repositories = {}
    └─ _models = {}
    ↓
Import models with @register_repository decorator
    ├─ @register_repository("user_repo")
    │   ↓
    │   decorator calls register_repository(key)
    │   ├─ Gets DatabaseSingleton instance
    │   └─ Calls db.register_model(User, UserRepository, "user_repo")
    │       └─ Stores in _models and _repositories
    ↓
db = DatabaseSingleton.get_instance()
    ↓
db.configure("app.db", soft_delete_enabled=True)
    ├─ Creates SqliteDatabase instance
    ├─ Sets soft_delete_enabled flag
    └─ Returns self (for chaining)
    ↓
db.connect()
    ├─ Checks if connection is usable
    ├─ Connects if needed
    └─ Returns self (for chaining)
    ↓
db.create_tables()
    ├─ Iterates through _models
    ├─ Ensures each model has database assigned
    │   └─ model._meta.database = self._db
    └─ Calls db.create_tables(models.values())
```

### Flow 2: Creating a Record

```
user = User(username="alice", email="alice@example.com", full_name="Alice")
    ↓
user_repo = UserRepository(db._db)
    ├─ Initializes BaseRepository
    ├─ Sets self.db = database
    └─ Creates TransactionManager(database)
    ↓
user_repo.create(user)
    ├─ Starts transaction: with transaction_manager.transaction()
    ├─ Calls user.save()
    │   ├─ Sets created_at = datetime.utcnow()
    │   ├─ Sets updated_at = datetime.utcnow()
    │   └─ Inserts into database
    ├─ Commits transaction
    └─ Returns user instance
```

### Flow 3: Updating a Record

```
user_repo.update(user_id, ("full_name", "Alice Smith"))
    ├─ Starts transaction
    ├─ Gets field: getattr(User, "full_name")
    ├─ Creates update query
    │   └─ User.update({User.full_name: "Alice Smith"}).where(User.id == user_id)
    ├─ Executes query
    ├─ Commits transaction
    └─ Returns rows affected
```

### Flow 4: Soft Delete

```
user_repo.delete(user_id)
    ├─ Check: if soft_delete_enabled
    ├─ Starts transaction
    ├─ Updates deleted_at field
    │   └─ User.update({User.deleted_at: datetime.utcnow()}).where(User.id == user_id)
    ├─ Commits transaction
    └─ Returns rows affected

# Record is now "soft deleted" - logically removed but still in database
# get_all() and similar methods exclude soft-deleted records by default
```

### Flow 5: Data Transformation

```
# Model → Dictionary
user_dict = DataTransformer.model_to_dict(user)
    └─ Returns user.__data__  # Internal Peewee dict

# Model → JSON
user_json = DataTransformer.model_to_json(user)
    └─ Returns json.dumps(user.__data__, default=str)

# Repository convenience methods
user_dict = user_repo.domain_to_dict(user)
    └─ Calls DataTransformer.domain_to_dict(user)
        └─ Returns user.__data__

user_json = user_repo.domain_to_json(user)
    └─ Calls DataTransformer.domain_to_json(user)
        └─ Returns json.dumps(user.__data__, default=str)
```

---

## Usage Guide

### Setting Up a New Project

#### Step 1: Create Your Models

```python
# models/user.py
from dbpykitpw import BaseModel
from peewee import CharField, BooleanField, DateTimeField

class User(BaseModel):
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=255, unique=True)
    full_name = CharField(max_length=255)
    is_active = BooleanField(default=True)
    deleted_at = DateTimeField(null=True)
    
    class Meta:
        table_name = "user"
    
    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}')"
    
    def __str__(self):
        return f"User: {self.username}"
```

#### Step 2: Create Your Repositories

```python
# repositories/user_repo.py
from dbpykitpw import BaseRepository, register_repository
from models.user import User

@register_repository("user_repo")
class UserRepository(BaseRepository):
    model = User
    soft_delete_enabled = True
    
    def get_by_username(self, username):
        return self.get_by_field("username", username)
    
    def get_by_email(self, email):
        return self.get_by_field("email", email)
    
    def get_active_users(self):
        with self.transaction_manager.transaction():
            query = User.select().where(
                (User.deleted_at.is_null()) & (User.is_active == True)
            )
            return list(query)
```

#### Step 3: Initialize in Your Application

```python
# main.py
from dbpykitpw import DatabaseSingleton
from repositories.user_repo import UserRepository

def setup_database():
    """Initialize database during app startup."""
    db = DatabaseSingleton.get_instance()
    db.configure("app.db", soft_delete_enabled=True)
    db.connect()
    db.create_tables()
    return db

def initialize_repositories(db):
    """Get repository instances."""
    return {
        "user_repo": UserRepository(db._db),
    }

if __name__ == "__main__":
    # Setup
    db = setup_database()
    repos = initialize_repositories(db)
    user_repo = repos["user_repo"]
    
    # Use
    user = User(username="alice", email="alice@example.com", full_name="Alice")
    user_repo.create(user)
    
    # Find
    alice = user_repo.get_by_username("alice")
    print(alice)
    
    # Cleanup
    db.disconnect()
```

### Advanced Usage

#### Transaction Management

```python
db = DatabaseSingleton.get_instance()

# Atomic transaction
try:
    with db.transaction() as txn:
        user1 = User(username="alice", email="alice@example.com", full_name="Alice")
        user1.save()
        
        user2 = User(username="bob", email="bob@example.com", full_name="Bob")
        user2.save()
        
        # If any error occurs, both are rolled back
        print("Transaction successful")
except Exception as e:
    print(f"Transaction failed: {e}")
```

#### Soft Delete with Restore

```python
user_repo = UserRepository(db._db)

# Create user
user = User(username="alice", email="alice@example.com", full_name="Alice")
user_repo.create(user)

# Soft delete
user_repo.delete(user.id)

# User is deleted but still in database
deleted_user = user_repo.get_by_id(user.id, include_deleted=True)
print(deleted_user)  # Returns the deleted user

# Active users exclude this
active_users = user_repo.get_all()  # Doesn't include deleted user

# Restore
user_repo.restore(user.id)
restored_user = user_repo.get_by_id(user.id)
print(restored_user)  # Now available in get_all()
```

#### Data Export

```python
from dbpykitpw import DataTransformer
import json

user = user_repo.get_by_username("alice")

# To dictionary
user_dict = user_repo.domain_to_dict(user)
print(user_dict)

# To JSON
user_json = user_repo.domain_to_json(user)
json_obj = json.loads(user_json)

# Export multiple users
users = user_repo.get_all()
json_array = json.dumps([
    json.loads(user_repo.domain_to_json(u)) for u in users
])
```

---

## Query Methods Reference

### Requirements & Setup

| Requirement | Status | Description |
|-------------|--------|-------------|
| Database Initialized | **REQUIRED** | `db = DatabaseSingleton.get_instance()` |
| Database Configured | **REQUIRED** | `db.configure("app.db", soft_delete_enabled=True)` |
| Tables Created | **REQUIRED** | `db.create_tables()` |
| Repository Instantiated | **REQUIRED** | `repo = RepoClass(db._db)` |
| Models Registered | **Automatic** | Via `@register_repository` decorator |

### Basic Setup Flow

```python
# 1. Initialize Singleton
from dbpykitpw import DatabaseSingleton
db = DatabaseSingleton.get_instance()

# 2. Configure
db.configure("app.db", soft_delete_enabled=True)
db.connect()
db.create_tables()

# 3. Access Repository
from repositories.user_repo import UserRepository
user_repo = UserRepository(db._db)

# 4. Use Repository Methods
user = user_repo.get_by_id(1)
```

### Query Method Reference Table

| Query Type | Method | Returns | Parameters | Basic Flow |
|-----------|--------|---------|-----------|-----------|
| **Get by ID** | `get_by_id(id)` | `Model \| None` | `id`: primary key value | `repo.get_by_id(1)` |
| **Get by ID (with deleted)** | `get_by_id(id, include_deleted=True)` | `Model \| None` | `id`, `include_deleted` | `repo.get_by_id(1, include_deleted=True)` |
| **Get All** | `get_all()` | `List[Model]` | (none) | `user_list = repo.get_all()` |
| **Get All (with deleted)** | `get_all(include_deleted=True)` | `List[Model]` | `include_deleted` | `repo.get_all(include_deleted=True)` |
| **Get by Field** | `get_by_field(field_name, value)` | `List[Model]` | `field_name`, `value` | `repo.get_by_field("email", "test@test.com")` |
| **Count Records** | `count()` | `int` | (none) | `total = repo.count()` |
| **Count (with deleted)** | `count(include_deleted=True)` | `int` | `include_deleted` | `total_all = repo.count(include_deleted=True)` |
| **Check Exists** | `exists(id)` | `bool` | `id` | `if repo.exists(user_id): ...` |
| **Create Record** | `create(model_instance)` | `Model` | `model_instance` | `user_repo.create(user)` |
| **Create Many** | `create_many(list)` | `List[Model]` | `model_instances` | `user_repo.create_many([user1, user2])` |
| **Update Field** | `update(id, tuple)` | `int` (rows affected) | `id`, `(field_name, value)` | `repo.update(1, ("name", "Alice"))` |
| **Update from Dict** | `update(id, dict)` | `int` (rows affected) | `id`, `{field: value}` | `repo.update(1, {"name": "Alice"})` |
| **Update from Model** | `update(id, model)` | `int` (rows affected) | `id`, `Model` instance | `repo.update(1, updated_user)` |
| **Soft Delete** | `delete(id)` | `int` (rows affected) | `id` | `repo.delete(user_id)` |
| **Hard Delete** | `delete_hard(id)` | `int` (rows affected) | `id` | `repo.delete_hard(user_id)` |
| **Delete All** | `delete_all(soft=True)` | `int` (rows affected) | `soft` | `repo.delete_all()` |
| **Restore** | `restore(id)` | `int` (rows affected) | `id` | `repo.restore(deleted_user_id)` |

### Data Transformation Methods

| Conversion Type | Method | Input | Output | Example |
|-----------------|--------|-------|--------|---------|
| **Model → Dict** | `domain_to_dict(model)` | `Model` instance | `Dict[str, Any]` | `user_dict = repo.domain_to_dict(user)` |
| **Model → JSON** | `domain_to_json(model)` | `Model` instance | `JSON string` | `user_json = repo.domain_to_json(user)` |
| **Dict → Model** | `dict_to_model(dict, ModelClass)` | `Dict`, Model class | `Model` instance | `user = DataTransformer.dict_to_model(data, User)` |
| **JSON → Model** | `json_to_model(json, ModelClass)` | `JSON string`, Model class | `Model` instance | `user = DataTransformer.json_to_model(json_str, User)` |
| **Dict → JSON** | `dict_to_json(dict)` | `Dict` | `JSON string` | `json_str = DataTransformer.dict_to_json(user_dict)` |
| **JSON → Dict** | `json_to_dict(json)` | `JSON string` | `Dict` | `dict = DataTransformer.json_to_dict(json_str)` |

### Schema Introspection Methods

| Method | Purpose | Parameters | Returns | Example |
|--------|---------|-----------|---------|---------|
| **get_columns** | Get list of column names | `table_name`, `database` | `List[str]` | `cols = BaseRepository.get_columns("user", db._db)` |
| **get_column_info** | Get detailed column info | `table_name`, `database` | `List[Dict]` | `info = BaseRepository.get_column_info("user", db._db)` |
| **get_primary_key** | Get primary key column | `table_name`, `database` | `str \| None` | `pk = BaseRepository.get_primary_key("user", db._db)` |

### Common Query Patterns

#### Pattern 1: Create and Retrieve

```python
# Setup
db = DatabaseSingleton.get_instance()
db.configure("app.db", soft_delete_enabled=True)
db.connect()
db.create_tables()

from repositories.user_repo import UserRepository
user_repo = UserRepository(db._db)

# Create
user = User(username="alice", email="alice@example.com")
created_user = user_repo.create(user)

# Retrieve
found_user = user_repo.get_by_id(created_user.id)
```

#### Pattern 2: Find by Custom Field

```python
# Single match (returns list)
results = user_repo.get_by_field("email", "alice@example.com")
if results:
    user = results[0]
    print(f"Found: {user}")

# Check existence
if user_repo.exists(user.id):
    print("User exists")
```

#### Pattern 3: Update Record

```python
# Using tuple
user_repo.update(user.id, ("full_name", "Alice Smith"))

# Using dictionary
user_repo.update(user.id, {
    "full_name": "Alice Smith",
    "is_active": True
})

# Using updated model instance
user.full_name = "Alice Smith"
user_repo.update(user.id, user)
```

#### Pattern 4: Soft Delete + Restore

```python
# Soft delete - record hidden but not removed
user_repo.delete(user.id)

# Retrieve with deleted (include_deleted=True)
deleted_user = user_repo.get_by_id(user.id, include_deleted=True)

# Active users only (default behavior)
active_users = user_repo.get_all()  # Excludes deleted

# Restore
user_repo.restore(user.id)
restored = user_repo.get_by_id(user.id)  # Now accessible
```

#### Pattern 5: Batch Operations

```python
# Create multiple
users = [
    User(username="alice", email="alice@test.com"),
    User(username="bob", email="bob@test.com"),
    User(username="charlie", email="charlie@test.com"),
]
created = user_repo.create_many(users)

# Get all
all_users = user_repo.get_all()

# Count
total = user_repo.count()
print(f"Total active users: {total}")
```

#### Pattern 6: Data Export

```python
from dbpykitpw import DataTransformer
import json

# Single record to JSON
user = user_repo.get_by_id(1)
user_json = user_repo.domain_to_json(user)

# Multiple records to JSON array
all_users = user_repo.get_all()
users_json = json.dumps([
    json.loads(user_repo.domain_to_json(u)) for u in all_users
])

# Single record to dict
user_dict = user_repo.domain_to_dict(user)
```

---

## API Reference

### DatabaseSingleton

```python
class DatabaseSingleton:
    
    @classmethod
    def get_instance() -> DatabaseSingleton
    
    def configure(self, db_file: str, soft_delete_enabled: bool = False) -> DatabaseSingleton
    
    def connect(self) -> DatabaseSingleton
    
    def disconnect(self) -> None
    
    def register_model(
        self, 
        model_class: Type[Model], 
        repo_class: Type[BaseRepository], 
        key: str
    ) -> None
    
    def create_tables(self) -> None
    
    def get_repository(self, key: str) -> Optional[Type[BaseRepository]]
    
    def get_model(self, key: str) -> Optional[Type[Model]]
    
    def get_all_models(self) -> Dict[str, Type[Model]]
    
    def get_all_repositories(self) -> Dict[str, Type[BaseRepository]]
    
    @contextmanager
    def transaction(self) -> Iterator[SqliteDatabase]
    
    def execute_sql(self, sql: str, params: Optional[tuple] = None) -> List[Any]
    
    def __repr__(self) -> str
    def __str__(self) -> str
```

### BaseRepository

```python
class BaseRepository:
    model: Type[Model] = None
    soft_delete_enabled: bool = False
    
    def __init__(self, database)
    
    def create(self, model_instance: Model) -> Model
    
    def create_many(self, model_instances: List[Model]) -> List[Model]
    
    def get_by_id(self, primary_key, include_deleted: bool = False) -> Optional[Model]
    
    def get_all(self, include_deleted: bool = False) -> List[Model]
    
    def get_by_field(self, field_name: str, value: Any, include_deleted: bool = False) -> List[Model]
    
    def update(self, primary_key, value: Union[Tuple, Model, Dict]) -> int
    
    def delete(self, primary_key) -> int
    
    def delete_hard(self, primary_key) -> int
    
    def restore(self, primary_key) -> int
    
    def delete_all(self, soft: bool = True) -> int
    
    def count(self, include_deleted: bool = False) -> int
    
    def exists(self, primary_key) -> bool
    
    def __repr__(self) -> str
    def __str__(self) -> str
```

### DataTransformer

```python
class DataTransformer:
    
    @staticmethod
    def model_to_dict(model: Model) -> Dict[str, Any]
    
    @staticmethod
    def model_to_json(model: Model) -> str
    
    @staticmethod
    def row_to_domain(row: Optional[Model], domain_class: Type[Model]) -> Optional[Model]
    
    @staticmethod
    def domain_to_dict(domain_object: Model) -> Dict[str, Any]
    
    @staticmethod
    def domain_to_json(domain_object: Model) -> str
    
    @staticmethod
    def dict_to_model(data: Dict[str, Any], model_class: Type[Model]) -> Model
    
    @staticmethod
    def json_to_model(json_str: str, model_class: Type[Model]) -> Model
    
    @staticmethod
    def json_to_dict(json_str: str) -> Dict[str, Any]
    
    @staticmethod
    def dict_to_json(data: Dict[str, Any]) -> str
```

---

## Examples

### Example 1: User Management System

```python
from dbpykitpw import DatabaseSingleton, BaseModel, BaseRepository, register_repository
from peewee import CharField, DateTimeField, BooleanField
from datetime import datetime

# 1. Define Model
class User(BaseModel):
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=255, unique=True)
    full_name = CharField(max_length=255)
    is_active = BooleanField(default=True)
    deleted_at = DateTimeField(null=True)
    
    class Meta:
        table_name = "user"

# 2. Define Repository
@register_repository("user_repo")
class UserRepository(BaseRepository):
    model = User
    soft_delete_enabled = True
    
    def get_by_email(self, email):
        return self.get_by_field("email", email)
    
    def deactivate(self, user_id):
        return self.update(user_id, ("is_active", False))

# 3. Use in Application
db = DatabaseSingleton.get_instance()
db.configure("users.db", soft_delete_enabled=True)
db.connect()
db.create_tables()

user_repo = UserRepository(db._db)

# Create
user = User(username="alice", email="alice@example.com", full_name="Alice")
user_repo.create(user)

# Read
alice = user_repo.get_by_email("alice@example.com")
print(f"Found: {alice}")

# Update
user_repo.update(alice.id, ("full_name", "Alice Smith"))

# Deactivate
user_repo.deactivate(alice.id)

# Check status
updated = user_repo.get_by_id(alice.id)
print(f"Is active: {updated.is_active}")

db.disconnect()
```

### Example 2: Batch Operations with Transactions

```python
db = DatabaseSingleton.get_instance()
db.configure("batch.db")
db.connect()
db.create_tables()

user_repo = UserRepository(db._db)

# Create multiple users in transaction
users_data = [
    {"username": "user1", "email": "user1@example.com", "full_name": "User One"},
    {"username": "user2", "email": "user2@example.com", "full_name": "User Two"},
    {"username": "user3", "email": "user3@example.com", "full_name": "User Three"},
]

try:
    with db.transaction():
        for data in users_data:
            user = User(**data)
            user_repo.create(user)
    print(f"✓ Created {len(users_data)} users")
except Exception as e:
    print(f"✗ Failed: {e}")

# Verify
count = user_repo.count()
print(f"Total users: {count}")

db.disconnect()
```

### Example 3: Data Export

```python
from dbpykitpw import DataTransformer
import json

db = DatabaseSingleton.get_instance()
db.configure("export.db")
db.connect()
db.create_tables()

user_repo = UserRepository(db._db)

# Setup data
user = User(username="alice", email="alice@example.com", full_name="Alice Smith")
user_repo.create(user)

# Export single user to JSON
user = user_repo.get_by_username("alice")
user_json = user_repo.domain_to_json(user)
print("User JSON:", user_json)

# Export all users
all_users = user_repo.get_all()
users_json = json.dumps([
    json.loads(user_repo.domain_to_json(u)) for u in all_users
], indent=2)
print("All Users JSON:")
print(users_json)

db.disconnect()
```

---

## Best Practices

### 1. **Always Use Transactions for Multiple Operations**

```python
# ✓ Good: Atomic operation
with db.transaction():
    user1 = User(username="alice", email="alice@example.com", full_name="Alice")
    user1.save()
    user2 = User(username="bob", email="bob@example.com", full_name="Bob")
    user2.save()

# ✗ Bad: No transaction, not atomic
user1 = User(username="alice", email="alice@example.com", full_name="Alice")
user1.save()
user2 = User(username="bob", email="bob@example.com", full_name="Bob")
user2.save()
```

### 2. **Implement Custom Repository Methods**

```python
# ✓ Good: Custom repository method encapsulates logic
class UserRepository(BaseRepository):
    def get_by_domain(self, domain):
        email_suffix = f"@{domain}"
        with self.transaction_manager.transaction():
            query = User.select().where(User.email.endswith(email_suffix))
            return list(query)

# ✗ Bad: Logic in application code
users = []
for user in user_repo.get_all():
    if user.email.endswith("@example.com"):
        users.append(user)
```

### 3. **Use String Representations for Debugging**

```python
# ✓ Good: Clear understanding of object
user = user_repo.get_by_id(1)
print(user)           # User #1 - alice <alice@example.com> (ACTIVE)
print(repr(user))     # User(id=1, username='alice', ...)

# ✗ Bad: Unclear output
print(user.__dict__)  # Internal representation
```

### 4. **Handle Soft Delete Appropriately**

```python
# ✓ Good: Include deleted records when needed
deleted_users = user_repo.get_by_field("username", "alice", include_deleted=True)

# ✗ Bad: Forgetting to check for deleted records
user = user_repo.get_by_id(1)  # Might be logically deleted
# ... use user ...
```

### 5. **Cleanup Resources Properly**

```python
# ✓ Good: Always disconnect
db = DatabaseSingleton.get_instance()
db.configure("app.db")
db.connect()
try:
    # ... do work ...
    pass
finally:
    db.disconnect()

# Or using context manager pattern
@contextmanager
def get_db():
    db = DatabaseSingleton.get_instance()
    db.configure("app.db")
    db.connect()
    try:
        yield db
    finally:
        db.disconnect()

with get_db() as db:
    # ... do work ...
    pass
```

### 6. **Validate Data Before Creating**

```python
# ✓ Good: Validate input
def create_user(username, email, full_name):
    if not username or len(username) < 3:
        raise ValueError("Username must be at least 3 characters")
    if "@" not in email:
        raise ValueError("Invalid email format")
    
    user = User(username=username, email=email, full_name=full_name)
    return user_repo.create(user)

# ✗ Bad: No validation
user = User(username="x", email="invalid", full_name="")
user_repo.create(user)
```

### 7. **Use Appropriate Include/Exclude Flags**

```python
# ✓ Good: Explicit about including deleted
active_users = user_repo.get_all(include_deleted=False)  # Default
all_users = user_repo.get_all(include_deleted=True)

# ✗ Bad: Unclear intent
all_records = user_repo.get_all()  # Unclear if includes deleted
```

---

## Troubleshooting

### Issue: "database attribute does not appear to be set on the model"

**Cause**: Model doesn't have database assigned when `create_tables()` is called.

**Solution**: 
- Ensure `db.configure()` is called before `db.create_tables()`
- The SingleDatabase automatically assigns database to models during `create_tables()`

### Issue: "Circular import" errors

**Cause**: Models importing from DatabaseSingleton at module load time.

**Solution**:
- Don't assign database in model `Meta` class at import time
- Let DatabaseSingleton handle assignment during `create_tables()`

### Issue: "Soft deleted records appearing in queries"

**Cause**: Forgetting `include_deleted=False` parameter.

**Solution**:
```python
# Explicitly exclude soft-deleted
users = user_repo.get_all(include_deleted=False)
```

### Issue: "Transaction not atomic"

**Cause**: Not using `db.transaction()` context manager.

**Solution**:
```python
# Use context manager for atomicity
with db.transaction():
    # All operations here are atomic
    user.save()
```

---

## Migration from Plain Peewee

If you're using plain Peewee in an existing project:

```python
# Before (Plain Peewee)
from peewee import SqliteDatabase, Model

db = SqliteDatabase("app.db")

class BaseModel(Model):
    class Meta:
        database = db

# After (dbpykitpw)
from dbpykitpw import DatabaseSingleton, BaseModel

db = DatabaseSingleton.get_instance()
db.configure("app.db")
db.connect()
# BaseModel already has lifecycle management
```

---

## Contributing & Examples

The package includes a comprehensive demo showing all features:

```bash
# Run the demo
python3 demo/demo.py

# Or publish demo to another project
pykitdbdemo -o /path/to/my/project
```

Check [demo/demo.py](demo/demo.py) for complete working examples.

---

## License

MIT License - See LICENSE file for details.

---

## Questions & Support

For issues or questions:
1. Check this wiki first
2. Review demo.py for usage examples
3. Check the source code for implementations
4. Open an issue with detailed context
