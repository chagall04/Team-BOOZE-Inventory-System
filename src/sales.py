# src/sales.py
# This file is for Epic SCRUM-3 (Sales Transaction Management)
# Owned by: Sara Larkem

# This module handles the complex logic of processing a sale.

from src.database_manager import get_db_connection # and other db functions

def record_sale():
    """
    Handles the logic for SCRUM-12: "As a Store Clerk, I want to record a
    sale..."
    
    TODO (Sara):
    1. Implement SCRUM-39: Develop the "Process Sale" interface.
       - Create a "cart" (e.g., a list of dictionaries).
       - Loop to ask the clerk to input product IDs and quantities.
    2. Implement SCRUM-38: Add pre-sale checks.
       - For each item added to cart, call a db function (like Séan's
         SCRUM-29) to check if 'quantity_on_hand' is sufficient.
       - If not, show an error and don't add to cart.
    3. Implement SCRUM-37: Implement the process_sale() function.
       - When the cart is finalized, call your new db functions (SCRUM-36)
         to first create the 'transactions' record, then loop through
         the cart to create the 'transaction_items' records.
       - After the sale is logged, you must also call the
         db.adjust_stock() function (SCRUM-28) for each item to
         decrease the 'quantity_on_hand' in the 'booze' table.
    4. Implement SCRUM-40: Display a final summary.
       - Show the total price and items sold before committing the sale.
    """
    print("Function 'record_sale' is not yet implemented.")
    pass

# --- Backlog (Not in Sprint 1) ---
# SCRUM-13 (View Sales History) will be implemented here in a future sprint.