# src/database_manager.py
import sqlite3
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
        return False, "username already exists"
    except Exception as e:
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
            return False, "user not found"
        return True, "user deleted"
    except Exception as e:
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
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

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