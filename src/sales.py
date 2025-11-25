# src/sales.py
# This file is for Epic SCRUM-3 (Sales Transaction Management)
# Owned by: Sara Larkem

"""This module handles the complex logic of processing a sale."""

from src.database_manager import (
    get_product_details,
    process_sale_transaction,
    get_transaction_by_id,
    get_items_for_transaction,
    get_all_transactions
)

# Constants
SALE_CANCELLED_MSG = "Sale cancelled."

# scrum-72: store last successfully completed transaction ID
LAST_TRANSACTION_ID = None


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


def check_stock_availability(product_id, requested_quantity, cart=None):
    """
    scrum-38: pre-sale check for stock availability
    Accounts for quantities already in cart to prevent overselling
    returns (is_available, product_data, error_message)
    """
    product = get_product_details(product_id)

    if product is None:
        return False, None, f"Product with ID {product_id} not found"

    # Calculate quantity already in cart for this product
    cart_quantity = 0
    if cart:
        for item in cart:
            if item['product_id'] == product_id:
                cart_quantity += item['quantity']

    # Check if total requested (cart + new request) exceeds available stock
    total_requested = cart_quantity + requested_quantity
    if product["quantity_on_hand"] < total_requested:
        return False, product, (
            f"Insufficient stock for {product['name']}. "
            f"Available: {product['quantity_on_hand']}, "
            f"Already in cart: {cart_quantity}, "
            f"Requested: {requested_quantity}, "
            f"Total needed: {total_requested}"
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
              f"€{item['price']:.2f} = €{item_total:.2f}")
    print(f"Total: €{total:.2f}")


def process_sale(cart):
    """
    scrum-37: process the sale transaction
    creates transaction record, logs items, and updates inventory atomically
    returns (success, message)
    """
    global LAST_TRANSACTION_ID   # scrum-72  # pylint: disable=global-statement

    if not cart:
        return False, "Cannot process empty cart"

    # calculate total
    total_amount = sum(item['price'] * item['quantity'] for item in cart)

    # process sale atomically (creates transaction, logs items, updates stock)
    success, result = process_sale_transaction(cart, total_amount)

    if success:
        # scrum-72: save last completed transaction ID
        LAST_TRANSACTION_ID = result
        return True, f"Sale completed successfully! Transaction ID: {result}"

    return False, f"Sale failed: {result}"


def handle_add_item_to_cart(cart):
    """Handle adding an item to the cart"""
    product_id_str = input("Enter Product ID: ").strip()

    # Validate product ID
    is_valid, product_id, error = validate_product_input(product_id_str)
    if not is_valid:
        print(f"Error: {error}")
        return

    quantity_str = input("Enter quantity: ").strip()

    # Validate quantity
    is_valid, quantity, error = validate_quantity_input(quantity_str)
    if not is_valid:
        print(f"Error: {error}")
        return

    # Pre-sale check for stock availability
    is_available, product, error = check_stock_availability(product_id, quantity, cart)
    if not is_available:
        print(f"Error: {error}")
        return

    # Add to cart
    cart.append({
        'product_id': product['id'],
        'name': product['name'],
        'price': product['price'],
        'quantity': quantity,
        'current_stock': product['quantity_on_hand']
    })

    print(f"Added {quantity} x {product['name']} to cart.")


def handle_complete_sale(cart):
    """Handle completing the sale transaction"""
    if not cart:
        print("Error: Cart is empty. Please add items before completing sale.")
        return None

    # Display final summary
    print("\n=== Sale Summary ===")
    display_cart(cart)

    confirm = input("\nConfirm sale? (y/n): ").strip().lower()
    if confirm == 'y':
        # Process the sale
        success, message = process_sale(cart)
        if success:
            print(f"\n{message}")
            return True
        print(f"\nError: {message}")
        return False
    print(SALE_CANCELLED_MSG)
    return False


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
            handle_add_item_to_cart(cart)
        elif choice == '2':
            display_cart(cart)
        elif choice == '3':
            result = handle_complete_sale(cart)
            if result is not None:
                return result
        elif choice == '0':
            print(SALE_CANCELLED_MSG)
            return False
        else:
            print("Invalid choice. Please try again.")


def print_receipt(transaction, items, title="TRANSACTION RECEIPT"):
    """
    Helper function to print formatted receipt
    Reduces code duplication between view_transaction_details and view_last_transaction
    """
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)
    print(f"Transaction ID: {transaction['id']}")
    print(f"Date/Time: {transaction['timestamp']}")
    print("-" * 50)
    print(f"{'Item':<30} {'Qty':<5} {'Price':<10} {'Total':<10}")
    print("-" * 50)

    for item in items:
        item_total = item['quantity'] * item['price_at_sale']
        print(f"{item['name']:<30} {item['quantity']:<5} "
              f"€{item['price_at_sale']:<9.2f} €{item_total:<9.2f}")

    print("-" * 50)
    print(f"{'TOTAL:':<46} €{transaction['total_amount']:.2f}")
    print("=" * 50)


def view_transaction_details():
    """
    scrum-63: View detailed receipt for a specific transaction ID.

    Prompts the user to enter a transaction ID, validates the input,
    retrieves the transaction and its items from the database, and prints
    a formatted receipt to the console.

    Returns:
        True if the transaction details were successfully displayed,
        False if there was an error (e.g., invalid input, transaction not found).
    """
    print("\n=== View Transaction Details ===")
    
    transaction_id_str = input("Enter Transaction ID: ").strip()
    
    # validate transaction ID input
    try:
        transaction_id = int(transaction_id_str)
        if transaction_id <= 0:
            print("Error: Transaction ID must be a positive number")
            return False
    except ValueError:
        print("Error: Transaction ID must be a valid number")
        return False
    
    # retrieve transaction details
    transaction = get_transaction_by_id(transaction_id)
    
    if transaction is None:
        print(f"Error: Transaction with ID {transaction_id} not found")
        return False
    
    # retrieve transaction items
    items = get_items_for_transaction(transaction_id)
    
    if not items:
        print(f"Error: No items found for transaction {transaction_id}")
        return False
    
    # print formatted receipt
    print_receipt(transaction, items, "TRANSACTION RECEIPT")
    
    return True


def view_last_transaction():
    """
    scrum-71: view receipt for the most recent completed sale
    """
    print("\n=== View Last Sale ===")

    if LAST_TRANSACTION_ID is None:
        print("No previous sale found.")
        return False

    # retrieve transaction details
    transaction = get_transaction_by_id(LAST_TRANSACTION_ID)
    if transaction is None:
        print("Error: Last transaction could not be retrieved")
        return False

    # retrieve items for the transaction
    items = get_items_for_transaction(LAST_TRANSACTION_ID)
    if not items:
        print("Error: No items found for last transaction")
        return False

    # print formatted receipt
    print_receipt(transaction, items, "LAST TRANSACTION RECEIPT")

    return True


def view_sales_history():
    """
    scrum-15: display list of all sales transactions
    allows user to select a transaction to view full details
    
    returns:
        True if history was displayed, False on error or empty
    """
    print("\n=== Sales History ===")
    
    transactions = get_all_transactions()
    
    if not transactions:
        print("No sales transactions found.")
        return False
    
    # display all transactions
    print(f"\n{'ID':<6} {'Date/Time':<20} {'Total':>10}")
    print("-" * 40)
    
    for txn in transactions:
        print(f"{txn['id']:<6} {txn['timestamp']:<20} €{txn['total_amount']:>9.2f}")
    
    print("-" * 40)
    print(f"Total transactions: {len(transactions)}")
    
    # prompt to view details
    print("\nEnter transaction ID to view details, or 0 to go back:")
    choice = input("Transaction ID: ").strip()
    
    if choice in ('0', ''):
        return True
    
    # validate transaction id
    try:
        transaction_id = int(choice)
        if transaction_id <= 0:
            print("Error: Transaction ID must be a positive number")
            return True
    except ValueError:
        print("Error: Transaction ID must be a valid number")
        return True
    
    # check if transaction exists in our list
    txn_ids = [t['id'] for t in transactions]
    if transaction_id not in txn_ids:
        print(f"Error: Transaction with ID {transaction_id} not found")
        return True
    
    # retrieve and display transaction details
    transaction = get_transaction_by_id(transaction_id)
    if transaction is None:
        print(f"Error: Could not retrieve transaction {transaction_id}")
        return True
    
    items = get_items_for_transaction(transaction_id)
    if not items:
        print(f"Error: No items found for transaction {transaction_id}")
        return True
    
    # print receipt
    print_receipt(transaction, items, "TRANSACTION DETAILS")
    
    return True
