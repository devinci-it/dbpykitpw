# dbpykitpw Centralized CLI Guide

## Overview

**dbpykitpw** provides a centralized command-line interface with two main subcommands:
1. `demo-publish` (alias: `dp`) - Publish demo example files
2. `template-generate` (alias: `tg`) - Generate model and repository templates

## Installation

```bash
pip install -e .
```

This creates the main `dbpykitpw` command with subcommands.

---

## Command Reference

### Demo Publish

Publish complete working example files to your project.

#### Full Syntax
```bash
dbpykitpw demo-publish [OPTIONS]
```

#### Short Syntax
```bash
dbpykitpw dp [OPTIONS]
```

#### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output DIR` | `-o DIR` | Output directory | Current directory |
| `--force` | `-f` | Overwrite existing files | False |
| `--verbose` | `-v` | Show detailed output | False |
| `--help` | `-h` | Show help message | - |

#### Examples

```bash
# Publish demo to current directory
dbpykitpw demo-publish

# Or use short form
dbpykitpw dp

# Publish to specific directory
dbpykitpw demo-publish -o ./my_project

# Overwrite existing files
dbpykitpw dp -o ./my_project -f

# Show what's being copied
dbpykitpw demo-publish --verbose

# All options combined
dbpykitpw dp -o ./my_project -f -v
```

#### What Gets Published

```
demo/
├── __init__.py
├── user_model.py          # Example User model with all fields
├── user_repo.py           # Example UserRepository with custom queries  
└── demo.py                # Complete feature demonstration
```

---

### Template Generate

Generate boilerplate model and repository files for a new entity.

#### Full Syntax
```bash
dbpykitpw template-generate NAME [OPTIONS]
```

#### Short Syntax
```bash
dbpykitpw tg NAME [OPTIONS]
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `NAME` | Model name (e.g., User, Product, Order) |

#### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--models DIR` | `-m DIR` | Models directory | `./models` |
| `--repos DIR` | `-r DIR` | Repositories directory | `./repositories` |
| `--foreign-key MODEL` | `-fk MODEL` | Foreign key reference (repeatable) | - |
| `--force` | `-f` | Overwrite existing files | False |
| `--verbose` | `-v` | Show detailed output and next steps | False |
| `--help` | `-h` | Show help message | - |

#### Examples

```bash
# Generate User model/repo to default directories
dbpykitpw template-generate User

# Or use short form
dbpykitpw tg User

# Custom directories
dbpykitpw template-generate Product -m ./app/models -r ./app/repos

# With foreign key
dbpykitpw template-generate Product -fk User

# Multiple foreign keys
dbpykitpw tg Order -fk User -fk Product

# Combined options
dbpykitpw tg Comment -fk User -fk Post -m ./src/models -r ./src/repos -f -v
```

#### What Gets Generated

For `dbpykitpw tg User`:

**models/user.py**
```python
from dbpykitpw import BaseModel
from peewee import CharField, DateTimeField
from datetime import datetime

@register_model("user")
class User(BaseModel):
    # Auto-generated fields: created_at, updated_at
    deleted_at = DateTimeField(null=True)  # Soft delete
    
    class Meta:
        table_name = "user"
    
    def __repr__(self):
        return f"User(id={self.id}, created={self.created_at})"
    
    def __str__(self):
        return f"User #{self.id}"
```

**repositories/user_repo.py**
```python
from dbpykitpw import BaseRepository, register_repository
from models.user import User

@register_repository("user_repo")
class UserRepository(BaseRepository):
    model = User
    soft_delete_enabled = True
    
    # Add your custom methods here
    # Example:
    # def get_by_email(self, email):
    #     return self.get_by_field("email", email)
```

#### Foreign Key Example

For `dbpykitpw tg Product -fk User`:

Generated **models/product.py** includes:
```python
from peewee import ForeignKeyField
from models.user import User

class Product(BaseModel):
    # ... fields ...
    user = ForeignKeyField(User, backref="products")  # FK to User
```

---

## Usage Workflow

### 1. Start with Demo (Learn)

```bash
# See complete working example
dbpykitpw dp -v

# Go to demo/ directory
cd demo
python demo.py  # Run the example
```

### 2. Generate Models (Build)

```bash
# Create User entity
dbpykitpw tg User -v

# Create Product with FK to User
dbpykitpw tg Product -fk User -v

# View generated files
cat models/user.py
cat repositories/user_repo.py
```

### 3. Use in Your Code

```python
from dbpykitpw import DatabaseSingleton
from models.user import User
from models.product import Product
from repositories.user_repo import UserRepository
from repositories.product_repo import ProductRepository

# Setup
db = DatabaseSingleton.get_instance()
db.configure("app.db", soft_delete_enabled=True)
db.connect()
db.create_tables()

# Get repositories
user_repo = UserRepository(db._db)
product_repo = ProductRepository(db._db)

# Create
user = User(username="alice", email="alice@test.com")
user_repo.create(user)

# Use FK
product = Product(name="Laptop", user=user)
product_repo.create(product)
```

---

## Legacy Command Aliases

For backward compatibility, the old command-line tools still work:

```bash
# Old way (still works)
pykitdbdemo -o ./my_project    # Demo publish
dbpy-template User             # Template generate

# New way (preferred)
dbpykitpw dp -o ./my_project
dbpykitpw tg User
```

---

## Troubleshooting

### Command not found: dbpykitpw

Make sure you installed the package:
```bash
pip install -e .
```

### Existing files error

Use `-f` / `--force` to overwrite:
```bash
dbpykitpw dp -f
dbpykitpw tg User -f
```

### Need more information

Use `-v` / `--verbose` for detailed output:
```bash
dbpykitpw demo-publish -v
dbpykitpw template-generate User -v
```

---

## Help Command

Get help for any command:

```bash
# Main help
dbpykitpw --help
dbpykitpw -h

# Subcommand help
dbpykitpw demo-publish --help
dbpykitpw dp -h

dbpykitpw template-generate --help
dbpykitpw tg -h
```
