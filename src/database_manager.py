# src/database_manager.py
import sqlite3

DB_NAME = "inventory.db"

def get_db_connection():
    """connect to database"""
    conn = sqlite3.connect(DB_NAME)
    # return rows as dictionaries
    conn.row_factory = sqlite3.Row
    return conn

# auth functions (scrum-17)
def get_user_by_username(username):
    """
    get user hash and role
    part of scrum-18
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return {"hash": user_data["password_hash"], "role": user_data["role"]}
    return None

# product management functions (scrum-5)
# todo (lucy): implement scrum-24: db.insert_product(data)
# function takes product data and executes sql insert

# inventory tracking functions (scrum-9 & scrum-11)
def adjust_stock(product_id, new_quantity):
    """
    SCRUM-28: Update the stock level for a product
    Args:
        product_id (int): The ID of the product to update
        new_quantity (int): The new stock level to set
    Returns:
        bool: True if update successful, False if product not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE booze SET quantity_on_hand = ? WHERE id = ?", 
                  (new_quantity, product_id))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def get_stock_by_id(product_id):
    """
    SCRUM-29: Get the current stock level and name for a product
    Args:
        product_id (int): The ID of the product to look up
    Returns:
        dict: Product details with 'name' and 'quantity' keys, or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, quantity_on_hand FROM booze WHERE id = ?", 
                  (product_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'name': result['name'],
            'quantity': result['quantity_on_hand']
        }
    return None

# sales transaction functions (scrum-12)
# todo (sara): implement scrum-36: db.start_transaction() and db.log_item_sale()
# need functions to:
# 1. create new row in 'transactions' and return transaction_id
# 2. create new row in 'transaction_items' for each item
# 3. function to get 'quantity_on_hand' for product (scrum-38 check)
#    (can reuse séan's scrum-29 function)