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
# todo (séan): implement scrum-28: db.adjust_stock(product_id, quantity)
# function takes product_id and new_quantity
# executes sql update: "update booze set quantity_on_hand = ? where id = ?"

# todo (séan): implement scrum-29: db.get_stock_by_id(product_id)
# function takes product_id
# executes sql: "select name, quantity_on_hand from booze where id = ?"
# used by scrum-9 (get current stock) and scrum-11 (display stock)

# sales transaction functions (scrum-12)
# todo (sara): implement scrum-36: db.start_transaction() and db.log_item_sale()
# need functions to:
# 1. create new row in 'transactions' and return transaction_id
# 2. create new row in 'transaction_items' for each item
# 3. function to get 'quantity_on_hand' for product (scrum-38 check)
#    (can reuse séan's scrum-29 function)