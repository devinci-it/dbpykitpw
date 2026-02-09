# dbpykitpw - Database Python Kit with Peewee and Workflows

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Peewee 3.14+](https://img.shields.io/badge/peewee-3.14+-orange.svg)](https://github.com/coleifer/peewee)

A lightweight ORM toolkit built on top of [Peewee](https://docs.peewee-orm.com/) that provides:
- **Singleton Database Management** - Centralized database connection and lifecycle management
- **Repository Pattern** - Generic CRUD operations with transaction support  
- **Soft Delete Support** - Built-in logical deletion with restore functionality
- **Data Transformation** - Seamless conversion between models, dictionaries, and JSON
- **CLI Tools** - Centralized command-line interface for scaffolding and demos
- **Transaction Management** - Context managers for atomic database operations

---

## Quick Start

### 1. Clone from GitHub

```bash
git clone https://github.com/devinci-it/dbpykitpw.git
cd dbpykitpw
```

### 2. Install

```bash
# Install in development mode (recommended for local development)
pip install -e .

# Or traditional install
pip install .
```

### 3. Create Your First Model

```python
# models/user.py
from dbpykitpw import BaseModel
from peewee import CharField, BooleanField, DateTimeField

class User(BaseModel):
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=255, unique=True)
    is_active = BooleanField(default=True)
    deleted_at = DateTimeField(null=True)  # Soft delete field
    
    class Meta:
        table_name = "user"
```

### 4. Create Your Repository

```python
# repositories/user_repo.py
from dbpykitpw import BaseRepository, register_repository
from models.user import User

@register_repository("user_repo")
class UserRepository(BaseRepository):
    model = User
    soft_delete_enabled = True
    
    def get_by_email(self, email: str):
        return self.get_by_field("email", email)
```

### 5. Use in Your Application

```python
from dbpykitpw import DatabaseSingleton
from models.user import User
from repositories.user_repo import UserRepository

# Setup database
db = DatabaseSingleton.get_instance()
db.configure("app.db", soft_delete_enabled=True)
db.connect()
db.create_tables()

# Get repository
user_repo = UserRepository(db._db)

# Create
user = User(username="alice", email="alice@example.com", is_active=True)
user_repo.create(user)

# Read
found = user_repo.get_by_email("alice@example.com")
print(found)

# Update
user_repo.update(user.id, ("is_active", False))

# Soft Delete & Restore
user_repo.delete(user.id)          # Mark as deleted
user_repo.restore(user.id)         # Restore
```

---

## CLI Reference

### Centralized Console Script

All CLI tools are accessed through the main `dbpykitpw` command:

```bash
dbpykitpw --help
```

### Demo Publish

Publish complete working example files to learn from.

```bash
# Long form
dbpykitpw demo-publish
dbpykitpw demo-publish -o ./my_project

# Short form
dbpykitpw dp
dbpykitpw dp -o ./my_project -f -v
```

**Options:**
- `-o, --output DIR` - Output directory (default: current directory)
- `-f, --force` - Overwrite existing files
- `-v, --verbose` - Show detailed output

**Example:**
```bash
dbpykitpw dp -v          # Publish demo to current dir with verbose output
dbpykitpw dp -o ./app -f # Force publish to ./app directory
```

### Template Generate

Generate boilerplate model and repository files.

```bash
# Long form
dbpykitpw template-generate User
dbpykitpw template-generate Product --models ./app/models --repos ./app/repos

# Short form
dbpykitpw tg User
dbpykitpw tg Product -m ./app/models -r ./app/repos
```

**Options:**
- `-m, --models DIR` - Models directory (default: ./models)
- `-r, --repos DIR` - Repositories directory (default: ./repositories)
- `-fk, --foreign-key MODEL` - Foreign key reference (repeatable)
- `-f, --force` - Overwrite existing files
- `-v, --verbose` - Show verbose output

**Examples:**
```bash
dbpykitpw tg User                              # Simple model
dbpykitpw tg Product -fk User                  # With foreign key
dbpykitpw tg Order -fk User -fk Product -f -v  # Multiple FKs with options
```

---

## Features

### ✨ Core Features

- ✅ **Zero-Configuration Setup** - Get started with minimal configuration
- ✅ **Automatic Table Creation** - Tables created for all registered models
- ✅ **Soft Delete Built-in** - Logical deletion with restore capability
- ✅ **Transaction Support** - Atomic operations with context managers
- ✅ **Type-Safe Operations** - Work with Peewee models directly
- ✅ **Data Transformation** - Convert between models, dicts, and JSON
- ✅ **Decorator Registration** - Auto-register models and repos with decorators
- ✅ **Repository Pattern** - Generic CRUD operations with custom extensions
- ✅ **CLI Scaffolding** - Generate boilerplate code quickly

### 🔧 Components

| Component | Purpose |
|-----------|---------|
| `DatabaseSingleton` | Database connection and lifecycle management |
| `BaseModel` | Base class for all models with common fields |
| `BaseRepository` | Generic CRUD operations with transactions |
| `DataTransformer` | Model ↔ Dict ↔ JSON conversions |
| `TransactionManager` | Atomic transaction context managers |
| `@register_repository` | Decorator for automatic registration |

---

## Documentation

- **[Complete Wiki](WIKI.md)** - Comprehensive reference guide
- **[Common Flows](COMMON_FLOWS.md)** - Real-world workflow examples  
- **[CLI Guide](CENTRALIZED_CLI.md)** - Detailed command reference
- **[Template Generator](TEMPLATE_GENERATOR.md)** - Scaffolding usage

---

## Examples

### Example 1: Basic CRUD

```python
from dbpykitpw import DatabaseSingleton
from models.user import User
from repositories.user_repo import UserRepository

# Setup
db = DatabaseSingleton.get_instance()
db.configure("app.db")
db.connect()
db.create_tables()

user_repo = UserRepository(db._db)

# CREATE
user = User(username="bob", email="bob@test.com")
created = user_repo.create(user)

# READ
bob = user_repo.get_by_email("bob@test.com")[0]
print(f"Found: {bob}")

# UPDATE
user_repo.update(bob.id, ("username", "robert"))

# DELETE (soft)
user_repo.delete(bob.id)

# RESTORE
user_repo.restore(bob.id)
```

### Example 2: Soft Delete Workflow

```python
# Create user
user = User(username="alice", email="alice@test.com")
user_repo.create(user)

# Soft delete (marked as deleted but still in DB)
user_repo.delete(user.id)

# Query active users only (default behavior)
active = user_repo.get_all()  # Doesn't include deleted

# Query including deleted
all_including_deleted = user_repo.get_all(include_deleted=True)

# Restore deleted record
user_repo.restore(user.id)
```

### Example 3: Foreign Keys

```python
# User model
class User(BaseModel):
    name = CharField()
    class Meta:
        table_name = "user"

# Product model with FK to User
class Product(BaseModel):  
    name = CharField()
    user = ForeignKeyField(User, backref="products")
    class Meta:
        table_name = "product"

# Usage
user_repo.create(user)
product_repo.create(Product(name="Laptop", user=user))

# Access reverse relation
for product in user.products:
    print(product.name)
```

### Example 4: Custom Repository Methods

```python
@register_repository("user_repo")
class UserRepository(BaseRepository):
    model = User
    soft_delete_enabled = True
    
    def get_by_email(self, email: str):
        """Custom query method."""
        return self.get_by_field("email", email)
    
    def get_active_users(self):
        """Active users only."""
        query = User.select().where(
            (User.deleted_at.is_null()) & (User.is_active == True)
        )
        return list(query)
    
    def count_by_status(self, status):
        """Count users by status."""
        return User.select().where(User.status == status).count()
```

---

## Project Structure

```
dbpykitpw/
├── src/dbpykitpw/
│   ├── cli/
│   │   ├── console.py              # Main CLI entry point
│   │   ├── demo_publisher.py       # Demo publishing tool
│   │   ├── template_generator.py   # Template generation tool
│   │   └── util.py                 # CLI utilities
│   │
│   ├── db/
│   │   ├── database_singleton.py   # Database connection management
│   │   └── transaction_manager.py  # Transaction support
│   │
│   ├── models/
│   │   └── base_model.py           # Base model class
│   │
│   ├── repositories/
│   │   └── base_repository.py      # Base repository class
│   │
│   ├── utils/
│   │   ├── data_transformer.py     # Data transformations
│   │   └── decorators.py           # Registration decorators
│   │
│   └── __init__.py
│
├── setup.py                        # Package installation
├── WIKI.md                         # Complete reference
├── COMMON_FLOWS.md                 # Workflow examples
├── CENTRALIZED_CLI.md              # CLI guide
├── README.md                       # This file
└── LICENSE                         # MIT License
```

---

## Installation Options

Choose the installation method that best fits your workflow:

| Method | Best For | Command |
|--------|----------|---------|
| **Development** | Local development, contributors | `pip install -e .` |
| **Wheel** | Distribution, clean venv, testing | `pip install dist/dbpykitpw-*.whl` |
| **Standard** | Simple installation | `pip install .` |
| **PyPI** | When available on PyPI | `pip install dbpykitpw` |

### From GitHub (Recommended)

```bash
# Clone the repository
git clone https://github.com/devinci-it/dbpykitpw.git
cd dbpykitpw

# Install in development mode (editable)
pip install -e .

# Or standard install
pip install .
```

### From PyPI (When Available)

```bash
pip install dbpykitpw
```

### Build and Install from Wheel

Build a redistributable wheel package and install it in a virtual environment.

#### 1. Build the Wheel

```bash
# Clone the repository
git clone https://github.com/devinci-it/dbpykitpw.git
cd dbpykitpw

# Install build dependencies
pip install build wheel

# Build the wheel
python -m build

# Or use direct build command
python setup.py bdist_wheel

# Output: dist/dbpykitpw-1.0.0-py3-none-any.whl
ls dist/
```

#### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

#### 3. Install from Wheel

```bash
# Install the built wheel
pip install dist/dbpykitpw-1.0.0-py3-none-any.whl

# Or install with extras (if defined)
pip install dist/dbpykitpw-1.0.0-py3-none-any.whl[dev]
```

#### 4. Verify Installation

```bash
# Check if dbpykitpw is installed
pip list | grep dbpykitpw

# Test the CLI
dbpykitpw --help

# Test the import
python -c "from dbpykitpw import DatabaseSingleton; print('Success!')"
```

#### Complete Example Workflow

```bash
# Setup
git clone https://github.com/devinci-it/dbpykitpw.git
cd dbpykitpw
pip install build wheel

# Build
python -m build
echo "Built: dist/dbpykitpw-1.0.0-py3-none-any.whl"

# Create fresh venv
python -m venv test_env
source test_env/bin/activate  # or: test_env\Scripts\activate on Windows

# Install from wheel
pip install dist/dbpykitpw-1.0.0-py3-none-any.whl

# Verify
dbpykitpw --help
python -c "from dbpykitpw import DatabaseSingleton; print('✓ Installation successful!')"

# Deactivate when done
deactivate
```

### Verify Installation

```bash
dbpykitpw --help
```

---

## Requirements

- Python 3.8 or higher
- peewee >= 3.14.0

---

## Usage Workflow

### 1. Learn (Start with Demo)

```bash
# Get example files
dbpykitpw demo-publish -v

# Study the example
cd demo
python demo.py
```

### 2. Build (Generate Models)

```bash
# Create your models
dbpykitpw tg User -v
dbpykitpw tg Product -fk User -v
```

### 3. Develop (Use in Code)

```python
# Initialize and use
db = DatabaseSingleton.get_instance()
db.configure("app.db")
db.connect()
db.create_tables()

user_repo = UserRepository(db._db)
user = user_repo.create(User(username="test"))
```

### 4. Deploy (Use as Package)

```bash
pip install -e .
# Use in your project
```

---

## API Quick Reference

### DatabaseSingleton

```python
db = DatabaseSingleton.get_instance()
db.configure("app.db", soft_delete_enabled=True)
db.connect()
db.create_tables()
db.get_repository("user_repo")  # Get repo class
db.get_model("user")             # Get model class
with db.transaction:            # Transaction context (no parentheses needed)
    # Atomic operations
```

### BaseRepository

```python
repo = UserRepository(db._db)

# CRUD
repo.create(user)
repo.get_by_id(1)
repo.get_all()
repo.get_by_field("email", "test@test.com")
repo.update(1, ("name", "New Name"))
repo.delete(1)  # Soft delete
repo.restore(1)

# Utility
repo.count()
repo.exists(1)
repo.domain_to_dict(user)
repo.domain_to_json(user)
```

### DataTransformer

```python
from dbpykitpw.utils.data_transformer import DataTransformer

# Conversions
DataTransformer.model_to_dict(user)
DataTransformer.model_to_json(user)
DataTransformer.dict_to_model(data, User)
DataTransformer.json_to_model(json_str, User)
```

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## Support

- 📖 [Read the Wiki](WIKI.md)
- 💡 [View Examples](COMMON_FLOWS.md)
- 🔧 [CLI Reference](CENTRALIZED_CLI.md)
- 🐛 [Report Issues](https://github.com/devinci-it/dbpykitpw/issues)

---

## Author

**devinci-it** - [GitHub](https://github.com/devinci-it)

---

## Changelog

### v1.0.0
- Initial release
- Core singleton pattern implementation
- Repository pattern with CRUD operations
- Soft delete support
- Data transformation utilities
- Centralized CLI with subcommands
- Comprehensive documentation

---

**Happy coding! 🚀**

