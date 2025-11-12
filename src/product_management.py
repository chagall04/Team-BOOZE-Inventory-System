# src/product_management.py
# This file is for Epic SCRUM-1 (Product Management)
# Owned by: Lucy O'Connor

"""This module contains the business logic for adding, updating,
and viewing products in the 'booze' table."""

import sqlite3
from src.database_manager import insert_product

def validate_required_field(field_value, field_name):
    """Validate that a required field is not empty"""
    if not field_value or len(field_value.strip()) == 0:
        return [f"{field_name} is required"]
    return []

def get_min_value_error(field_name, min_value, max_value):
    """Get appropriate error message for minimum value validation"""
    if field_name == "Price":
        return [f"{field_name} must be non-negative"]
    if field_name == "Initial stock":
        return [f"{field_name} quantity must be non-negative"]
    if field_name == "Volume" and min_value == 1:
        return [f"{field_name} must be greater than 0"]
    return [f"{field_name} must be between 0 and {max_value}"]

def get_value_error(field_name, convert_func):
    """Get appropriate error message for value conversion errors"""
    if convert_func == int and field_name == "Initial stock":
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
        quantity, "Initial stock", int, min_value=0)
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
    print(f"\nError: Failed to add product - {result}")
    return False





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
        conn = sqlite3.connect('inventory.db')
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

def update_product_cli():
    """
    CLI flow for SCRUM-43: Update Product
    - prompts for product id
    - shows current values
    - prompts for new values (press Enter to keep current)
    - validates and calls database_manager.update_product_details()
    """
    from src import database_manager

    print("\n=== Update Product ===")

    def get_product_id_from_input():
        pid_input = input("Enter Product ID to update: ").strip()
        try:
            return int(pid_input)
        except ValueError:
            return None

    product_id = get_product_id_from_input()
    if product_id is None:
        print("Invalid product ID")
        return False

    found, res = lookup_product_by_id(product_id)
    if not found:
        print(res)
        return False

    product = res
    print("\nCurrent product details (leave blank to keep current value):")

    # Prompt for all fields in a compact loop
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

    # Validation helpers to keep main flow simple
    def required_str(key, display_name):
        val = inputs.get(key)
        if val is None:
            return None, None
        if not val.strip():
            return None, f"{display_name} is required"
        return val.strip(), None

    def optional_str_or_none(key):
        val = inputs.get(key)
        if val is None:
            return None, None
        return (val.strip() if val.strip() else None), None

    def parse_numeric(key, display_name, conv, min_value=None, max_value=None, whole=False):
        val = inputs.get(key)
        if val is None:
            return None, None
        if val == "":
            # explicit blank means set to None for optional numeric fields
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

    # Build update payload
    update_data = {}
    errors = []

    # Required textual fields
    for key, display in (('name', 'Product name'), ('brand', 'Brand name'), ('type', 'Product type')):
        val, err = required_str(key, display)
        if err:
            errors.append(err)
        elif val is not None:
            # map 'type' key to 'type' as earlier code used 'type' as column name
            update_data['type' if key == 'type' else key] = val

    # Price
    price_val, price_err = parse_numeric('price', 'Price', float, min_value=0)
    if price_err:
        errors.append(price_err)
    elif price_val is not None:
        update_data['price'] = price_val

    # Quantity
    qty_val, qty_err = parse_numeric('quantity', 'Quantity', int, min_value=0, whole=True)
    if qty_err:
        errors.append(qty_err)
    elif qty_val is not None:
        update_data['quantity_on_hand'] = qty_val

    # ABV (optional, allow blank -> keep or clear)
    abv_val, abv_err = parse_numeric('abv', 'ABV', float, min_value=0, max_value=100)
    if abv_err:
        errors.append(abv_err)
    elif 'abv' in inputs:
        # explicit blank should set to None, handled by parse_numeric returning (None, None)
        if inputs['abv'] == "":
            update_data['abv'] = None
        elif abv_val is not None:
            update_data['abv'] = abv_val

    # Volume
    vol_val, vol_err = parse_numeric('volume_ml', 'Volume', int, min_value=1, whole=True)
    if vol_err:
        errors.append(vol_err)
    elif 'volume_ml' in inputs:
        if inputs['volume_ml'] == "":
            update_data['volume_ml'] = None
        elif vol_val is not None:
            update_data['volume_ml'] = vol_val

    # Origin and description
    origin_val, _ = optional_str_or_none('origin_country')
    if origin_val is not None or ('origin_country' in inputs and inputs['origin_country'] == ""):
        update_data['origin_country'] = origin_val

    desc_val, _ = optional_str_or_none('description')
    if desc_val is not None or ('description' in inputs and inputs['description'] == ""):
        update_data['description'] = desc_val

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
