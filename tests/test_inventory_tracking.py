"""
SCRUM-31: Unit tests for inventory tracking functionality
Tests the receive_new_stock function and its dependent database functions
"""

import pytest
from unittest.mock import patch
import sqlite3
import os
from src.database_manager import get_stock_by_id, adjust_stock, DB_NAME

@pytest.fixture(autouse=True)
def setup_test_db():
    """Create a test database with sample data"""
    test_db = "test_inventory.db"
    
    # Back up and patch the DB_NAME
    import src.database_manager
    original_db = src.database_manager.DB_NAME
    src.database_manager.DB_NAME = test_db
    
    # Create test database with one product
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS booze (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity_on_hand INTEGER DEFAULT 0
    )
    """)
    
    cursor.execute("""
    INSERT INTO booze (id, name, quantity_on_hand) 
    VALUES (1, 'Test Product', 50)
    """)
    
    conn.commit()
    conn.close()
    
    # Provide the test context
    yield
    
    # Cleanup after test
    src.database_manager.DB_NAME = original_db
    if os.path.exists(test_db):
        os.remove(test_db)

def test_get_stock_by_id_existing_product():
    """SCRUM-29: Test retrieving stock for an existing product"""
    result = get_stock_by_id(1)
    assert result is not None
    assert result['name'] == 'Test Product'
    assert result['quantity'] == 50

def test_get_stock_by_id_nonexistent_product():
    """SCRUM-29: Test retrieving stock for a nonexistent product"""
    result = get_stock_by_id(999)
    assert result is None

def test_adjust_stock_valid_update():
    """SCRUM-28: Test updating stock for an existing product"""
    result = adjust_stock(1, 60)
    assert result is True
    
    # Verify the update
    updated = get_stock_by_id(1)
    assert updated['quantity'] == 60

def test_adjust_stock_invalid_product():
    """SCRUM-28: Test updating stock for a nonexistent product"""
    result = adjust_stock(999, 60)
    assert result is False

@patch('builtins.input', side_effect=['1', '10'])
def test_receive_new_stock_success(mock_input):
    """SCRUM-9 & SCRUM-30: Test successful stock receipt flow"""
    from src.inventory_tracking import receive_new_stock
    
    result = receive_new_stock()
    assert result is True
    
    # Verify final stock level
    updated = get_stock_by_id(1)
    assert updated['quantity'] == 60  # 50 + 10

@patch('builtins.input', side_effect=['abc', '10'])
def test_receive_new_stock_invalid_id(mock_input):
    """SCRUM-30: Test handling invalid product ID input"""
    from src.inventory_tracking import receive_new_stock
    
    result = receive_new_stock()
    assert result is False

@patch('builtins.input', side_effect=['1', '-5'])
def test_receive_new_stock_negative_quantity(mock_input):
    """SCRUM-30: Test handling negative quantity input"""
    from src.inventory_tracking import receive_new_stock
    
    result = receive_new_stock()
    assert result is False
    
    # Verify stock wasn't changed
    current = get_stock_by_id(1)
    assert current['quantity'] == 50