# src/sales.py
# This file is for Epic SCRUM-3 (Sales Transaction Management)
# Owned by: Sara Larkem

"""This module handles the complex logic of processing a sale."""

from src.database_manager import (
    get_product_details,
    start_transaction,
    log_item_sale,
    adjust_stock
)


def validate_product_input(product_id_str):
    """
    scrum-38: validate product ID input
    returns (is_valid, product_id, error_message)
    """
    try:
        product_id = int(product_id_str)
        if product_id <= 0:
            return False, None, "Product ID must be a positive number"
        return True, product_id, None
    except ValueError:
        return False, None, "Product ID must be a valid number"


def validate_quantity_input(quantity_str):
    """
    scrum-38: validate quantity input
    returns (is_valid, quantity, error_message)
    """
    try:
        quantity = int(quantity_str)
        if quantity <= 0:
            return False, None, "Quantity must be a positive number"
        return True, quantity, None
    except ValueError:
        return False, None, "Quantity must be a valid number"


def check_stock_availability(product_id, requested_quantity):
    """
    scrum-38: pre-sale check for stock availability
    returns (is_available, product_data, error_message)
    """
    product = get_product_details(product_id)

    if product is None:
        return False, None, f"Product with ID {product_id} not found"

    if product["quantity_on_hand"] < requested_quantity:
        return False, product, (
            f"Insufficient stock for {product['name']}. "
            f"Available: {product['quantity_on_hand']}, Requested: {requested_quantity}"
        )

    return True, product, None


def display_cart(cart):
    """
    scrum-40: display current cart contents
    """
    if not cart:
        print("Cart is empty.")
        return

    print("\n--- Current Cart ---")
    total = 0.0
    for item in cart:
        item_total = item['price'] * item['quantity']
        total += item_total
        print(f"{item['name']} - Quantity: {item['quantity']} @ "
              f"${item['price']:.2f} = ${item_total:.2f}")
    print(f"Total: ${total:.2f}")


def process_sale(cart):
    """
    scrum-37: process the sale transaction
    creates transaction record, logs items, and updates inventory
    returns (success, message)
    """
    if not cart:
        return False, "Cannot process empty cart"

    # Calculate total
    total_amount = sum(item['price'] * item['quantity'] for item in cart)

    # Create transaction record
    transaction_id = start_transaction(total_amount)
    if transaction_id is None:
        return False, "Failed to create transaction record"

    # Log each item and update stock
    for item in cart:
        # Log the item sale
        if not log_item_sale(transaction_id, item['product_id'], item['quantity'], item['price']):
            return False, f"Failed to log sale for {item['name']}"

        # Adjust stock (scrum-28)
        new_stock = item['current_stock'] - item['quantity']
        if not adjust_stock(item['product_id'], new_stock):
            return False, f"Failed to update stock for {item['name']}"

    return True, f"Sale completed successfully! Transaction ID: {transaction_id}"


def record_sale():
    """
    Handles the logic for SCRUM-12: "As a Store Clerk, I want to record a
    sale..."

    Implementation:
    - SCRUM-39: Develop the "Process Sale" interface (cart management)
    - SCRUM-38: Add pre-sale checks (stock availability)
    - SCRUM-37: Implement the process_sale() function
    - SCRUM-40: Display a final summary

    Returns:
        bool: True if sale was successfully processed, False otherwise
    """
    print("\n=== Record a Sale ===")
    cart = []

    # SCRUM-39: Cart interface - loop to add items
    while True:
        print("\n[1] Add item to cart")
        print("[2] View cart")
        print("[3] Complete sale")
        print("[0] Cancel and exit")

        choice = input("Enter choice: ").strip()

        if choice == '1':
            # Add item to cart
            product_id_str = input("Enter Product ID: ").strip()

            # Validate product ID
            is_valid, product_id, error = validate_product_input(product_id_str)
            if not is_valid:
                print(f"Error: {error}")
                continue

            quantity_str = input("Enter quantity: ").strip()

            # Validate quantity
            is_valid, quantity, error = validate_quantity_input(quantity_str)
            if not is_valid:
                print(f"Error: {error}")
                continue

            # SCRUM-38: Pre-sale check for stock availability
            is_available, product, error = check_stock_availability(product_id, quantity)
            if not is_available:
                print(f"Error: {error}")
                continue

            # Add to cart
            cart.append({
                'product_id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'current_stock': product['quantity_on_hand']
            })

            print(f"Added {quantity} x {product['name']} to cart.")

        elif choice == '2':
            # SCRUM-40: View cart
            display_cart(cart)

        elif choice == '3':
            # Complete sale
            if not cart:
                print("Error: Cart is empty. Please add items before completing sale.")
                continue

            # SCRUM-40: Display final summary
            print("\n=== Sale Summary ===")
            display_cart(cart)

            confirm = input("\nConfirm sale? (y/n): ").strip().lower()
            if confirm == 'y':
                # SCRUM-37: Process the sale
                success, message = process_sale(cart)
                if success:
                    print(f"\n{message}")
                    return True
                else:
                    print(f"\nError: {message}")
                    return False
            else:
                print("Sale cancelled.")
                return False

        elif choice == '0':
            print("Sale cancelled.")
            return False

        else:
            print("Invalid choice. Please try again.")


# --- Backlog (Not in Sprint 1) ---
# SCRUM-13 (View Sales History) will be implemented here in a future sprint.
