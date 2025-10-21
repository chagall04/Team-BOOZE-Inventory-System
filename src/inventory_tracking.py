# src/inventory_tracking.py
# This file is for Epic SCRUM-2 (Inventory Tracking)
# Owned by: Séan Bardon

# This module contains the business logic for managing stock levels.

from src.database_manager import get_db_connection # and other db functions

def receive_new_stock():
    """
    Handles the logic for SCRUM-9: "As a Store Clerk, I want to receive new
    stock..."
    
    TODO (Séan):
    1. Implement SCRUM-30: Create the "Receive Stock" CLI screen.
       - Ask user for the product ID to update.
       - Ask for the quantity being added.
    2. Call the db.get_stock_by_id() function (SCRUM-29) to get current stock.
    3. Calculate new_stock = current_stock + quantity_added.
    4. Call the db.adjust_stock() function (SCRUM-28) to save the new total.
    5. Print a success message.
    6. SCRUM-31 (Unit Test) will be handled in 'tests/test_inventory_tracking.py'
    """
    print("Function 'receive_new_stock' is not yet implemented.")
    pass

def view_current_stock():
    """
    Handles the logic for SCRUM-11: "As a Store Clerk, I want to view the
    current stock level..."
    
    TODO (Séan):
    1. Implement SCRUM-32: Create a function to handle product lookup.
       - Ask user for the product ID to view.
    2. Call the db.get_stock_by_id() function (SCRUM-29) to get the data.
    3. Implement SCRUM-34: Format the retrieved data for clear display.
       - e.g., print(f"Product: {product_name}, Current Stock: {stock_level}")
    4. This is already integrated into the 'View Stock' menu (SCRUM-33)
       in app.py.
    """
    print("Function 'view_current_stock' is not yet implemented.")
    pass

# --- Backlog (Not in Sprint 1) ---
# SCRUM-10 (Log Product Loss) will be implemented here in a future sprint.