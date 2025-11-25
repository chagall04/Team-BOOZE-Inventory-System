# src/database_manager.py
"""Database manager module for Team-BOOZE Inventory System.

This module provides database operations for users, products, and sales transactions.
"""
import sqlite3
from datetime import datetime
import bcrypt

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


def create_user(username, password, role):
    """
    scrum-17: create new user in database
    returns (success, result_id_or_error)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role)
        )
        conn.commit()
        return True, cursor.lastrowid
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        conn.close()


def delete_user(username):
    """
    scrum-17: delete user from database
    returns (success, message)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        if cursor.rowcount == 0:
            return False, "User not found"
        return True, "User deleted"
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        conn.close()

# product management functions (scrum-5)
def insert_product(data):
    """Insert a new product into the database (SCRUM-24)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO booze (name, brand, type, abv, volume_ml, origin_country, price, quantity_on_hand, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['brand'],
            data['type'],
            data.get('abv', None),  # Optional fields with defaults
            data.get('volume_ml', None),
            data.get('origin_country', None),
            data['price'],
            data['quantity'],
            data.get('description', None)
        ))
        conn.commit()
        return True, cursor.lastrowid
    except sqlite3.IntegrityError:
        return False, "Product name already exists"
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        conn.close()

# inventory tracking functions (scrum-9 & scrum-11)
def adjust_stock(product_id, new_quantity):
    """
    scrum-28: update stock quantity for a product
    returns True on success, False on failure
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE booze SET quantity_on_hand = ? WHERE id = ?",
                      (new_quantity, product_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        return False
    finally:
        conn.close()


def get_stock_by_id(product_id):
    """
    scrum-29: get product name and stock quantity by id
    returns dict with 'name' and 'quantity' or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, quantity_on_hand FROM booze WHERE id = ?",
                  (product_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return {"name": result["name"], "quantity": result["quantity_on_hand"]}
    return None


# sales transaction functions (scrum-12)
def get_product_details(product_id):
    """
    scrum-38: get full product details for sale validation
    returns dict with product info or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, price, quantity_on_hand FROM booze WHERE id = ?",
        (product_id,)
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "id": result["id"],
            "name": result["name"],
            "price": result["price"],
            "quantity_on_hand": result["quantity_on_hand"]
        }
    return None


def start_transaction(total_amount):
    """
    scrum-36: create new transaction record
    returns transaction_id on success, None on failure
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO transactions (timestamp, total_amount) VALUES (?, ?)",
            (timestamp, total_amount)
        )
        conn.commit()
        transaction_id = cursor.lastrowid
        return transaction_id
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def log_item_sale(transaction_id, product_id, quantity, price_at_sale):
    """
    scrum-36: create transaction_items record
    returns True on success, False on failure
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO transaction_items
               (transaction_id, product_id, quantity, price_at_sale)
               VALUES (?, ?, ?, ?)""",
            (transaction_id, product_id, quantity, price_at_sale)
        )
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

# low stock reporting functions (scrum-14, scrum-56)
def get_low_stock_report(threshold):
    """
    scrum-56: query database for all products with stock below threshold
    
    args:
        threshold: stock level threshold (e.g., 20 units)
    
    returns:
        list of dicts with product info, sorted by quantity ascending
        each dict contains: id, name, brand, quantity_on_hand, price
        returns empty list if no products below threshold
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT id, name, brand, quantity_on_hand, price 
               FROM booze 
               WHERE quantity_on_hand < ? 
               ORDER BY quantity_on_hand ASC""",
            (threshold,)
        )
        results = cursor.fetchall()
        
        # convert Row objects to dictionaries
        low_stock_products = []
        for row in results:
            low_stock_products.append({
                "id": row["id"],
                "name": row["name"],
                "brand": row["brand"],
                "quantity_on_hand": row["quantity_on_hand"],
                "price": row["price"]
            })
        
        return low_stock_products
    except sqlite3.Error:
        return []
    finally:
        conn.close()

def get_all_products():
    """
    scrum-45: retrieve all products from inventory
    
    returns:
        list of dicts with complete product info
        each dict contains: id, name, brand, type, abv, volume_ml, 
                           origin_country, price, quantity_on_hand, description
        returns empty list on error
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT id, name, brand, type, abv, volume_ml, origin_country, 
                      price, quantity_on_hand, description 
               FROM booze 
               ORDER BY name ASC"""
        )
        results = cursor.fetchall()

        # convert Row objects to dictionaries
        products = []
        for row in results:
            products.append({
                "id": row["id"],
                "name": row["name"],
                "brand": row["brand"],
                "type": row["type"],
                "abv": row["abv"],
                "volume_ml": row["volume_ml"],
                "origin_country": row["origin_country"],
                "price": row["price"],
                "quantity_on_hand": row["quantity_on_hand"],
                "description": row["description"]
            })

        return products
    except sqlite3.Error:
        return []
    finally:
        conn.close()


# transaction detail functions (scrum-60)
def get_transaction_by_id(transaction_id):
    """
    scrum-61: retrieve transaction details by ID
    
    args:
        transaction_id: unique transaction ID
    
    returns:
        dict with 'id', 'timestamp', 'total_amount' or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT transaction_id, timestamp, total_amount FROM transactions WHERE transaction_id = ?",
            (transaction_id,)
        )
        result = cursor.fetchone()
        
        if result:
            return {
                "id": result["transaction_id"],
                "timestamp": result["timestamp"],
                "total_amount": result["total_amount"]
            }
        return None
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def get_items_for_transaction(transaction_id):
    """
    scrum-62: retrieve all items for a transaction with product details
    
    joins transaction_items with booze table to get product name, quantity,
    and price-at-sale for all items linked to the transaction
    
    args:
        transaction_id: unique transaction ID
    
    returns:
        list of dicts with 'name', 'quantity', 'price_at_sale'
        returns empty list if no items found or on error
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT b.name, ti.quantity, ti.price_at_sale
               FROM transaction_items ti
               JOIN booze b ON ti.product_id = b.id
               WHERE ti.transaction_id = ?
               ORDER BY ti.item_id""",
            (transaction_id,)
        )
        results = cursor.fetchall()
        
        # convert Row objects to dictionaries
        items = []
        for row in results:
            items.append({
                "name": row["name"],
                "quantity": row["quantity"],
                "price_at_sale": row["price_at_sale"]
            })
        
        return items
    except sqlite3.Error:
        return []
    finally:
        conn.close()


def process_sale_transaction(cart_items, total_amount):
    """
    scrum-12: atomic sale transaction with rollback support
    processes entire sale as single transaction - creates transaction record,
    logs all items, and updates stock atomically
    
    args:
        cart_items: list of dicts with 'product_id', 'quantity', 'price'
        total_amount: total sale amount
    
    returns:
        (success: bool, transaction_id or error_message: str)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # start database transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # create transaction record
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO transactions (timestamp, total_amount) VALUES (?, ?)",
            (timestamp, total_amount)
        )
        transaction_id = cursor.lastrowid
        
        # process each item in the cart
        for item in cart_items:
            # log the item sale
            cursor.execute(
                """INSERT INTO transaction_items
                   (transaction_id, product_id, quantity, price_at_sale)
                   VALUES (?, ?, ?, ?)""",
                (transaction_id, item['product_id'], item['quantity'], item['price'])
            )
            
            # get current stock (re-fetch to avoid stale data)
            cursor.execute(
                "SELECT quantity_on_hand FROM booze WHERE id = ?",
                (item['product_id'],)
            )
            stock_result = cursor.fetchone()
            if stock_result is None:
                raise sqlite3.Error(f"Product {item['product_id']} not found")
            
            current_stock = stock_result['quantity_on_hand']
            new_stock = current_stock - item['quantity']
            
            # validate that stock won't go negative (race condition protection)
            if new_stock < 0:
                raise sqlite3.Error(
                    f"Insufficient stock for product {item['product_id']}: "
                    f"available {current_stock}, requested {item['quantity']}"
                )
            
            # update stock
            cursor.execute(
                "UPDATE booze SET quantity_on_hand = ? WHERE id = ?",
                (new_stock, item['product_id'])
            )
        
        # commit all changes atomically
        conn.commit()
        return True, transaction_id
        
    except sqlite3.Error as e:
        # rollback all changes if anything failed
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def update_product_details(product_id, data):
    """Update existing product details in the database
    
    Args:
        product_id (int): ID of the product to update
        data (dict): Dictionary containing fields to update. Valid keys are:
            - name (str)
            - brand (str)
            - type (str)
            - abv (float)
            - volume_ml (int)
            - origin_country (str)
            - price (float)
            - quantity_on_hand (int)
            - description (str)
            
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build update query dynamically based on provided fields
    valid_fields = [
        'name', 'brand', 'type', 'abv', 'volume_ml',
        'origin_country', 'price', 'quantity_on_hand', 'description'
    ]
    
    # Filter out invalid fields, but keep None values to allow clearing optional fields
    update_data = {k: v for k, v in data.items() if k in valid_fields}
    
    if not update_data:
        conn.close()
        return False, "No valid fields to update"
    
    try:
        # Construct UPDATE query
        set_clause = ", ".join(f"{field} = ?" for field in update_data.keys())
        query = f"UPDATE booze SET {set_clause} WHERE id = ?"
        
        # Execute query with values
        values = list(update_data.values()) + [product_id]
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            return False, "Product not found"
            
        conn.commit()
        return True, "Product updated successfully"
        
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()


def update_product(product_id, data):
    """Alias for update_product_details for backward compatibility"""
    return update_product_details(product_id, data)


def get_total_inventory_value():
    """
    calculate total inventory value by multiplying price by stock for all products
    
    returns:
        float: total value of all products in stock (price * quantity_on_hand)
               returns 0.00 if database is empty or result is NULL
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT SUM(price * quantity_on_hand) FROM booze")
        result = cursor.fetchone()
        
        # handle NULL result (empty database or all products have NULL price/quantity)
        if result is None or result[0] is None:
            return 0.00
        
        return float(result[0])
    except sqlite3.Error:
        return 0.00
    finally:
        conn.close()


def search_products_by_term(search_term):
    """Search products by name or brand"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, brand, quantity_on_hand, price
            FROM booze
            WHERE name LIKE ? OR brand LIKE ?
            ORDER BY name
        """, (f"%{search_term}%", f"%{search_term}%"))
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except sqlite3.Error:
        return []
    finally:
        conn.close()
