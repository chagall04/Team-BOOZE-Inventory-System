# src/product_management.py
# This file is for Epic SCRUM-1 (Product Management)
# Owned by: Lucy O'Connor

"""This module contains the business logic for adding, updating,
and viewing products in the 'booze' table."""

from src.database_manager import insert_product

# Constants
INITIAL_STOCK_FIELD = "Initial stock"

def validate_required_field(field_value, field_name):
    """Validate that a required field is not empty"""
    if not field_value or len(field_value.strip()) == 0:
        return [f"{field_name} is required"]
    return []

def get_min_value_error(field_name, min_value, max_value):
    """Get appropriate error message for minimum value validation"""
    if field_name == "Price":
        return f"{field_name} must be non-negative"
    if field_name == INITIAL_STOCK_FIELD:
        return f"{field_name} quantity must be non-negative"
    if field_name == "Volume" and min_value == 1:
        return f"{field_name} must be greater than 0"
    return f"{field_name} must be between 0 and {max_value}"

def get_value_error_message(field_name, convert_func):
    """Get appropriate error message for value conversion errors"""
    if convert_func == int and field_name == INITIAL_STOCK_FIELD:
        return f"{field_name} must be a valid whole number"
    return f"{field_name} must be a valid number"

def validate_numeric_value(value, field_name, convert_func, min_value=None, max_value=None):
    """Validate numeric fields with optional range checks"""
    try:
        num_value = convert_func(value)
        if min_value is not None and num_value < min_value:
            error_msg = get_min_value_error(field_name, min_value, max_value)
            return [error_msg], None
        if max_value is not None and num_value > max_value:
            return [f"{field_name} must be between 0 and {max_value}"], None
        return [], num_value
    except ValueError:
        error_msg = get_value_error_message(field_name, convert_func)
        return [error_msg], None

def validate_product_data(name, brand, type_, price, quantity, abv=None, volume_ml=None):
    """Client-side validation for product data (SCRUM-25)"""
    errors = []

    # Required fields validation
    errors.extend(validate_required_field(name, "Product name"))
    errors.extend(validate_required_field(brand, "Brand name"))
    errors.extend(validate_required_field(type_, "Product type"))

    # Price validation
    price_errors, _ = validate_numeric_value(
        price, "Price", float, min_value=0)
    errors.extend(price_errors)

    # Quantity validation
    quantity_errors, _ = validate_numeric_value(
        quantity, INITIAL_STOCK_FIELD, int, min_value=0)
    errors.extend(quantity_errors)

    # Optional field validation
    if abv and abv.strip():
        abv_errors, _ = validate_numeric_value(
            abv, "ABV", float, min_value=0, max_value=100)
        errors.extend(abv_errors)

    if volume_ml and volume_ml.strip():
        volume_errors, _ = validate_numeric_value(volume_ml, "Volume", int, min_value=1)
        errors.extend(volume_errors)

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
    price = input("Price (€): ").strip()
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
    print(f"\nError: Failed to add product - {result}")
    return False

# --- Backlog (Not in Sprint 1) ---
# SCRUM-6 (Update Product) and SCRUM-7 (View All Products)
# will be implemented here in a future sprint.
