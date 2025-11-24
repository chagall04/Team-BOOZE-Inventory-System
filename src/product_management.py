# src/product_management.py
# This file is for Epic SCRUM-1 (Product Management)
# Owned by: Lucy O'Connor

"""This module contains the business logic for adding, updating,
and viewing products in the 'booze' table."""

import sqlite3
from src.database_manager import insert_product, get_db_connection, get_all_products

# Constants for field names
INITIAL_STOCK_FIELD = "Initial stock"

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
        return [f"{field_name} must be non-negative"]
    if field_name == INITIAL_STOCK_FIELD:
        return [f"{field_name} quantity must be non-negative"]
    if field_name == "Volume" and min_value == 1:
        return [f"{field_name} must be greater than 0"]
    return [f"{field_name} must be between 0 and {max_value}"]

def get_value_error(field_name, convert_func):
    """Get appropriate error message for value conversion errors"""
    if convert_func == int and field_name == INITIAL_STOCK_FIELD:
        return [f"{field_name} must be a valid whole number"]
    return [f"{field_name} must be a valid number"]

def validate_numeric_value(value, field_name, convert_func, min_value=None, max_value=None):
    """Validate numeric fields with optional range checks"""
    try:
        num_value = convert_func(value)
        if min_value is not None and num_value < min_value:
            return get_min_value_error(field_name, min_value, max_value), None
        if max_value is not None and num_value > max_value:
            return [f"{field_name} must be between 0 and {max_value}"], None
        return [], num_value
    except ValueError:
        return get_value_error(field_name, convert_func), None

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


def view_all_products():
    """
    SCRUM-46: Display all products in inventory
    
    Shows a clear, paginated list with key details:
    - ID, name, price, current stock
    """
    print("\n=== All Products ===")
    
    products = get_all_products()
    
    if not products:
        print("No products found in inventory.")
        return
    
    # Display header
    print(f"\n{'ID':<5} {'Name':<30} {'Brand':<20} {'Price (€)':<12} {'Stock':<8}")
    print("-" * 80)
    
    # Display each product
    for product in products:
        price_formatted = f"€{product['price']:.2f}"
        print(f"{product['id']:<5} {product['name']:<30} {product['brand']:<20} "
              f"{price_formatted:<12} {product['quantity_on_hand']:<8}")
    
    print(f"\nTotal products: {len(products)}")
    return True


def lookup_product_by_id(product_id):
    """
    Look up a product by its ID in the database.
    
    Args:
        product_id (int): The ID of the product to find
        
    Returns:
        tuple: (success, result) where:
            - success (bool): True if product was found, False if error occurred
            - result: Dict with product data if found, error message if not
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query the database for the product
        cursor.execute("""
            SELECT id, name, brand, type, price, quantity_on_hand, 
                   abv, volume_ml, origin_country, description
            FROM booze 
            WHERE id = ?
        """, (product_id,))
        
        row = cursor.fetchone()
        
        if row is None:
            return False, f"No product found with ID: {product_id}"
            
        # Convert row to dictionary
        product = {
            'id': row[0],
            'name': row[1],
            'brand': row[2],
            'type': row[3],
            'price': row[4],
            'quantity': row[5],
            'abv': row[6],
            'volume_ml': row[7],
            'origin_country': row[8],
            'description': row[9]
        }
        
        return True, product
        
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"
    finally:
        if 'conn' in locals():
            conn.close()
            
            
def prompt_with_default(prompt_text, default):
    """Prompt showing the current/default value; return None if user leaves blank."""
    val = input(f"{prompt_text} [{default}]: ").strip()
    return None if val == "" else val


def _validate_required_str(val, display_name):
    """Validate required string field."""
    if val is None:
        return None, None
    # User entered a non-empty value - validate it's not just whitespace
    if not val or not val.strip():
        return None, f"{display_name} is required"
    return val.strip(), None


def _validate_optional_str(val):
    """Validate optional string field."""
    if val is None:
        return None, None
    return (val.strip() if val.strip() else None), None


def _validate_numeric(val, display_name, conv, min_value=None, max_value=None, whole=False):
    """Validate numeric field with optional range checks."""
    if val is None:
        return None, None
    if val == "":
        return None, None
    try:
        num = conv(val)
    except ValueError:
        if whole:
            return None, f"{display_name} must be a valid whole number"
        return None, f"{display_name} must be a valid number"
    if min_value is not None and num < min_value:
        if display_name.lower().startswith("price"):
            return None, f"{display_name} must be non-negative"
        return None, f"{display_name} must be between {min_value} and {max_value if max_value is not None else '∞'}"
    if max_value is not None and num > max_value:
        return None, f"{display_name} must be between {min_value if min_value is not None else 0} and {max_value}"
    return num, None


def _get_product_id_from_input():
    """Get and validate product ID from user input."""
    pid_input = input("Enter Product ID to update: ").strip()
    try:
        return int(pid_input)
    except ValueError:
        return None


def _collect_user_inputs(product):
    """Collect all user inputs for product update."""
    prompts = [
        ('name', "Product Name", product['name']),
        ('brand', "Brand", product['brand']),
        ('type', "Type", product['type']),
        ('price', "Price (numeric)", product['price']),
        ('quantity', "Quantity on hand (whole number)", product['quantity']),
        ('abv', "ABV %", product['abv'] if product['abv'] is not None else ""),
        ('volume_ml', "Volume in ml", product['volume_ml'] if product['volume_ml'] is not None else ""),
        ('origin_country', "Country of Origin", product['origin_country'] if product['origin_country'] else ""),
        ('description', "Description", product['description'] if product['description'] else "")
    ]
    
    inputs = {}
    for key, prompt_text, default in prompts:
        inputs[key] = prompt_with_default(prompt_text, default)
    return inputs


def _process_required_fields(inputs, update_data, errors):
    """Process and validate required text fields."""
    for key, display in (('name', 'Product name'), ('brand', 'Brand name'), ('type', 'Product type')):
        val, err = _validate_required_str(inputs.get(key), display)
        if err:
            errors.append(err)
        elif val is not None:
            update_data[key] = val


def _process_price_field(inputs, update_data, errors):
    """Process and validate price field."""
    price_val, price_err = _validate_numeric(inputs.get('price'), 'Price', float, min_value=0)
    if price_err:
        errors.append(price_err)
    elif price_val is not None:
        update_data['price'] = price_val


def _process_quantity_field(inputs, update_data, errors):
    """Process and validate quantity field."""
    qty_val, qty_err = _validate_numeric(inputs.get('quantity'), 'Quantity', int, min_value=0, whole=True)
    if qty_err:
        errors.append(qty_err)
    elif qty_val is not None:
        update_data['quantity_on_hand'] = qty_val


def _process_optional_numeric_field(inputs, update_data, errors, field_key, display_name, conv, min_val, max_val=None):
    """Process and validate optional numeric field."""
    val, err = _validate_numeric(inputs.get(field_key), display_name, conv, min_value=min_val, max_value=max_val, whole=(conv == int))
    if err:
        errors.append(err)
    elif val is not None:
        update_data[field_key] = val


def _process_optional_text_field(inputs, update_data, field_key):
    """Process and validate optional text field."""
    val, _ = _validate_optional_str(inputs.get(field_key))
    if val is not None:
        update_data[field_key] = val


def _validate_and_build_update_data(inputs):
    """Validate inputs and build update data dictionary."""
    update_data = {}
    errors = []

    _process_required_fields(inputs, update_data, errors)
    _process_price_field(inputs, update_data, errors)
    _process_quantity_field(inputs, update_data, errors)
    _process_optional_numeric_field(inputs, update_data, errors, 'abv', 'ABV', float, 0, 100)
    _process_optional_numeric_field(inputs, update_data, errors, 'volume_ml', 'Volume', int, 1)
    _process_optional_text_field(inputs, update_data, 'origin_country')
    _process_optional_text_field(inputs, update_data, 'description')

    return update_data, errors


def update_product_cli():
    """
    CLI flow for SCRUM-6: Update Product
    - prompts for product id
    - shows current values
    - prompts for new values (press Enter to keep current)
    - validates and calls database_manager.update_product()
    """
    from src import database_manager

    print("\n=== Update Product ===")

    product_id = _get_product_id_from_input()
    if product_id is None:
        print("Invalid product ID")
        return False

    found, res = lookup_product_by_id(product_id)
    if not found:
        print(res)
        return False

    product = res
    print("\nCurrent product details (leave blank to keep current value):")

    inputs = _collect_user_inputs(product)
    update_data, errors = _validate_and_build_update_data(inputs)

    if errors:
        print("\nError: Invalid input:")
        for e in errors:
            print(f"- {e}")
        return False

    if not update_data:
        print("No changes provided.")
        return False

    success, msg = database_manager.update_product(product_id, update_data)
    if success:
        print(f"Success: {msg}")
        return True

    print(f"Error: {msg}")
    return False
