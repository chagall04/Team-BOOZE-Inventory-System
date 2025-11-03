# src/inventory_tracking.py
# This file is for Epic SCRUM-2 (Inventory Tracking)
# Owned by: Séan Bardon

# This module contains the business logic for managing stock levels.

from src.database_manager import get_db_connection # and other db functions

def receive_new_stock():
    """
    Handles the logic for SCRUM-9: "As a Store Clerk, I want to receive new
    stock so that the inventory is updated correctly."
    
    Returns:
        bool: True if stock was successfully updated, False otherwise
    """
    print("\n--- Receive New Stock ---")
    
    # SCRUM-30: CLI interface for receiving stock
    try:
        product_id = int(input("Enter Product ID: "))
    except ValueError:
        print("Error: Product ID must be a number.")
        return False
        
    try:
        quantity_to_add = int(input("Enter quantity to add: "))
        if quantity_to_add < 0:
            raise ValueError("Quantity cannot be negative")
    except ValueError as e:
        print(f"Error: {str(e)}")
        return False
    
    # Get current stock level (SCRUM-29)
    from src.database_manager import get_stock_by_id, adjust_stock
    current_stock = get_stock_by_id(product_id)
    
    if current_stock is None:
        print(f"Error: Product with ID {product_id} not found.")
        return False
    
    # Calculate new stock level
    new_stock_level = current_stock['quantity'] + quantity_to_add
    
    # Update the database (SCRUM-28)
    if adjust_stock(product_id, new_stock_level):
        print(f"\nSuccess! Updated stock for {current_stock['name']}:")
        print(f"Previous stock level: {current_stock['quantity']}")
        print(f"Added: {quantity_to_add}")
        print(f"New stock level: {new_stock_level}")
        return True
    else:
        print("Error: Failed to update stock level.")
        return False

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