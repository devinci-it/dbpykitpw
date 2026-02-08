"""
Demo Script - Comprehensive demonstration of dbpykitpw features.

This script demonstrates:
1. Database initialization and configuration
2. Repository registration
3. CRUD operations (Create, Read, Update, Delete)
4. Soft delete and restore functionality
5. Data transformation
6. Transaction management
7. String representations (__repr__ and __str__)
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
# From src/dbpykitpw/static/demo/ go up 3 levels to src, then we can import from dbpykitpw
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(project_root))  # Add src to path

from dbpykitpw.db.database_singleton import DatabaseSingleton
from dbpykitpw.utils.data_transformer import DataTransformer
from dbpykitpw.static.demo.user_model import User
from dbpykitpw.static.demo.user_repo import UserRepository


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n  → {title}")
    print("-" * 80)


def demo_initialization():
    """Demo 1: Database initialization and configuration."""
    print_section("DEMO 1: Database Initialization & Configuration")

    print("\n  Configuring DatabaseSingleton...")
    db = DatabaseSingleton.get_instance()
    db.configure("demo.db", soft_delete_enabled=True)
    print(f"  ✓ Configuration: {db}")
    print(f"  ✓ Detailed: {repr(db)}")

    print("\n  Connecting to database...")
    db.connect()
    print("  ✓ Connected to demo.db")

    print("\n  Creating tables...")
    db.create_tables()
    print("  ✓ Tables created successfully")

    return db


def demo_user_crud_operations(db: DatabaseSingleton):
    """Demo 2: CRUD operations with User repository."""
    print_section("DEMO 2: CRUD Operations with UserRepository")

    # Get repository instance
    user_repo = UserRepository(db._db)

    print_subsection("CREATE: Adding new users")
    users_data = [
        {"username": "alice", "email": "alice@example.com", "full_name": "Alice Johnson"},
        {"username": "bob", "email": "bob@example.com", "full_name": "Bob Smith"},
        {"username": "charlie", "email": "charlie@example.com", "full_name": "Charlie Brown"},
    ]

    created_users = []
    for user_data in users_data:
        user = User(**user_data)
        user_repo.create(user)
        created_users.append(user)
        print(f"  ✓ Created: {user}")
        print(f"    └─ Detailed: {repr(user)}")

    print_subsection("READ: Retrieving users")
    print("  Get user by ID:")
    user = user_repo.get_by_id(1)
    if user:
        print(f"    ✓ Found: {user}")
        print(f"      └─ Repr: {repr(user)}")

    print("\n  Get user by username:")
    user = user_repo.get_by_username("alice")
    if user:
        print(f"    ✓ Found: {user}")

    print("\n  Get user by email:")
    user = user_repo.get_by_email("bob@example.com")
    if user:
        print(f"    ✓ Found: {user}")

    print("\n  Get all active users:")
    all_users = user_repo.get_all()
    print(f"    ✓ Total active users: {len(all_users)}")
    for user in all_users:
        print(f"      - {user}")

    print_subsection("UPDATE: Modifying users")
    print("  Update user full_name:")
    rows_affected = user_repo.update(1, ("full_name", "Alice Smith"))
    print(f"    ✓ Rows affected: {rows_affected}")
    updated_user = user_repo.get_by_id(1)
    print(f"    ✓ Updated user: {updated_user}")

    print("\n  Deactivate user:")
    rows_affected = user_repo.deactivate_user(2)
    print(f"    ✓ Rows affected: {rows_affected}")
    user = user_repo.get_by_id(2)
    print(f"    ✓ User is_active: {user.is_active}")

    print("\n  Activate user:")
    rows_affected = user_repo.activate_user(2)
    print(f"    ✓ Rows affected: {rows_affected}")
    user = user_repo.get_by_id(2)
    print(f"    ✓ User is_active: {user.is_active}")

    print_subsection("DELETE: Soft delete operations")
    print("  Soft delete a user:")
    rows_affected = user_repo.delete(3)
    print(f"    ✓ Rows affected: {rows_affected}")
    deleted_user = user_repo.get_by_id(3, include_deleted=True)
    print(f"    ✓ Deleted user: {deleted_user}")
    print(f"      └─ Is deleted: {deleted_user.is_deleted()}")

    print("\n  Get only deleted users:")
    deleted_users = user_repo.get_deleted_users()
    print(f"    ✓ Total deleted users: {len(deleted_users)}")
    for user in deleted_users:
        print(f"      - {user}")

    print("\n  Restore deleted user:")
    rows_affected = user_repo.restore(3)
    print(f"    ✓ Rows affected: {rows_affected}")
    restored_user = user_repo.get_by_id(3)
    print(f"    ✓ Restored user: {restored_user}")
    print(f"      └─ Is deleted: {restored_user.is_deleted()}")

    print("\n  Get active users count:")
    count = user_repo.count()
    print(f"    ✓ Total active users: {count}")

    return user_repo, created_users


def demo_data_transformation(user_repo: UserRepository, users: list):
    """Demo 3: Data transformation utilities."""
    print_section("DEMO 3: Data Transformation")

    if not users:
        print("  ✗ No users available for transformation demo")
        return

    user = users[0]

    print_subsection("Model to Dictionary")
    user_dict = DataTransformer.model_to_dict(user)
    print(f"  ✓ Model: {user}")
    print(f"  ✓ Dictionary: {user_dict}")

    print_subsection("Model to JSON")
    user_json = DataTransformer.model_to_json(user)
    print(f"  ✓ JSON: {user_json}")

    print_subsection("Dictionary to JSON")
    dict_to_json = DataTransformer.dict_to_json(user_dict)
    print(f"  ✓ JSON: {dict_to_json}")

    print_subsection("JSON to Dictionary")
    json_to_dict = DataTransformer.json_to_dict(user_json)
    print(f"  ✓ Dictionary: {json_to_dict}")

    print_subsection("Using DataTransformer with Repository")
    user_from_db = user_repo.get_by_id(user.id)
    domain_dict = user_repo.domain_to_dict(user_from_db)
    print(f"  ✓ Domain to dict: {domain_dict}")

    domain_json = user_repo.domain_to_json(user_from_db)
    print(f"  ✓ Domain to JSON: {domain_json}")


def demo_transaction_management(db: DatabaseSingleton):
    """Demo 4: Transaction management."""
    print_section("DEMO 4: Transaction Management")

    user_repo = UserRepository(db._db)

    print_subsection("Atomic Transaction Example")

    print("  Creating multiple users in a single transaction...")
    users_to_create = [
        User(username="dave", email="dave@example.com", full_name="Dave Wilson"),
        User(username="eve", email="eve@example.com", full_name="Eve Davis"),
    ]

    try:
        with db.transaction() as transaction_db:
            for user in users_to_create:
                user.save()
            print(f"  ✓ Transaction committed with {len(users_to_create)} users")
    except Exception as e:
        print(f"  ✗ Transaction failed: {e}")

    print(f"\n  Total users in database: {user_repo.count()}")


def demo_repository_repr_and_str(user_repo: UserRepository, db: DatabaseSingleton):
    """Demo 6: String representations."""
    print_section("DEMO 6: Repository & Database String Representations")

    print_subsection("Repository String Representations")
    print(f"  __str__(): {str(user_repo)}")
    print(f"  __repr__(): {repr(user_repo)}")

    print_subsection("Database String Representations")
    print(f"  __str__(): {str(db)}")
    print(f"  __repr__(): {repr(db)}")

    print_subsection("User Model String Representations")
    user = user_repo.get_by_id(1)
    if user:
        print(f"  __str__(): {str(user)}")
        print(f"  __repr__(): {repr(user)}")


def demo_cleanup():
    """Demo 7: Cleanup and disconnection."""
    print_section("DEMO 7: Cleanup")

    db = DatabaseSingleton.get_instance()

    print("  Disconnecting from database...")
    db.disconnect()
    print("  ✓ Disconnected successfully")

    print("\n  Cleaning up demo database file...")
    if os.path.exists("demo.db"):
        os.remove("demo.db")
        print("  ✓ demo.db cleaned up")


def main():
    """Run all demonstration scenarios."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  DBPYKITPW - Comprehensive Feature Demonstration".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        # Run all demos in sequence
        db = demo_initialization()
        user_repo, users = demo_user_crud_operations(db)
        demo_data_transformation(user_repo, users)
        demo_transaction_management(db)
        demo_repository_repr_and_str(user_repo, db)
        demo_cleanup()

        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + "  ✓ All demonstrations completed successfully!".center(78) + "║")
        print("╚" + "=" * 78 + "╝")
        print("\n")

    except Exception as e:
        print(f"\n  ✗ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
