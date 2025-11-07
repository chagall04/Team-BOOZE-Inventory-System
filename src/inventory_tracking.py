# src/inventory_tracking.py
# This file is for Epic SCRUM-2 (Inventory Tracking)
# Owned by: Séan Bardon

"""This module contains the business logic for managing stock levels."""

from .database_manager import get_stock_by_id, adjust_stock

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
    current_stock = get_stock_by_id(product_id)

    if current_stock is None:
        print(f"Error: Product with ID {product_id} not found.")
        return False

    # Calculate new stock level
    new_stock_level = current_stock['quantity'] + quantity_to_add

    # Update the database (SCRUM-28)
    update_result = adjust_stock(product_id, new_stock_level)
    if not update_result:
        print("\nError: Failed to update stock level in database.")
        return False

    # If we get here, update was successful
    print(f"\nSuccess! Updated stock for {current_stock['name']}:")
    print(f"Previous stock level: {current_stock['quantity']}")
    print(f"Added: {quantity_to_add}")
    print(f"New stock level: {new_stock_level}")
    return True

def view_current_stock():
    """
    Handles the logic for SCRUM-11: "As a Store Clerk, I want to view the
    current stock level of a product."

    Returns:
        bool: True if stock was successfully displayed, False if there was an error
    """
    print("\n--- View Current Stock ---")

    # SCRUM-32: Handle product lookup
    try:
        product_id = int(input("Enter Product ID: "))
    except ValueError:
        print("Error: Product ID must be a number.")
        return False

    # SCRUM-29: Get stock data from database
    stock_data = get_stock_by_id(product_id)

    if stock_data is None:
        print(f"Error: Product with ID {product_id} not found.")
        return False

    # SCRUM-34: Format and display the data
    print("\nStock Information:")
    print(f"Product Name: {stock_data['name']}")
    print(f"Current Stock: {stock_data['quantity']} units")
    return True

# --- Backlog (Not in Sprint 1) ---
# SCRUM-10 (Log Product Loss) will be implemented here in a future sprint.
