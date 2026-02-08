from repos.product_repo import ProductRepository
from models.product import Product
from repos.user_repo import UserRepository
from models.user import User

from dbpykitpw import DatabaseSingleton

# Initialize and configure the Database
db = DatabaseSingleton.get_instance()
db.configure("./app.db", soft_delete_enabled=True)
db.create_tables()

# Print DatabaseSingleton information
print(f"DatabaseSingleton instance: {db}")
print(f"Available repositories: {db._repositories.keys()}")
print(f"Available models: {db._models.keys()}")

# Example usage of UserRepository
UserRepositoryClass = db.get_repository("user_repo")
user_repo = UserRepositoryClass(db._db)  # Instantiate the repository with database

# Fetch all column info of the User model
ids = user_repo.get_column_info("user", db._db)
for each in ids:
    print(each)

# Get the User model object
user_model = user_repo.model
print(f"User model: {user_model}")

# User model fields (attributes)
print(f"User model fields: {user_model._meta.fields.keys()}")

# Example CRUD operations for User and Product

def create_record_from_dict(repo, data):
    """
    Create a new record in the database using the provided repository and data dictionary.

    Args:
        repo: The repository instance to use for creating the record
        data: A dictionary containing the field values for the new record
    Returns:
        The created model instance
    """
    # Ensure that the data is passed to the model to create an instance
    model_instance = repo.model(**data)  # Create model instance using data
    created_instance = repo.create(model_instance)  # Use base repository create method
    return created_instance

def get_user_dict():
    """
    Returns a dictionary of user data
    """
    return {
        "email": "test@email.com",
        "username": "testuser",
        "is_active": True,
        "first_name": "Test",
        "last_name": "User",
        "full_name": "Test User",
        "birth_date": "1990-01-01",
        "phone_number": "123-456-7890"
    }

def get_product_dict(user_id):
    """
    Returns a dictionary of product data, with a foreign key to the user.
    """
    return {
        "name": "Product 1",
        "description": "This is a product",
        "price": 29.99,
        "user": user_id  # FK to user
    }

def main():
    # Create a new user
    user_data = get_user_dict()
    created_user = create_record_from_dict(user_repo, user_data)
    print(f"Created User: {created_user}")

    # Create a new product for the created user
    ProductRepositoryClass = db.get_repository("product_repo")
    product_repo = ProductRepositoryClass(db._db)  # Instantiate the repository
    product_data = get_product_dict(created_user.id)
    created_product = create_record_from_dict(product_repo, product_data)
    print(f"Created Product: {created_product}")

    # Fetch the user and their associated products (one-to-many relationship)
    print("\nFetching User and Products:")
    user_with_products = user_repo.model.select().where(user_repo.model.id == created_user.id).first()
    print(f"User: {user_with_products}")
    products = created_user.products  # Assuming 'products' is a relationship
    for product in products:
        print(f"Product: {product}")

    # Demonstrating CRUD operations for the user and product

    # 1. **Read**: Fetch user by ID
    fetched_user = user_repo.model.get(user_repo.model.id == created_user.id)
    print(f"\nFetched User: {fetched_user}")

    # 2. **Update**: Update the product price
    updated_product = created_product
    updated_product.price = 49.99
    updated_product.save()
    print(f"Updated Product: {updated_product}")

    # 3. **Delete**: Delete the product
    created_product.delete_instance()
    print(f"Deleted Product: {created_product}")

    # Fetch all users from DB after deletion
    print("\nAll Users in DB:")
    all_users = user_repo.model.select()
    for user in all_users:
        print(f"User: {user}")

    # Fetch all products after deletion
    print("\nAll Products in DB (after deletion):")
    all_products = product_repo.model.select()
    for product in all_products:
        print(f"Product: {product}")

if __name__ == "__main__":
    main()
