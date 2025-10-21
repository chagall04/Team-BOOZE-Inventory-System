# src/database_manager.py
import sqlite3

DB_NAME = "inventory.db"

def get_db_connection():
    """Establishes a connection to the database."""
    conn = sqlite3.connect(DB_NAME)
    # Return rows as dictionaries instead of tuples
    conn.row_factory = sqlite3.Row
    return conn

# --- Auth Functions (SCRUM-17) ---
def get_user_by_username(username):
    """Fetches a user's hashed password and role."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return {"hash": user_data["password_hash"], "role": user_data["role"]}
    return None

# --- Product Management Functions (SCRUM-5) ---
# TODO (Lucy): Implement SCRUM-24: db.insert_product(data)
# This function should take product data (name, brand, price, etc.)
# and execute an SQL INSERT statement on the 'booze' table.

# --- Inventory Tracking Functions (SCRUM-9 & SCRUM-11) ---
# TODO (Séan): Implement SCRUM-28: db.adjust_stock(product_id, quantity)
# This function should take a product_id and a new_quantity
# and execute an SQL UPDATE statement:
# "UPDATE booze SET quantity_on_hand = ? WHERE id = ?"

# TODO (Séan): Implement SCRUM-29: db.get_stock_by_id(product_id)
# This function should take a product_id and
# "SELECT name, quantity_on_hand FROM booze WHERE id = ?"
# It will be used by both SCRUM-9 (to get current stock) 
# and SCRUM-11 (to display stock).

# --- Sales Transaction Functions (SCRUM-12) ---
# TODO (Sara): Implement SCRUM-36: db.start_transaction() and db.log_item_sale()
# You will need functions to:
# 1. Create a new row in 'transactions' and return the new 'transaction_id'.
# 2. Create a new row in 'transaction_items' for each item in the sale.
# 3. A function to get 'quantity_on_hand' for a product (for SCRUM-38 check).
#    (You can reuse Séan's SCRUM-29 function for this).