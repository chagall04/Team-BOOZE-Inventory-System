# src/product_management.py
# This file is for Epic SCRUM-1 (Product Management)
# Owned by: Lucy O'Connor

# This module will contain the business logic for adding, updating,
# and viewing products in the 'booze' table.

from src.database_manager import get_db_connection, insert_product

def validate_product_data(name, brand, type_, price, quantity, abv=None, volume_ml=None):
    """Client-side validation for product data (SCRUM-25)"""
    errors = []
    
    if not name or len(name.strip()) == 0:
        errors.append("Product name is required")
    if not brand or len(brand.strip()) == 0:
        errors.append("Brand name is required")
    if not type_ or len(type_.strip()) == 0:
        errors.append("Product type is required")
    
    try:
        price = float(price)
        if price < 0:
            errors.append("Price must be non-negative")
    except ValueError:
        errors.append("Price must be a valid number")
    
    try:
        quantity = int(quantity)
        if quantity < 0:
            errors.append("Initial stock quantity must be non-negative")
    except ValueError:
        errors.append("Initial stock must be a valid whole number")

    # Optional field validation
    if abv is not None and abv.strip():
        try:
            abv = float(abv)
            if abv < 0 or abv > 100:
                errors.append("ABV must be between 0 and 100")
        except ValueError:
            errors.append("ABV must be a valid number")
    
    if volume_ml is not None and volume_ml.strip():
        try:
            volume_ml = int(volume_ml)
            if volume_ml <= 0:
                errors.append("Volume must be greater than 0")
        except ValueError:
            errors.append("Volume must be a valid whole number")
    
    return len(errors) == 0, errors

def add_new_product():
    """
    Handles the logic for SCRUM-5: "As a Store Manager, I want to add a new 
    product..."
    
    Implementation covers:
    - SCRUM-26: CLI input screen for product details
    - SCRUM-25: Client-side validation
    - SCRUM-24: Database insertion via insert_product()
    """
    print("\n=== Add New Product ===")
    
    # Get user input (SCRUM-26)
    name = input("Product Name: ").strip()
    brand = input("Brand: ").strip()
    type_ = input("Type (e.g., Beer, Wine, Spirit): ").strip()
    price = input("Price: $").strip()
    quantity = input("Initial Stock Quantity: ").strip()
    
    # Optional details
    print("\nOptional Details (press Enter to skip):")
    abv = input("ABV % (e.g., 40.0): ").strip()
    volume_ml = input("Volume in ml (e.g., 700): ").strip()
    origin = input("Country of Origin: ").strip()
    description = input("Product Description: ").strip()
    
    # Validate input (SCRUM-25)
    is_valid, errors = validate_product_data(name, brand, type_, price, quantity, abv, volume_ml)
    
    if not is_valid:
        print("\nError: Invalid product data:")
        for error in errors:
            print(f"- {error}")
        return False
    
    # Prepare data for database
    product_data = {
        'name': name,
        'brand': brand,
        'type': type_,
        'price': float(price),
        'quantity': int(quantity),
        'abv': float(abv) if abv else None,
        'volume_ml': int(volume_ml) if volume_ml else None,
        'origin_country': origin if origin else None,
        'description': description if description else None
    }
    
    # Save to database (SCRUM-24)
    success, result = insert_product(product_data)
    
    if success:
        print(f"\nSuccess! Product '{name}' has been added with ID: {result}")
        return True
    else:
        print(f"\nError: Failed to add product - {result}")
        return False

# --- Backlog (Not in Sprint 1) ---
# SCRUM-6 (Update Product) and SCRUM-7 (View All Products)
# will be implemented here in a future sprint.