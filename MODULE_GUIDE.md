# Module Documentation Guide

Comprehensive documentation for all dbpykitpw modules with type hints, parameters, return types, and usage examples.

## Table of Contents

1. [DatabaseSingleton](#databasesingleton)
2. [BaseRepository](#baserepository)
3. [BaseModel](#basemodel)
4. [DataTransformer](#datatransformer)
5. [TransactionManager](#transactionmanager)
6. [Decorators](#decorators)
7. [CLI Console](#cli-console)

---

## DatabaseSingleton

**Module**: `dbpykitpw.db.database_singleton`

Central database management using the singleton pattern.

### Initialization

```python
from dbpykitpw import DatabaseSingleton

db = DatabaseSingleton.get_instance()
```

### Key Methods

#### `get_instance() -> DatabaseSingleton`

Get the singleton instance (always same instance).

```python
db = DatabaseSingleton.get_instance()
db2 = DatabaseSingleton.get_instance()
assert db is db2  # True
```

#### `configure(db_file: str, soft_delete_enabled: bool = False) -> DatabaseSingleton`

Configure database with file path and soft delete settings.

**Args:**
- `db_file` (str): Path to SQLite database file
- `soft_delete_enabled` (bool): Enable soft delete globally

**Returns:** Self for method chaining

```python
db.configure("app.db", soft_delete_enabled=True)
```

#### `connect() -> DatabaseSingleton`

Establish database connection.

```python
db.configure("app.db").connect()
```

#### `create_tables() -> None`

Create all registered model tables.

```python
db.create_tables()
```

#### `register_model(model_class: Type[Model], repo_class: Type[BaseRepository], key: str) -> None`

Register a model and repository (usually automatic via decorator).

```python
db.register_model(User, UserRepository, "user_repo")
```

#### `get_repository(key: str) -> Optional[Type[BaseRepository]]`

Retrieve repository class by key.

```python
UserRepoClass = db.get_repository("user_repo")
user_repo = UserRepoClass(db._db)  # Instantiate
```

#### `get_model(key: str) -> Optional[Type[Model]]`

Retrieve model class by key.

```python
User = db.get_model("user")
```

#### `transaction() -> Iterator[SqliteDatabase]`

Context manager for atomic transactions.

```python
try:
    with db.transaction:
        user1 = User(username="alice", email="alice@test.com")
        user1.save()
        user2 = User(username="bob", email="bob@test.com")
        user2.save()
except Exception:
    # Both creates rolled back
    pass
```

#### `execute_sql(sql: str, params: Optional[tuple] = None) -> List[Any]`

Execute raw SQL query.

```python
results = db.execute_sql(
    "SELECT id, username FROM user WHERE active = ?",
    (True,)
)
```

#### `execute_sql_single(sql: str, params: Optional[tuple] = None) -> Optional[Any]`

Execute SQL and return first result.

```python
result = db.execute_sql_single(
    "SELECT username FROM user WHERE id = ?",
    (1,)
)
```

---

## BaseRepository

**Module**: `dbpykitpw.repositories.base_repository`

Generic CRUD operations with transaction support.

### Basic Setup

```python
from dbpykitpw import BaseRepository, register_repository
from models.user import User

@register_repository("user_repo")
class UserRepository(BaseRepository):
    model = User
    soft_delete_enabled = True
    
    def get_by_email(self, email: str) -> List[Model]:
        return self.get_by_field("email", email)

# Use
repo = UserRepository(db._db)
```

### Key Methods

#### `create(model_instance: Model) -> Model`

Create and save a single record.

```python
user = User(username="alice", email="alice@test.com")
created = repo.create(user)
print(created.id)  # Auto-populated
```

#### `create_many(model_instances: List[Model]) -> List[Model]`

Create multiple records atomically.

```python
users = [
    User(username="alice", email="alice@test.com"),
    User(username="bob", email="bob@test.com"),
]
created = repo.create_many(users)
```

#### `get_by_id(primary_key: Union[int, str], include_deleted: bool = False) -> Optional[Model]`

Retrieve record by ID.

```python
user = repo.get_by_id(1)
if user:
    print(user.username)

# Include soft-deleted
deleted_user = repo.get_by_id(1, include_deleted=True)
```

#### `get_all(include_deleted: bool = False) -> List[Model]`

Get all records.

```python
all_users = repo.get_all()
all_including_deleted = repo.get_all(include_deleted=True)
```

#### `get_by_field(field_name: str, value: Any, include_deleted: bool = False) -> List[Model]`

Query by any field.

```python
users_by_email = repo.get_by_field("email", "alice@test.com")
active_users = repo.get_by_field("is_active", True)
```

#### `update(primary_key: Union[int, str], value: Union[Tuple, Model, Dict]) -> int`

Update record field(s).

```python
# By tuple
repo.update(1, ("username", "alice_smith"))

# By dictionary
repo.update(1, {"username": "alice_smith", "is_active": False})

# By model instance
user.username = "alice_smith"
repo.update(1, user)
```

#### `delete(primary_key: Union[int, str]) -> int`

Soft delete (or hard delete if disabled).

```python
repo.delete(1)  # Soft delete if enabled
```

#### `delete_hard(primary_key: Union[int, str]) -> int`

Force hard delete regardless of soft delete setting.

```python
repo.delete_hard(1)  # Permanent deletion
```

#### `restore(primary_key: Union[int, str]) -> int`

Restore soft-deleted record.

```python
repo.restore(1)
```

#### `delete_all(soft: bool = True) -> int`

Delete all records.

```python
repo.delete_all()  # Soft delete all
repo.delete_all(soft=False)  # Hard delete all
```

#### `count(include_deleted: bool = False) -> int`

Count records.

```python
active_count = repo.count()
total_count = repo.count(include_deleted=True)
```

#### `exists(primary_key: Union[int, str]) -> bool`

Check if record exists.

```python
if repo.exists(1):
    print("User 1 exists")
```

#### `domain_to_dict(domain_object: Model) -> Dict[str, Any]`

Convert model to dictionary.

```python
user_dict = repo.domain_to_dict(user)
print(user_dict)  # {"id": 1, "username": "alice", ...}
```

#### `domain_to_json(domain_object: Model) -> str`

Convert model to JSON string.

```python
user_json = repo.domain_to_json(user)
print(user_json)  # '{"id": 1, "username": "alice", ...}'
```

#### `get_columns(table_name: str, database) -> List[str]`

Get column names (static method).

```python
cols = BaseRepository.get_columns("user", db._db)
# Returns: ['id', 'username', 'email', ...]
```

#### `get_column_info(table_name: str, database) -> List[Dict[str, Any]]`

Get detailed column information (static method).

```python
info = BaseRepository.get_column_info("user", db._db)
# Returns: [
#   {"cid": 0, "name": "id", "type": "INTEGER", "notnull": True, "pk": True},
#   {"cid": 1, "name": "username", "type": "TEXT", "notnull": True, "pk": False},
#   ...
# ]
```

#### `get_primary_key(table_name: str, database) -> Optional[str]`

Get primary key column name (static method).

```python
pk = BaseRepository.get_primary_key("user", db._db)
# Returns: "id"
```

---

## BaseModel

**Module**: `dbpykitpw.models.base_model`

Base model class for all entities.

### Features

- Auto-generated `created_at` timestamp
- Auto-updated `updated_at` timestamp
- Optional `deleted_at` for soft delete support
- Automatic string representations

### Usage

```python
from dbpykitpw import BaseModel
from peewee import CharField, BooleanField, DateTimeField

class User(BaseModel):
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=255, unique=True)
    is_active = BooleanField(default=True)
    deleted_at = DateTimeField(null=True)
    
    class Meta:
        table_name = "user"
```

---

## DataTransformer

**Module**: `dbpykitpw.utils.data_transformer`

Convert between models, dictionaries, and JSON.

### Methods

#### `model_to_dict(model: Model) -> Dict[str, Any]`

Convert Peewee model to dictionary.

```python
user_dict = DataTransformer.model_to_dict(user)
```

#### `model_to_json(model: Model) -> str`

Convert Peewee model to JSON.

```python
user_json = DataTransformer.model_to_json(user)
```

#### `dict_to_model(data: Dict[str, Any], model_class: Type[Model]) -> Model`

Convert dictionary to model instance.

```python
user_dict = {"username": "alice", "email": "alice@test.com"}
user = DataTransformer.dict_to_model(user_dict, User)
```

#### `json_to_model(json_str: str, model_class: Type[Model]) -> Model`

Convert JSON to model instance.

```python
json_str = '{"username": "alice", "email": "alice@test.com"}'
user = DataTransformer.json_to_model(json_str, User)
```

#### `dict_to_json(data: Dict[str, Any]) -> str`

Convert dictionary to JSON.

```python
data = {"username": "alice", "email": "alice@test.com"}
json_str = DataTransformer.dict_to_json(data)
```

#### `json_to_dict(json_str: str) -> Dict[str, Any]`

Convert JSON to dictionary.

```python
json_str = '{"username": "alice"}'
data = DataTransformer.json_to_dict(json_str)
```

---

## TransactionManager

**Module**: `dbpykitpw.db.transaction_manager`

Handle database transactions.

### Methods

#### `transaction() -> Iterator[SqliteDatabase]`

Context manager for atomic operations.

```python
with transaction_manager.transaction():
    # All operations atomic
    user1.save()
    user2.save()
    # Auto-commit on success
    # Auto-rollback on exception
```

#### `savepoint(name: str) -> Iterator[SqliteDatabase]`

Named savepoint within transaction.

```python
with transaction_manager.transaction():
    user1.save()
    with transaction_manager.savepoint("sp1"):
        user2.save()
        # Can rollback to sp1 without losing user1
```

---

## Decorators

**Module**: `dbpykitpw.utils.decorators`

Registration decorators for models and repositories.

### `@register_repository(key: str)`

Register repository and model automatically.

```python
from dbpykitpw import register_repository, BaseRepository

@register_repository("user_repo")
class UserRepository(BaseRepository):
    model = User
    soft_delete_enabled = True
```

This automatically:
1. Registers the User model
2. Registers the UserRepository class
3. Sets up the database connection

---

## CLI Console

**Module**: `dbpykitpw.cli.console`

Centralized command-line interface.

### Commands

#### Demo Publish

```bash
dbpykitpw demo-publish              # Long form
dbpykitpw dp                        # Short form
dbpykitpw dp -o ./my_app -f -v     # With options
```

**Options:**
- `-o, --output DIR`: Output directory
- `-f, --force`: Overwrite existing files
- `-v, --verbose`: Detailed output

#### Template Generate

```bash
dbpykitpw template-generate User    # Long form
dbpykitpw tg User                   # Short form
dbpykitpw tg Product -fk User -f -v # With FK and options
```

**Options:**
- `-m, --models DIR`: Models directory (default: ./models)
- `-r, --repos DIR`: Repos directory (default: ./repositories)
- `-fk, --foreign-key MODEL`: Foreign key reference (repeatable)
- `-f, --force`: Overwrite existing files
- `-v, --verbose`: Detailed output

---

## Complete Example

```python
from dbpykitpw import DatabaseSingleton, BaseModel, BaseRepository, register_repository
from peewee import CharField, BooleanField, DateTimeField, ForeignKeyField
from datetime import datetime

# 1. Define Models
class User(BaseModel):
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=255, unique=True)
    is_active = BooleanField(default=True)
    deleted_at = DateTimeField(null=True)
    
    class Meta:
        table_name = "user"

class Product(BaseModel):
    name = CharField(max_length=255)
    user = ForeignKeyField(User, backref="products")
    deleted_at = DateTimeField(null=True)
    
    class Meta:
        table_name = "product"

# 2. Define Repositories
@register_repository("user_repo")
class UserRepository(BaseRepository):
    model = User
    soft_delete_enabled = True
    
    def get_by_email(self, email: str):
        return self.get_by_field("email", email)

@register_repository("product_repo")
class ProductRepository(BaseRepository):
    model = Product
    soft_delete_enabled = True

# 3. Setup Database
db = DatabaseSingleton.get_instance()
db.configure("app.db", soft_delete_enabled=True)
db.connect()
db.create_tables()

# 4. Use Repositories
user_repo = UserRepository(db._db)
product_repo = ProductRepository(db._db)

# Create
user = User(username="alice", email="alice@test.com", is_active=True)
user_repo.create(user)

# Read
found = user_repo.get_by_email("alice@test.com")
all_active = user_repo.get_all()

# Update
user_repo.update(user.id, ("username", "alice_smith"))

# Create related
product = Product(name="Laptop", user=user)
product_repo.create(product)

# Soft Delete & Restore
user_repo.delete(user.id)
user_repo.restore(user.id)

# Cleanup
db.disconnect()
```

---

**Last Updated**: February 8, 2026  
**Version**: 1.0.0
