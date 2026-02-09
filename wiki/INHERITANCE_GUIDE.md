# Inheritance Guide - BaseModel & BaseRepository Features

Comprehensive guide to features, attributes, and methods automatically inherited from `BaseModel` and `BaseRepository`.

## Table of Contents

1. [BaseModel Inheritance](#basemodel-inheritance)
2. [BaseRepository Inheritance](#baserepository-inheritance)
3. [Usage Examples](#usage-examples)
4. [Best Practices](#best-practices)

---

## BaseModel Inheritance

All models inheriting from `BaseModel` automatically gain the following features:

### Automatic Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `AutoField` | Primary key, auto-incremented |
| `created_at` | `DateTimeField` | Timestamp of record creation, auto-set |
| `updated_at` | `DateTimeField` | Timestamp of last update, auto-updated on save |

These fields are **always present** in every model:

```python
from dbpykitpw import BaseModel
from peewee import CharField

class User(BaseModel):
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=255, unique=True)
    
    class Meta:
        table_name = "user"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# User automatically has:
# - id (primary key)
# - created_at (auto set)
# - updated_at (auto updated)
# - username
# - email
```

### Dynamic Setter Methods (Fluent Builder Pattern)

Every field in your model automatically gets a `set_<field_name>()` method for method chaining:

```python
user = User()
user.set_username("alice").set_email("alice@test.com")
# Returns: User instance with username="alice" and email="alice@test.com"
```

**How it works:**
- `__getattr__` intercepts calls to `set_*` methods
- Dynamically creates setter functions for any field
- Returns `self` for method chaining
- Works with any field name

**Advantages:**
- Fluent, readable syntax
- No need to manually define setters
- Works immediately for new fields
- Clean, chainable API

### Meta Class Attributes

Every model has a `Meta` class with these attributes:

```python
class User(BaseModel):
    username = CharField()
    
    class Meta:
        table_name = "user"  # Required: database table name
        abstract = False      # Can be overridden for abstract models
```

**Access model metadata:**

```python
user = User()
print(user._meta.table_name)      # "user"
print(user._meta.fields.keys())   # dict_keys(['id', 'created_at', 'updated_at', 'username', ...])
print(user._meta.primary_key)     # <Field: id>
```

### Automatic Timestamp Management

`updated_at` is automatically updated whenever `.save()` is called:

```python
user = User(username="alice", email="alice@test.com")
user.created_at  # Auto-set to current time on creation
user.updated_at  # Same as created_at initially

# ... later ...
user.username = "alice_smith"
user.save()      # updated_at automatically updated to current time
```

### String Representations

BaseModel provides `__repr__()` and `__str__()` methods:

```python
user = User(id=1)
str(user)        # "User #1"
repr(user)       # "User(id=1)"

# Without id (unsaved):
unsaved = User()
str(unsaved)     # "User"
repr(unsaved)    # "User()"
```

### Database Soft Delete Support

Models can support soft deletes via a `deleted_at` field:

```python
from datetime import datetime
from peewee import DateTimeField

class User(BaseModel):
    username = CharField()
    deleted_at = DateTimeField(null=True)  # Soft delete field
    
    class Meta:
        table_name = "user"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def is_deleted(self):
        """Check if record is soft deleted."""
        return self.deleted_at is not None
```

When using with repositories that have `soft_delete_enabled=True`, soft-deleted records are automatically filtered from queries.

---

## BaseRepository Inheritance

All repositories inheriting from `BaseRepository` automatically gain complete CRUD functionality:

### Class Attributes

Define these in your repository:

```python
from dbpykitpw import BaseRepository, register_repository

@register_repository("user_repo")
class UserRepository(BaseRepository):
    model = User                    # Required: the model class
    soft_delete_enabled = True      # Optional: enable soft delete (default: False)
    soft_delete_field = "deleted_at"  # Optional: field name for soft delete
```

### Automatic CRUD Methods

#### Create Operations

```python
# Single record
user = User(username="alice", email="alice@test.com")
created = repo.create(user)  # Returns created instance with id

# Multiple records (atomic)
users = [
    User(username="bob", email="bob@test.com"),
    User(username="charlie", email="charlie@test.com"),
]
created_users = repo.create_many(users)
```

#### Read Operations

```python
# By primary key
user = repo.get_by_id(1)              # Returns User or None
user = repo.get_by_id(1, include_deleted=True)  # Include soft-deleted

# All records
all_users = repo.get_all()            # Active records only
all_users = repo.get_all(include_deleted=True)  # Including deleted

# By any field
users = repo.get_by_field("email", "alice@test.com")
active_users = repo.get_by_field("is_active", True)
inactive_users = repo.get_by_field("is_active", False)
```

#### Update Operations

Three patterns supported:

```python
# Pattern 1: Tuple (single field)
repo.update(1, ("username", "alice_smith"))

# Pattern 2: Dictionary (multiple fields)
repo.update(1, {
    "username": "alice_smith",
    "email": "alice.smith@test.com",
    "is_active": False
})

# Pattern 3: Model instance
user.username = "alice_smith"
user.email = "alice.smith@test.com"
repo.update(1, user)
```

#### Delete Operations

```python
# Soft delete (if enabled)
repo.delete(1)                        # Hidden from queries
repo.get_by_id(1)                     # Returns None (soft-deleted)
repo.get_by_id(1, include_deleted=True)  # Returns the record

# Restore soft-deleted
repo.restore(1)                       # Clears deleted_at, visible again

# Hard delete (permanent)
repo.delete_hard(1)                   # Permanent removal, bypasses soft delete

# Batch operations
repo.delete_all()                     # Soft delete all
repo.delete_all(soft=False)           # Hard delete all
```

### Query Utility Methods

```python
# Counting
count = repo.count()                  # Active records only
total = repo.count(include_deleted=True)  # Including deleted
deleted_count = total - count

# Existence checking
if repo.exists(1):
    user = repo.get_by_id(1)
else:
    user = repo.create(User(...))
```

### Data Transformation Methods

```python
# To Dictionary
user_dict = repo.domain_to_dict(user)
# Returns: {"id": 1, "username": "alice", "created_at": ..., ...}

# To JSON (datetime objects automatically ISO formatted)
user_json = repo.domain_to_json(user)
# Returns: '{"id": 1, "username": "alice", "created_at": "2026-02-08T10:30:00", ...}'

# Parse JSON back
import json
data = json.loads(user_json)
```

### Database Information Methods

```python
# Get column names
columns = repo.get_columns("user", db._db)
# Returns: ['id', 'username', 'email', 'created_at', 'updated_at', ...]

# Get detailed column info
info = repo.get_column_info("user", db._db)
# Returns list with: {'cid': 0, 'name': 'id', 'type': 'INTEGER', 'notnull': True, 'pk': True}

# Get primary key
pk = repo.get_primary_key("user", db._db)
# Returns: "id"
```

### Transaction Support

All operations are wrapped in transactions:

```python
# Automatic transaction handling
try:
    user1 = repo.create(User(username="alice", email="alice@test.com"))
    user2 = repo.create(User(username="bob", email="bob@test.com"))
except Exception:
    # Both creates rolled back automatically
    pass
```

### String Representations

```python
user_repo = UserRepository(db._db)
str(user_repo)        # "Repository for User"
repr(user_repo)       # "UserRepository(model=User)"
```

---

## Usage Examples

### Example 1: Custom Repository with Domain Methods

```python
from dbpykitpw import BaseRepository, register_repository

@register_repository("user_repo")
class UserRepository(BaseRepository):
    model = User
    soft_delete_enabled = True
    
    # Custom domain methods (use inherited CRUD)
    def find_by_email(self, email: str):
        """Find user by email."""
        return self.get_by_field("email", email)
    
    def find_active_users(self):
        """Get all active users."""
        return self.get_by_field("is_active", True)
    
    def deactivate(self, user_id: int):
        """Soft deactivate user instead of deleting."""
        return self.update(user_id, ("is_active", False))
    
    def permanently_delete(self, user_id: int):
        """Permanently remove user from system."""
        return self.delete_hard(user_id)
```

**Usage:**

```python
repo = UserRepository(db._db)

# Inherited methods
all_users = repo.get_all()
user = repo.get_by_id(1)
repo.delete(1)

# Custom methods
alice = repo.find_by_email("alice@test.com")
active = repo.find_active_users()
repo.deactivate(1)
repo.permanently_delete(1)
```

### Example 2: Complex Model with Soft Delete

```python
from dbpykitpw import BaseModel
from peewee import CharField, BooleanField, DateTimeField, ForeignKeyField

class Product(BaseModel):
    """Product model with soft delete and relationships."""
    
    name = CharField(max_length=255)
    description = CharField(max_length=500, null=True)
    price = DecimalField(decimal_places=2)
    is_active = BooleanField(default=True)
    user = ForeignKeyField(User, backref="products")
    deleted_at = DateTimeField(null=True)
    
    class Meta:
        table_name = "product"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# Inherited features:
# - Automatic id, created_at, updated_at
# - Dynamic setters: .set_name(), .set_price(), etc.
# - Soft delete via deleted_at field
# - String representations
```

**With Repository:**

```python
@register_repository("product_repo")
class ProductRepository(BaseRepository):
    model = Product
    soft_delete_enabled = True
    
    def find_by_user(self, user_id: int):
        """Products created by a user."""
        products = self.get_by_field("user", user_id)
        return products
    
    def find_active_by_price(self, max_price: float):
        """Active products under price."""
        return [p for p in self.get_by_field("is_active", True)
                if p.price <= max_price]

# Usage with inheritance
repo = ProductRepository(db._db)

# Create with dynamic setters
product = Product()
product.set_name("Laptop").set_price(999.99).set_user(1)
repo.create(product)

# Query
products = repo.find_by_user(1)
cheap = repo.find_active_by_price(500.00)

# Soft delete
repo.delete(product.id)
repo.restore(product.id)
```

### Example 3: Data Pipeline with Inheritance

```python
def import_users_from_csv(csv_file, repo):
    """Import users with inherited CRUD and transformation."""
    users = []
    with open(csv_file) as f:
        for row in csv.DictReader(f):
            user = User(**row)
            users.append(user)
    
    # Batch create with inherited method
    created = repo.create_many(users)
    
    # Transform and return
    return [repo.domain_to_json(u) for u in created]

def export_users_to_json(repo):
    """Export all users as JSON with inherited features."""
    users = repo.get_all()
    
    # Transform to JSON (datetime handled automatically)
    json_list = [repo.domain_to_json(u) for u in users]
    
    return json.dumps(json_list)
```

---

## Best Practices

### 1. **Always Define `__init__` for Models**

Ensures dynamic setter methods work correctly:

```python
class User(BaseModel):
    username = CharField()
    
    class Meta:
        table_name = "user"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
```

### 2. **Use Soft Delete for Auditing**

Preserve deletion history:

```python
class User(BaseModel):
    username = CharField()
    deleted_at = DateTimeField(null=True)
    
    class Meta:
        table_name = "user"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@register_repository("user_repo")
class UserRepository(BaseRepository):
    model = User
    soft_delete_enabled = True
```

### 3. **Extend Repositories with Domain Methods**

Don't override inherited methods, extend them:

```python
@register_repository("user_repo")
class UserRepository(BaseRepository):
    model = User
    soft_delete_enabled = True
    
    # Custom domain logic
    def find_by_email(self, email):
        return self.get_by_field("email", email)
    
    # Don't override inherited methods like create, get_by_id, etc.
    # They handle transactions and soft delete automatically
```

### 4. **Leverage Automatic Timestamps**

Never manually set `created_at` or `updated_at`:

```python
# DON'T do this:
user = User(username="alice", created_at=datetime.now())

# DO this:
user = User(username="alice")
repo.create(user)  # updated_at auto-set
```

### 5. **Use Dynamic Setters for Initialization**

Clean, chainable syntax:

```python
# DON'T:
user = User()
user.username = "alice"
user.email = "alice@test.com"
user.is_active = True

# DO:
user = User().set_username("alice").set_email("alice@test.com").set_is_active(True)
```

### 6. **Use JSON Serialization with DateTimeEncoder**

Datetime objects are automatically handled:

```python
# Inherited and automatic
user_json = repo.domain_to_json(user)
# Datetime fields are ISO format strings

# Or manual
from dbpykitpw import DateTimeEncoder
import json
json_str = json.dumps(data, cls=DateTimeEncoder)
```

### 7. **Batch Operations for Performance**

Use atomic batch operations:

```python
# Slow - multiple transactions
for user_data in users_list:
    repo.create(User(**user_data))

# Fast - single transaction
users = [User(**data) for data in users_list]
repo.create_many(users)
```

### 8. **Verify Soft Delete Configuration**

Clear configuration in repositories:

```python
@register_repository("user_repo")
class UserRepository(BaseRepository):
    model = User
    soft_delete_enabled = True        # Explicit soft delete
    soft_delete_field = "deleted_at"  # Explicit field name
```

---

## Inheritance Hierarchy

```
Model (Peewee)
    └── BaseModel
            ├── User
            ├── Product
            ├── Order
            └── ... (your models)

BaseRepository
    ├── UserRepository
    ├── ProductRepository
    ├── OrderRepository
    └── ... (your repositories)
```

All features are inherited down the chain automatically.

---

## Quick Reference Table

| Feature | BaseModel | BaseRepository | Notes |
|---------|-----------|-----------------|-------|
| Auto ID | ✓ | - | AutoField primary key |
| Timestamps (created_at, updated_at) | ✓ | - | Auto-managed |
| Dynamic Setters | ✓ | - | set_field_name() methods |
| Create | - | ✓ | Single & batch |
| Read | - | ✓ | By ID, all, by field |
| Update | - | ✓ | Tuple, dict, or model |
| Delete | - | ✓ | Soft & hard delete |
| Soft Delete | ✓* | ✓ | Via deleted_at field & enabled flag |
| Transactions | - | ✓ | Auto-wrapped |
| Query Utilities | - | ✓ | count, exists, columns |
| Data Transform | - | ✓ | dict, JSON |
| String Repr | ✓ | ✓ | __str__ and __repr__ |

*Soft delete requires `deleted_at` field and repository with `soft_delete_enabled=True`

---

**Last Updated**: February 8, 2026  
**Version**: 1.0.0
