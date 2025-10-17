import sqlite3
import os

# Define the path for the SQLite database
DATABASE_FILE = "inventory.db"

def connect():
    """Create a connection to the SQLite database."""
    try:     
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
        print(f"[STATUS] Database connection established to {DATABASE_FILE}")
        return conn
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to connect to database: {e}")
        return None
    
def close_connection(conn):
    """Close the database connection."""
    if conn:
        conn.close()
        print("[STATUS] Database connection closed.")

def execute_query(conn, query, params=()):
    """Execute a single query with optional parameters."""
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        print("[STATUS] Query executed successfully.")
        return cursor
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to execute query: {e}")
        return None

    