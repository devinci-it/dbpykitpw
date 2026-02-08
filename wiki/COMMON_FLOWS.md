# dbpykitpw - Common Workflows & Flows

This document provides step-by-step guides for the most common development scenarios.

## Table of Contents

1. [System Initialization Flow](#system-initialization-flow)
2. [CRUD Operations Flow](#crud-operations-flow)
3. [User Registration Flow](#user-registration-flow)
4. [Soft Delete & Recovery Flow](#soft-delete--recovery-flow)
5. [Data Import Flow](#data-import-flow)
6. [Data Export Flow](#data-export-flow)
7. [Batch Operations Flow](#batch-operations-flow)
8. [Error Handling Pattern](#error-handling-pattern)
9. [Multi-Repository Coordination Flow](#multi-repository-coordination-flow)
10. [Audit Logging Flow](#audit-logging-flow)

---

## System Initialization Flow

**Scenario**: Starting your application and preparing the database.

### Flow Diagram

```
Application Start
    ↓
Import models & repositories
    ↓
Get DatabaseSingleton instance
    ↓
Configure database file & settings
    ↓
Connect to database
    ↓
Create tables for models
    ↓
Ready for operations
    ↓
... application runs ...
    ↓
Disconnect database
    ↓
Application Exit
```

### Implementation

```python
# app.py
from dbpykitpw import DatabaseSingleton
from repositories.user_repo import UserRepository
from repositories.product_repo import ProductRepository
import logging

logger = logging.getLogger(__name__)

class Application:
    def __init__(self):
        self.db = None
        self.repositories = {}
    
    def initialize(self):
        """Initialize database and repositories at startup."""
        try:
            # Step 1: Get singleton instance
            self.db = DatabaseSingleton.get_instance()
            logger.info("DatabaseSingleton instance obtained")
            
            # Step 2: Configure database
            self.db.configure("app.db", soft_delete_enabled=True)
            logger.info("Database configured: app.db (soft_delete=True)")
            
            # Step 3: Connect to database
            self.db.connect()
            logger.info("Connected to database")
            
            # Step 4: Create tables
            self.db.create_tables()
            logger.info("Tables created for all registered models")
            
            # Step 5: Initialize repositories
            self.repositories["users"] = UserRepository(self.db._db)
            self.repositories["products"] = ProductRepository(self.db._db)
            logger.info("Repositories initialized")
            
            logger.info("✓ Application ready")
            return True
            
        except Exception as e:
            logger.error(f"✗ Initialization failed: {e}")
            return False
    
    def shutdown(self):
        """Clean up resources when exiting."""
        try:
            if self.db:
                self.db.disconnect()
                logger.info("Database disconnected")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def get_repository(self, name):
        """Get a repository by name."""
        return self.repositories.get(name)

# Usage
app = Application()
if app.initialize():
    try:
        # ... use app.repositories["users"], etc ...
        pass
    finally:
        app.shutdown()
```

---

## CRUD Operations Flow

**Scenario**: Performing Create, Read, Update, Delete operations on a single model.

### Flow Diagram

```
┌─────────────────────────────────────┐
│      CRUD Operations Flow           │
├─────────────────────────────────────┤
│                                     │
│  CREATE  │  READ  │  UPDATE  │ DELETE
│    ↓       ↓         ↓          ↓
│  Validate  Query    Fetch     Get ID
│    ↓       ↓         ↓          ↓
│  Model   Return    Modify     Mark
│    ↓                ↓       Deleted
│  Save                ↓
│    ↓          Commit
│  Return      Changes
│    ↓             ↓
│  Success     Success
│                                     │
└─────────────────────────────────────┘
```

### Implementation

```python
from datetime import datetime
from peewee import IntegrityError

class UserCRUDService:
    def __init__(self, repository):
        self.user_repo = repository
    
    # CREATE
    def create_user(self, username, email, full_name):
        """Create a new user with validation."""
        # Validate input
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if "@" not in email:
            raise ValueError("Invalid email format")
        if not full_name:
            raise ValueError("Full name is required")
        
        # Create model instance
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            is_active=True
        )
        
        try:
            # Save to database
            created_user = self.user_repo.create(user)
            print(f"✓ Created user: {created_user}")
            return created_user
        except IntegrityError as e:
            if "username" in str(e):
                raise ValueError(f"Username '{username}' already exists")
            elif "email" in str(e):
                raise ValueError(f"Email '{email}' already exists")
            else:
                raise
    
    # READ
    def get_user_by_username(self, username):
        """Retrieve user by username."""
        user = self.user_repo.get_by_username(username)
        if not user:
            raise ValueError(f"User '{username}' not found")
        return user
    
    def get_user_by_id(self, user_id):
        """Retrieve user by ID."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User ID {user_id} not found")
        return user
    
    def list_all_users(self):
        """Retrieve all active users."""
        users = self.user_repo.get_all(include_deleted=False)
        return users
    
    # UPDATE
    def update_user_profile(self, user_id, **kwargs):
        """Update user profile with validation."""
        # Verify user exists
        user = self.get_user_by_id(user_id)
        
        # Validate fields
        allowed_fields = ["full_name", "email"]
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            raise ValueError("No valid fields to update")
        
        # Update each field
        for field_name, value in updates.items():
            try:
                rows_affected = self.user_repo.update(user_id, (field_name, value))
                print(f"✓ Updated {field_name}: {rows_affected} row(s)")
            except Exception as e:
                raise ValueError(f"Failed to update {field_name}: {e}")
        
        # Return updated user
        return self.get_user_by_id(user_id)
    
    # DELETE
    def delete_user(self, user_id, soft=True):
        """Delete user (soft or hard delete)."""
        # Verify user exists
        user = self.get_user_by_id(user_id)
        
        if soft:
            # Soft delete (logical delete)
            rows_affected = self.user_repo.delete(user_id)
            print(f"✓ Soft deleted user: {rows_affected} row(s)")
        else:
            # Hard delete (permanent)
            rows_affected = self.user_repo.delete_hard(user_id)
            print(f"✓ Permanently deleted user: {rows_affected} row(s)")
        
        return rows_affected > 0

# Usage Example
if __name__ == "__main__":
    db = DatabaseSingleton.get_instance()
    db.configure("crud_demo.db", soft_delete_enabled=True)
    db.connect()
    db.create_tables()
    
    user_repo = UserRepository(db._db)
    crud_service = UserCRUDService(user_repo)
    
    try:
        # Create
        alice = crud_service.create_user("alice", "alice@example.com", "Alice Smith")
        
        # Read
        user = crud_service.get_user_by_username("alice")
        print(f"Retrieved: {user}")
        
        # Update
        updated = crud_service.update_user_profile(alice.id, full_name="Alice Johnson")
        print(f"Updated: {updated}")
        
        # Delete
        crud_service.delete_user(alice.id, soft=True)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.disconnect()
```

---

## User Registration Flow

**Scenario**: New user registration with validation, duplicate checking, and welcome initialization.

### Flow Diagram

```
User Registration Request
    ↓
Validate Input (username, email, password)
    ↓
Check Username Availability
    ├─ Available → Continue
    └─ Taken → Return Error
    ↓
Check Email Availability
    ├─ Available → Continue
    └─ Taken → Return Error
    ↓
Hash Password
    ↓
Create User Record
    ├─ Success → Continue
    └─ Error → Rollback & Return Error
    ↓
Create User Profile
    ├─ Success → Continue
    └─ Error → Rollback & Return Error
    ↓
Send Verification Email
    ↓
Return Success
```

### Implementation

```python
import hashlib
import re
from datetime import datetime

class RegistrationService:
    def __init__(self, db, user_repo, email_service=None):
        self.db = db
        self.user_repo = user_repo
        self.email_service = email_service
    
    def validate_registration_data(self, username, email, password, password_confirm):
        """Validate all registration input."""
        errors = []
        
        # Username validation
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters")
        elif len(username) > 50:
            errors.append("Username must be at most 50 characters")
        elif not re.match(r"^[a-zA-Z0-9_-]+$", username):
            errors.append("Username can only contain letters, numbers, _, and -")
        
        # Email validation
        if not email or "@" not in email or "." not in email.split("@")[1]:
            errors.append("Invalid email format")
        
        # Password validation
        if not password or len(password) < 8:
            errors.append("Password must be at least 8 characters")
        elif password != password_confirm:
            errors.append("Passwords do not match")
        
        return errors
    
    def check_username_available(self, username):
        """Check if username is available."""
        existing = self.user_repo.get_by_username(username)
        return existing is None
    
    def check_email_available(self, email):
        """Check if email is available."""
        existing = self.user_repo.get_by_email(email)
        return existing is None
    
    def hash_password(self, password):
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, email, full_name, password, password_confirm):
        """Register a new user with full validation."""
        
        # Step 1: Validate input
        validation_errors = self.validate_registration_data(
            username, email, password, password_confirm
        )
        if validation_errors:
            return {
                "success": False,
                "errors": validation_errors
            }
        
        # Step 2: Check username availability
        if not self.check_username_available(username):
            return {
                "success": False,
                "errors": [f"Username '{username}' is already taken"]
            }
        
        # Step 3: Check email availability
        if not self.check_email_available(email):
            return {
                "success": False,
                "errors": [f"Email '{email}' is already registered"]
            }
        
        # Step 4: Create user in transaction
        try:
            with self.db.transaction() as txn:
                # Hash password
                password_hash = self.hash_password(password)
                
                # Create user
                user = User(
                    username=username,
                    email=email,
                    full_name=full_name,
                    is_active=True
                )
                created_user = self.user_repo.create(user)
                
                # Store password_hash (in real app, use a separate table)
                # For demo, assume User model has password_hash field
                self.user_repo.update(created_user.id, ("password_hash", password_hash))
                
                print(f"✓ User registered: {created_user}")
                
                # Step 5: Send welcome email (if email service available)
                if self.email_service:
                    self.email_service.send_welcome_email(email, full_name)
                    print(f"✓ Welcome email sent to {email}")
                
                return {
                    "success": True,
                    "message": f"Welcome {full_name}! Registration successful.",
                    "user_id": created_user.id
                }
        
        except Exception as e:
            print(f"✗ Registration failed: {e}")
            # Transaction is automatically rolled back
            return {
                "success": False,
                "errors": ["Registration failed. Please try again."]
            }

# Usage Example
registration = RegistrationService(db, user_repo)
result = registration.register_user(
    username="newuser",
    email="newuser@example.com",
    full_name="New User",
    password="SecurePassword123",
    password_confirm="SecurePassword123"
)
print(result)
```

---

## Soft Delete & Recovery Flow

**Scenario**: Managing deleted records with recovery capability.

### Flow Diagram

```
Record in System
    ↓
DELETE REQUEST
    ↓
Mark deleted_at = NOW()
    ├─ Record still in DB
    ├─ Excluded from normal queries
    └─ Queryable with include_deleted=True
    ↓
RECOVERY REQUEST
    ├─ Set deleted_at = NULL
    └─ Record returns to active queries
    ↓
Record Active Again
```

### Implementation

```python
class SoftDeleteService:
    def __init__(self, repository):
        self.repo = repository
    
    def soft_delete(self, entity_id):
        """Soft delete an entity."""
        # Verify exists and not already deleted
        entity = self.repo.get_by_id(entity_id, include_deleted=False)
        if not entity:
            raise ValueError(f"Cannot delete: entity {entity_id} not found")
        
        # Soft delete
        rows = self.repo.delete(entity_id)
        print(f"✓ Soft deleted: {rows} row(s)")
        
        # Verify it's deleted but recoverable
        deleted_entity = self.repo.get_by_id(entity_id, include_deleted=True)
        if deleted_entity and deleted_entity.is_deleted():
            print(f"✓ Entity marked as deleted: {deleted_entity.deleted_at}")
            return True
        
        return False
    
    def get_deleted_entities(self):
        """Get all soft-deleted entities."""
        deleted = self.repo.get_deleted_users()
        print(f"Found {len(deleted)} deleted entities")
        return deleted
    
    def recover_entity(self, entity_id):
        """Recover a soft-deleted entity."""
        # Verify it's actually deleted
        entity = self.repo.get_by_id(entity_id, include_deleted=True)
        if not entity:
            raise ValueError(f"Entity {entity_id} not found even in deleted records")
        
        if not entity.is_deleted():
            raise ValueError(f"Entity {entity_id} is not deleted")
        
        # Restore
        rows = self.repo.restore(entity_id)
        print(f"✓ Recovered: {rows} row(s)")
        
        # Verify recovery
        recovered = self.repo.get_by_id(entity_id)
        if recovered:
            print(f"✓ Entity recovered: {recovered}")
            return True
        
        return False
    
    def permanently_delete(self, entity_id):
        """Permanently delete a soft-deleted entity."""
        # Verify it exists (deleted or not)
        entity = self.repo.get_by_id(entity_id, include_deleted=True)
        if not entity:
            raise ValueError(f"Entity {entity_id} not found")
        
        # Hard delete
        rows = self.repo.delete_hard(entity_id)
        print(f"✓ Permanently deleted: {rows} row(s)")
        
        # Verify gone
        missing = self.repo.get_by_id(entity_id, include_deleted=True)
        return missing is None
    
    def audit_trail(self):
        """Show deletion timeline."""
        active = self.repo.get_all(include_deleted=False)
        deleted = self.repo.get_all(include_deleted=True)
        deleted = [u for u in deleted if u.is_deleted()]
        
        print(f"Active: {len(active)}")
        for entity in active:
            print(f"  - {entity} (created: {entity.created_at})")
        
        print(f"\nDeleted: {len(deleted)}")
        for entity in deleted:
            print(f"  - {entity} (deleted: {entity.deleted_at})")

# Usage Example
soft_delete_service = SoftDeleteService(user_repo)

# Delete
soft_delete_service.soft_delete(1)

# View deleted
deleted_users = soft_delete_service.get_deleted_entities()

# Recover
soft_delete_service.recover_entity(1)

# Show timeline
soft_delete_service.audit_trail()
```

---

## Data Import Flow

**Scenario**: Importing data from CSV or JSON file into the database.

### Flow Diagram

```
CSV/JSON File
    ↓
Parse File
    ↓
For Each Record:
    ├─ Transform to model
    ├─ Validate data
    ├─ Check for duplicates
    ├─ Create record
    ├─ Log success/failure
    └─ Continue
    ↓
Commit All Changes
    ↓
Report Results
    ├─ Created: N
    ├─ Skipped: M
    ├─ Failed: K
    └─ Summary
```

### Implementation

```python
import json
import csv
from typing import List, Dict, Tuple

class DataImportService:
    def __init__(self, db, repository):
        self.db = db
        self.repo = repository
    
    def import_from_csv(self, filepath: str) -> Dict:
        """Import users from CSV file."""
        results = {
            "created": 0,
            "skipped": 0,
            "errors": [],
            "records": []
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                with self.db.transaction():
                    for row_num, row in enumerate(reader, start=2):  # Start at 2 (skip header)
                        try:
                            # Step 1: Transform data
                            user_data = {
                                "username": row.get("username", "").strip(),
                                "email": row.get("email", "").strip(),
                                "full_name": row.get("full_name", "").strip(),
                            }
                            
                            # Step 2: Validate
                            if not all([user_data["username"], user_data["email"], user_data["full_name"]]):
                                results["skipped"] += 1
                                results["records"].append({
                                    "row": row_num,
                                    "status": "skipped",
                                    "reason": "Missing required fields"
                                })
                                continue
                            
                            # Step 3: Check for duplicates
                            existing = self.repo.get_by_username(user_data["username"])
                            if existing:
                                results["skipped"] += 1
                                results["records"].append({
                                    "row": row_num,
                                    "username": user_data["username"],
                                    "status": "skipped",
                                    "reason": "Username already exists"
                                })
                                continue
                            
                            # Step 4: Create record
                            user = User(**user_data)
                            self.repo.create(user)
                            
                            results["created"] += 1
                            results["records"].append({
                                "row": row_num,
                                "username": user_data["username"],
                                "status": "created"
                            })
                        
                        except Exception as e:
                            results["errors"].append({
                                "row": row_num,
                                "error": str(e)
                            })
                            results["records"].append({
                                "row": row_num,
                                "status": "error",
                                "reason": str(e)
                            })
        
        except FileNotFoundError:
            results["errors"].append(f"File not found: {filepath}")
        except Exception as e:
            results["errors"].append(f"Import failed: {str(e)}")
        
        return results
    
    def import_from_json(self, filepath: str) -> Dict:
        """Import users from JSON file."""
        results = {
            "created": 0,
            "skipped": 0,
            "errors": [],
            "records": []
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both list and dict formats
            users_data = data if isinstance(data, list) else [data]
            
            with self.db.transaction():
                for idx, user_data in enumerate(users_data):
                    try:
                        # Step 1: Transform
                        user = User(
                            username=user_data.get("username"),
                            email=user_data.get("email"),
                            full_name=user_data.get("full_name"),
                        )
                        
                        # Step 2: Validate
                        if not user.username or not user.email:
                            results["skipped"] += 1
                            continue
                        
                        # Step 3: Check duplicates
                        if self.repo.get_by_username(user.username):
                            results["skipped"] += 1
                            continue
                        
                        # Step 4: Create
                        self.repo.create(user)
                        results["created"] += 1
                    
                    except Exception as e:
                        results["errors"].append(f"Record {idx}: {str(e)}")
        
        except Exception as e:
            results["errors"].append(f"JSON import failed: {str(e)}")
        
        return results
    
    def report_import(self, results: Dict) -> str:
        """Generate import report."""
        report = f"""
╔════════════════════════════════════════╗
║         IMPORT REPORT                  ║
╠════════════════════════════════════════╣
║ Created:   {results['created']:>6}                ║
║ Skipped:   {results['skipped']:>6}                ║
║ Errors:    {len(results['errors']):>6}                ║
╚════════════════════════════════════════╝
        """
        
        if results['errors']:
            report += "\nErrors:\n"
            for error in results['errors'][:5]:  # Show first 5 errors
                report += f"  - {error}\n"
        
        return report

# Usage Example
import_service = DataImportService(db, user_repo)

# Import from CSV
results = import_service.import_from_csv("users.csv")
print(import_service.report_import(results))

# Import from JSON
results = import_service.import_from_json("users.json")
print(import_service.report_import(results))
```

---

## Data Export Flow

**Scenario**: Exporting data to CSV, JSON, or other formats.

### Flow Diagram

```
Query Database
    ↓
Fetch Records
    ↓
Transform to Export Format
    ├─ Model → Dictionary
    ├─ Dictionary → JSON/CSV
    └─ Handle Dates & Types
    ↓
Write to File
    ↓
Verify Export
    ↓
Return Success
```

### Implementation

```python
import json
import csv
from datetime import datetime

class DataExportService:
    def __init__(self, repository):
        self.repo = repository
    
    def export_to_json(self, filepath: str, include_deleted=False) -> Dict:
        """Export users to JSON format."""
        try:
            # Fetch records
            users = self.repo.get_all(include_deleted=include_deleted)
            
            # Transform to JSON-serializable format
            users_data = []
            for user in users:
                user_dict = self.repo.domain_to_dict(user)
                
                # Handle datetime fields
                if isinstance(user_dict.get('created_at'), datetime):
                    user_dict['created_at'] = user_dict['created_at'].isoformat()
                if isinstance(user_dict.get('updated_at'), datetime):
                    user_dict['updated_at'] = user_dict['updated_at'].isoformat()
                if user_dict.get('deleted_at'):
                    user_dict['deleted_at'] = user_dict['deleted_at'].isoformat()
                
                users_data.append(user_dict)
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=2)
            
            return {
                "success": True,
                "file": filepath,
                "records": len(users_data),
                "message": f"Exported {len(users_data)} users to {filepath}"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_to_csv(self, filepath: str, include_deleted=False) -> Dict:
        """Export users to CSV format."""
        try:
            # Fetch records
            users = self.repo.get_all(include_deleted=include_deleted)
            
            if not users:
                return {
                    "success": False,
                    "error": "No users to export"
                }
            
            # Get all field names from first user
            first_user = self.repo.domain_to_dict(users[0])
            fieldnames = list(first_user.keys())
            
            # Write CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for user in users:
                    row = self.repo.domain_to_dict(user)
                    # Convert datetime to string
                    for key, value in row.items():
                        if isinstance(value, datetime):
                            row[key] = value.isoformat()
                    writer.writerow(row)
            
            return {
                "success": True,
                "file": filepath,
                "records": len(users),
                "message": f"Exported {len(users)} users to {filepath}"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_to_dict_list(self, include_deleted=False) -> List[Dict]:
        """Export to Python list of dictionaries."""
        users = self.repo.get_all(include_deleted=include_deleted)
        return [self.repo.domain_to_dict(u) for u in users]
    
    def export_single_as_json(self, user_id: int) -> str:
        """Export single user as JSON string."""
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        return self.repo.domain_to_json(user)

# Usage Example
export_service = DataExportService(user_repo)

# Export all to JSON
result = export_service.export_to_json("users_export.json")
print(result["message"])

# Export to CSV
result = export_service.export_to_csv("users_export.csv")
print(result["message"])

# Export single user
json_str = export_service.export_single_as_json(1)
print(json_str)
```

---

## Batch Operations Flow

**Scenario**: Performing operations on multiple records efficiently.

### Flow Diagram

```
Prepare Batch (List of Operations)
    ↓
Start Transaction
    ├─ Operation 1: Create/Update/Delete
    ├─ Operation 2: Create/Update/Delete
    ├─ Operation 3: Create/Update/Delete
    ├─ ... Continue with batch
    └─ All succeed OR all rollback (atomic)
    ↓
Commit Transaction
    ↓
Report Results
    ├─ Success count
    ├─ Failure count
    └─ Error details
```

### Implementation

```python
from typing import List, Callable, Any

class BatchOperationService:
    def __init__(self, db, repository):
        self.db = db
        self.repo = repository
    
    def batch_create(self, users_data: List[Dict]) -> Dict:
        """Create multiple users in a transaction."""
        results = {
            "created": 0,
            "failed": 0,
            "errors": [],
            "details": []
        }
        
        try:
            with self.db.transaction():
                for idx, data in enumerate(users_data):
                    try:
                        user = User(**data)
                        self.repo.create(user)
                        
                        results["created"] += 1
                        results["details"].append({
                            "index": idx,
                            "status": "created",
                            "username": data.get("username")
                        })
                    
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append({
                            "index": idx,
                            "error": str(e),
                            "data": data
                        })
                        results["details"].append({
                            "index": idx,
                            "status": "failed",
                            "error": str(e)
                        })
                        # Continue with next, transaction will rollback if fatal
        
        except Exception as e:
            # Transaction rolled back
            results["errors"].insert(0, f"Batch transaction failed: {str(e)}")
            results["created"] = 0
        
        return results
    
    def batch_update(self, updates: List[Tuple[int, str, Any]]) -> Dict:
        """Update multiple records in a transaction.
        
        Args:
            updates: List of (id, field_name, new_value) tuples
        """
        results = {
            "updated": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            with self.db.transaction():
                for user_id, field_name, new_value in updates:
                    try:
                        rows = self.repo.update(user_id, (field_name, new_value))
                        results["updated"] += rows
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"Failed to update user {user_id}: {str(e)}")
        
        except Exception as e:
            results["errors"].insert(0, f"Batch update transaction failed: {str(e)}")
            results["updated"] = 0
        
        return results
    
    def batch_delete(self, user_ids: List[int], soft=True) -> Dict:
        """Delete multiple users in a transaction."""
        results = {
            "deleted": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            with self.db.transaction():
                for user_id in user_ids:
                    try:
                        if soft:
                            rows = self.repo.delete(user_id)
                        else:
                            rows = self.repo.delete_hard(user_id)
                        
                        results["deleted"] += rows
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"Failed to delete user {user_id}: {str(e)}")
        
        except Exception as e:
            results["errors"].insert(0, f"Batch delete transaction failed: {str(e)}")
            results["deleted"] = 0
        
        return results
    
    def batch_operation(self, operations: List[Dict]) -> Dict:
        """Execute mix of create/update/delete in single transaction.
        
        Format:
            [
                {"action": "create", "data": {...}},
                {"action": "update", "id": 1, "field": "name", "value": "New Name"},
                {"action": "delete", "id": 2, "soft": True},
            ]
        """
        results = {
            "processed": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            with self.db.transaction():
                for idx, op in enumerate(operations):
                    try:
                        action = op.get("action")
                        
                        if action == "create":
                            user = User(**op.get("data", {}))
                            self.repo.create(user)
                        
                        elif action == "update":
                            self.repo.update(op["id"], (op["field"], op["value"]))
                        
                        elif action == "delete":
                            if op.get("soft", True):
                                self.repo.delete(op["id"])
                            else:
                                self.repo.delete_hard(op["id"])
                        
                        results["processed"] += 1
                    
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"Operation {idx} failed: {str(e)}")
        
        except Exception as e:
            results["errors"].insert(0, f"Batch operation transaction failed: {str(e)}")
            results["processed"] = 0
        
        return results

# Usage Example
batch_service = BatchOperationService(db, user_repo)

# Batch create
users_data = [
    {"username": "user1", "email": "user1@example.com", "full_name": "User One"},
    {"username": "user2", "email": "user2@example.com", "full_name": "User Two"},
]
result = batch_service.batch_create(users_data)
print(f"Created: {result['created']}, Failed: {result['failed']}")

# Batch update
updates = [
    (1, "full_name", "Updated One"),
    (2, "is_active", False),
]
result = batch_service.batch_update(updates)
print(f"Updated: {result['updated']}")

# Batch delete
result = batch_service.batch_delete([1, 2], soft=True)
print(f"Deleted: {result['deleted']}")
```

---

## Error Handling Pattern

**Scenario**: Handling various error conditions gracefully.

### Implementation

```python
from contextlib import contextmanager
from peewee import IntegrityError, OperationalError

class ErrorCategory:
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    DUPLICATE = "duplicate"
    DATABASE_ERROR = "database_error"
    UNKNOWN = "unknown"

class APIResponse:
    def __init__(self, success, data=None, error=None, error_category=None):
        self.success = success
        self.data = data
        self.error = error
        self.error_category = error_category
    
    def to_dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "error_category": self.error_category
        }

class ErrorHandlingService:
    def __init__(self, repository):
        self.repo = repository
    
    @contextmanager
    def handle_operation(self, operation_name: str):
        """Context manager for safe operation execution."""
        try:
            yield
        except ValueError as e:
            # Validation errors
            message = f"{operation_name} validation failed: {str(e)}"
            print(f"✗ {message}")
            raise APIResponse(
                success=False,
                error=message,
                error_category=ErrorCategory.VALIDATION_ERROR
            )
        except IntegrityError as e:
            # Database constraint violations
            if "unique" in str(e).lower():
                message = f"{operation_name}: Record already exists (duplicate)"
                error_category = ErrorCategory.DUPLICATE
            else:
                message = f"{operation_name}: Database constraint violation"
                error_category = ErrorCategory.DATABASE_ERROR
            
            print(f"✗ {message}")
            raise APIResponse(
                success=False,
                error=message,
                error_category=error_category
            )
        except Exception as e:
            # Unexpected errors
            message = f"{operation_name} failed: {str(e)}"
            print(f"✗ {message}")
            raise APIResponse(
                success=False,
                error=message,
                error_category=ErrorCategory.UNKNOWN
            )
    
    def create_user_safe(self, username, email, full_name):
        """Create user with error handling."""
        try:
            with self.handle_operation("User creation"):
                # Validation
                if not username or len(username) < 3:
                    raise ValueError("Username must be at least 3 characters")
                if "@" not in email:
                    raise ValueError("Invalid email")
                
                # Create
                user = User(username=username, email=email, full_name=full_name)
                created = self.repo.create(user)
                
                return APIResponse(
                    success=True,
                    data=self.repo.domain_to_dict(created)
                )
        
        except APIResponse as api_resp:
            return api_resp
    
    def get_user_safe(self, user_id):
        """Get user with error handling."""
        try:
            user = self.repo.get_by_id(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            return APIResponse(
                success=True,
                data=self.repo.domain_to_dict(user)
            )
        
        except ValueError as e:
            return APIResponse(
                success=False,
                error=str(e),
                error_category=ErrorCategory.NOT_FOUND
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=str(e),
                error_category=ErrorCategory.UNKNOWN
            )

# Usage Example
error_service = ErrorHandlingService(user_repo)

# Safe create
response = error_service.create_user_safe("alice", "alice@example.com", "Alice")
print(response.to_dict())

# Safe get
response = error_service.get_user_safe(1)
print(response.to_dict())
```

---

## Multi-Repository Coordination Flow

**Scenario**: Coordinating operations across multiple models/repositories.

### Flow Diagram

```
User Creates Post
    ↓
Start Transaction
    ├─ Create Post (PostRepository)
    ├─ Create PostMetadata (MetadataRepository)
    ├─ Update User Stats (UserRepository)
    ├─ Create Activity Log (LogRepository)
    └─ All succeed OR all rollback
    ↓
Commit Transaction
```

### Implementation

```python
class PostService:
    def __init__(self, db, user_repo, post_repo, metadata_repo, log_repo):
        self.db = db
        self.user_repo = user_repo
        self.post_repo = post_repo
        self.metadata_repo = metadata_repo
        self.log_repo = log_repo
    
    def create_post_with_logging(self, user_id, title, content):
        """Create post with metadata and logging in transaction."""
        try:
            with self.db.transaction():
                # Step 1: Verify user exists
                user = self.user_repo.get_by_id(user_id)
                if not user:
                    raise ValueError(f"User {user_id} not found")
                
                # Step 2: Create post
                post = Post(
                    user_id=user_id,
                    title=title,
                    content=content
                )
                created_post = self.post_repo.create(post)
                print(f"✓ Post created: {created_post.id}")
                
                # Step 3: Create metadata
                metadata = PostMetadata(
                    post_id=created_post.id,
                    word_count=len(content.split()),
                    character_count=len(content)
                )
                self.metadata_repo.create(metadata)
                print(f"✓ Metadata created")
                
                # Step 4: Update user stats
                self.user_repo.increment_post_count(user_id)
                print(f"✓ User stats updated")
                
                # Step 5: Log activity
                log_entry = ActivityLog(
                    user_id=user_id,
                    action="post_created",
                    resource_type="post",
                    resource_id=created_post.id,
                    details=f"Created post: {title}"
                )
                self.log_repo.create(log_entry)
                print(f"✓ Activity logged")
                
                return {
                    "success": True,
                    "post_id": created_post.id,
                    "message": "Post created successfully with all related records"
                }
        
        except Exception as e:
            print(f"✗ Transaction rolled back: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Post creation failed - all changes rolled back"
            }

# Usage Example
post_service = PostService(db, user_repo, post_repo, metadata_repo, log_repo)
result = post_service.create_post_with_logging(
    user_id=1,
    title="My First Post",
    content="This is the content of my first post..."
)
print(result)
```

---

## Audit Logging Flow

**Scenario**: Tracking all changes for compliance and debugging.

### Flow Diagram

```
Any Database Operation
    ↓
Log Operation Details:
├─ User (WHO)
├─ Action (WHAT)
├─ Timestamp (WHEN)
├─ Old Value
└─ New Value
    ↓
Store in AuditLog
    ↓
Available for:
├─ Compliance reports
├─ Debugging
├─ User activity tracking
└─ System analysis
```

### Implementation

```python
from datetime import datetime
from enum import Enum

class AuditAction(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RESTORE = "restore"

class AuditLogger:
    def __init__(self, db, audit_repo):
        self.db = db
        self.audit_repo = audit_repo
    
    def log_create(self, entity_type: str, entity_id: int, data: Dict, user_id=None):
        """Log entity creation."""
        log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=AuditAction.CREATE.value,
            old_value=None,
            new_value=json.dumps(data, default=str),
            user_id=user_id,
            timestamp=datetime.utcnow()
        )
        self.audit_repo.create(log)
    
    def log_update(self, entity_type: str, entity_id: int, field: str, old_value, new_value, user_id=None):
        """Log entity update."""
        log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=AuditAction.UPDATE.value,
            old_value=str(old_value),
            new_value=str(new_value),
            user_id=user_id,
            timestamp=datetime.utcnow()
        )
        self.audit_repo.create(log)
    
    def log_delete(self, entity_type: str, entity_id: int, data: Dict, user_id=None):
        """Log entity deletion."""
        log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=AuditAction.DELETE.value,
            old_value=json.dumps(data, default=str),
            new_value=None,
            user_id=user_id,
            timestamp=datetime.utcnow()
        )
        self.audit_repo.create(log)
    
    def get_entity_history(self, entity_type: str, entity_id: int):
        """Get complete change history for an entity."""
        logs = self.audit_repo.get_by_fields({
            "entity_type": entity_type,
            "entity_id": entity_id
        })
        
        history = []
        for log in logs:
            history.append({
                "timestamp": log.timestamp,
                "action": log.action,
                "old_value": log.old_value,
                "new_value": log.new_value,
                "user_id": log.user_id
            })
        
        return history
    
    def get_user_activity(self, user_id: int, limit=100):
        """Get all activities by a user."""
        logs = self.audit_repo.get_by_field("user_id", user_id)
        return logs[:limit]
    
    def generate_report(self, entity_type: str, start_date=None, end_date=None):
        """Generate audit report for entity type."""
        query = AuditLog.select().where(AuditLog.entity_type == entity_type)
        
        if start_date:
            query = query.where(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.where(AuditLog.timestamp <= end_date)
        
        logs = list(query)
        
        # Summarize
        summary = {
            "total_changes": len(logs),
            "creates": sum(1 for log in logs if log.action == AuditAction.CREATE.value),
            "updates": sum(1 for log in logs if log.action == AuditAction.UPDATE.value),
            "deletes": sum(1 for log in logs if log.action == AuditAction.DELETE.value),
            "by_user": {}
        }
        
        # Group by user
        for log in logs:
            user_id = log.user_id or "system"
            if user_id not in summary["by_user"]:
                summary["by_user"][user_id] = 0
            summary["by_user"][user_id] += 1
        
        return summary

# Usage Example
audit_logger = AuditLogger(db, audit_repo)

# Log operations
audit_logger.log_create("User", 1, {"username": "alice", "email": "alice@example.com"})
audit_logger.log_update("User", 1, "full_name", "Alice", "Alice Smith", user_id=2)
audit_logger.log_delete("User", 1, {"username": "alice"})

# Get history
history = audit_logger.get_entity_history("User", 1)
print(history)

# Generate report
report = audit_logger.generate_report("User")
print(report)
```

---

## Summary Table

| Flow | Use Case | Key Tools | Transaction Needed |
|------|----------|-----------|-------------------|
| System Init | App startup | DatabaseSingleton | No |
| CRUD | Basic operations | BaseRepository | Per operation |
| User Registration | New users | Validation + CRUD | Yes |
| Soft Delete | Logical removal | get_all(include_deleted) | No |
| Data Import | Bulk load | CSV/JSON parsing | Yes |
| Data Export | Bulk extract | DataTransformer | No |
| Batch Ops | Multiple changes | Transactions | Yes |
| Error Handling | Graceful failures | Try/except | Contextual |
| Multi-Repo | Cross-model ops | Multiple repos | Yes |
| Audit Logging | Change tracking | AuditLog model | Per log |

---

## Quick Reference

### Start Application
```python
db = DatabaseSingleton.get_instance()
db.configure("app.db", soft_delete_enabled=True)
db.connect()
db.create_tables()
```

### Create Record
```python
user = User(username="alice", email="alice@example.com")
user_repo.create(user)
```

### Update Record
```python
user_repo.update(user_id, ("field_name", new_value))
```

### Delete (Soft)
```python
user_repo.delete(user_id)
```

### Query All (Exclude Deleted)
```python
users = user_repo.get_all(include_deleted=False)
```

### Query All (Include Deleted)
```python
users = user_repo.get_all(include_deleted=True)
```

### Atomic Transaction
```python
with db.transaction():
    # all ops atomic
    user1.save()
    user2.save()
```

### Export to JSON
```python
user_json = user_repo.domain_to_json(user)
```

### Stop Application
```python
db.disconnect()
```
