# src/inventory_tracking.py
# This file is for Epic SCRUM-2 (Inventory Tracking)
# Owned by: Séan Bardon

"""This module contains the business logic for managing stock levels."""

from colorama import Fore, Style

from .database_manager import get_stock_by_id, adjust_stock, search_products_by_term

# Constants for user prompts
PROMPT_PRODUCT_ID = f"{Fore.YELLOW}Enter Product ID: {Style.RESET_ALL}"
ERROR_PRODUCT_ID_NOT_NUMBER = f"{Fore.RED}Error: Product ID must be a number.{Style.RESET_ALL}"

def receive_new_stock():
    """
    Handles the logic for SCRUM-9: "As a Store Clerk, I want to receive new
    stock so that the inventory is updated correctly."

    Returns:
        bool: True if stock was successfully updated, False otherwise
    """
    print(f"\n{Fore.CYAN}--- Receive New Stock ---{Style.RESET_ALL}")

    # SCRUM-30: CLI interface for receiving stock
    try:
        product_id = int(input(PROMPT_PRODUCT_ID))
    except ValueError:
        print(ERROR_PRODUCT_ID_NOT_NUMBER)
        return False

    try:
        quantity_to_add = int(input(f"{Fore.YELLOW}Enter quantity to add: {Style.RESET_ALL}"))
        if quantity_to_add < 0:
            raise ValueError("Quantity cannot be negative")
    except ValueError as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        return False

    # Get current stock level (SCRUM-29)
    current_stock = get_stock_by_id(product_id)

    if current_stock is None:
        print(f"{Fore.RED}Error: Product with ID {product_id} not found.{Style.RESET_ALL}")
        return False

    # Calculate new stock level
    new_stock_level = current_stock['quantity'] + quantity_to_add

    # Update the database (SCRUM-28)
    update_result = adjust_stock(product_id, new_stock_level)
    if not update_result:
        print(f"\n{Fore.RED}Error: Failed to update stock level in database.{Style.RESET_ALL}")
        return False

    # If we get here, update was successful
    print(f"\n{Fore.GREEN}Success! Updated stock for {current_stock['name']}:{Style.RESET_ALL}")
    print(f"Previous stock level: {current_stock['quantity']}")
    print(f"Added: {Fore.GREEN}+{quantity_to_add}{Style.RESET_ALL}")
    print(f"New stock level: {Fore.WHITE}{new_stock_level}{Style.RESET_ALL}")
    return True

def view_current_stock():
    """
    Handles the logic for SCRUM-11: "As a Store Clerk, I want to view the
    current stock level of a product."

    Returns:
        bool: True if stock was successfully displayed, False if there was an error
    """
    print(f"\n{Fore.CYAN}--- View Current Stock ---{Style.RESET_ALL}")

    # SCRUM-32: Handle product lookup
    try:
        product_id = int(input(PROMPT_PRODUCT_ID))
    except ValueError:
        print(ERROR_PRODUCT_ID_NOT_NUMBER)
        return False

    # SCRUM-29: Get stock data from database
    stock_data = get_stock_by_id(product_id)

    if stock_data is None:
        print(f"{Fore.RED}Error: Product with ID {product_id} not found.{Style.RESET_ALL}")
        return False

    # SCRUM-34: Format and display the data
    print(f"\n{Fore.WHITE}Stock Information:{Style.RESET_ALL}")
    print(f"Product Name: {Fore.CYAN}{stock_data['name']}{Style.RESET_ALL}")
    print(f"Current Stock: {Fore.WHITE}{stock_data['quantity']}{Style.RESET_ALL} units")
    return True

def log_product_loss():
    """
    Handles the logic for SCRUM-10: "As a Store Clerk, I want to log a product
    loss so that the inventory is adjusted correctly."

    Returns:
        bool: True if loss was successfully logged, False otherwise
    """
    print(f"\n{Fore.CYAN}--- Log Product Loss ---{Style.RESET_ALL}")

    # SCRUM-48: CLI interface for logging product loss
    try:
        product_id = int(input(PROMPT_PRODUCT_ID))
    except ValueError:
        print(ERROR_PRODUCT_ID_NOT_NUMBER)
        return False

    # SCRUM-49: Reuse get_stock_by_id() to fetch current stock
    current_stock = get_stock_by_id(product_id)

    if current_stock is None:
        print(f"{Fore.RED}Error: Product with ID {product_id} not found.{Style.RESET_ALL}")
        return False

    # Get quantity lost from user
    try:
        quantity_lost_input = input(f"{Fore.YELLOW}Enter quantity lost: {Style.RESET_ALL}")
        quantity_lost = int(quantity_lost_input)
    except ValueError:
        print(f"{Fore.RED}Error: Quantity lost must be a number.{Style.RESET_ALL}")
        return False
    if quantity_lost < 0:
        print(f"{Fore.RED}Error: Quantity lost cannot be negative{Style.RESET_ALL}")
        return False
    if quantity_lost == 0:
        print(f"{Fore.RED}Error: Quantity lost must be greater than zero{Style.RESET_ALL}")
        return False

    # Verify we have enough stock to lose
    if quantity_lost > current_stock['quantity']:
        print(f"{Fore.RED}Error: Cannot log loss of {quantity_lost} units. "
              f"Current stock is only {current_stock['quantity']} units.{Style.RESET_ALL}")
        return False

    # Calculate new stock level
    new_stock_level = current_stock['quantity'] - quantity_lost

    # SCRUM-50: Reuse adjust_stock() function, passing in the new quantity
    update_result = adjust_stock(product_id, new_stock_level)
    if not update_result:
        print(f"\n{Fore.RED}Error: Failed to update stock level in database.{Style.RESET_ALL}")
        return False

    # If we get here, update was successful
    print(f"\n{Fore.GREEN}Success! Logged loss for {current_stock['name']}:{Style.RESET_ALL}")
    print(f"Previous stock level: {current_stock['quantity']}")
    print(f"Lost: {Fore.RED}-{quantity_lost}{Style.RESET_ALL}")
    print(f"New stock level: {Fore.WHITE}{new_stock_level}{Style.RESET_ALL}")
    return True

def search_products():
    """
    Handles logic for SCRUM-66: "As a Store Clerk, I want to search products..."
    
    Implementation:
    - SCRUM-68: Get input and display results
    """
    print(f"\n{Fore.CYAN}--- Search Products ---{Style.RESET_ALL}")
    
    # Get search term
    search_term = input(f"{Fore.YELLOW}Enter search term (name or brand): {Style.RESET_ALL}").strip()
    
    if len(search_term) == 0:
        print(f"{Fore.RED}Error: Search term cannot be empty.{Style.RESET_ALL}")
        return False

    # Query database (SCRUM-67)
    results = search_products_by_term(search_term)
    
    # Display results
    if not results:
        print(f"\n{Fore.YELLOW}No products found matching '{search_term}'.{Style.RESET_ALL}")
        return True
        
    print(f"\n{Fore.GREEN}Found {len(results)} matching products:{Style.RESET_ALL}")
    print("-" * 75)
    print(f"{Fore.WHITE}{'ID':<5} {'Product Name':<25} {'Brand':<15} {'Stock':<8} {'Price':<10}{Style.RESET_ALL}")
    print("-" * 75)
    
    for product in results:
        p_id = product["id"]
        name = product["name"][:25]  # truncate for display
        brand = product["brand"][:15] if product["brand"] else "N/A"
        qty = product["quantity_on_hand"]
        price = product["price"]
        
        print(f"{p_id:<5} {name:<25} {brand:<15} {qty:<8} {Fore.GREEN}€{price:<9.2f}{Style.RESET_ALL}")
        
    print("-" * 75)
    return True

# --- Backlog (Not in Sprint 1) ---
# SCRUM-10 (Log Product Loss) has been implemented above.
