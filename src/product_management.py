# src/product_management.py
# This file is for Epic SCRUM-1 (Product Management)
# Owned by: Lucy O'Connor

# This module will contain the business logic for adding, updating,
# and viewing products in the 'booze' table.

from src.database_manager import get_db_connection # and other db functions

def add_new_product():
    """
    Handles the logic for SCRUM-5: "As a Store Manager, I want to add a new 
    product..."
    
    TODO (Lucy):
    1. Implement SCRUM-26: Create the CLI input screen.
       - Ask the user for name, brand, type, price, initial stock, etc.
    2. Implement SCRUM-25: Add client-side validation.
       - Check for non-negative price/stock before sending to DB.
    3. Call the new db.insert_product() function (from SCRUM-24) 
       to save the new product.
    4. Print a success or error message.
    5. SCRUM-27 (Unit Test) will be handled in 'tests/test_product_management.py'
    """
    print("Function 'add_new_product' is not yet implemented.")
    pass

# --- Backlog (Not in Sprint 1) ---
# SCRUM-6 (Update Product) and SCRUM-7 (View All Products)
# will be implemented here in a future sprint.