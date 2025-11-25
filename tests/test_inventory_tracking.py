"""
SCRUM-31: Unit tests for inventory tracking functionality
Tests the receive_new_stock function and its dependent database functions
"""

import os
import sqlite3
from unittest.mock import patch
import pytest
from src.database_manager import get_stock_by_id, adjust_stock, search_products_by_term
from src.inventory_tracking import receive_new_stock, view_current_stock, log_product_loss, search_products

# ---------------- SCRUM-31: Inventory Tracking Tests ----------------

@pytest.fixture(autouse=True)
def setup_test_db():
    """Create a test database with sample data"""
    test_db = "test_inventory.db"
    
    # Back up and patch the DB_NAME
    import src.database_manager
    original_db = src.database_manager.DB_NAME
    src.database_manager.DB_NAME = test_db
    
    # Clean up before creating (add this)
    if os.path.exists(test_db):
        os.remove(test_db)
    
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
    assert updated is not None
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
    assert updated is not None
    assert updated['quantity'] == 60  # 50 + 10

@patch('builtins.input', side_effect=['abc', '10'])
def test_receive_new_stock_invalid_id(mock_input):
    """SCRUM-30: Test handling invalid product ID input"""
    from src.inventory_tracking import receive_new_stock
    
    result = receive_new_stock()
    assert result is False

@patch('builtins.input', side_effect=['999', '10'])
@patch('src.database_manager.get_stock_by_id')
def test_receive_new_stock_nonexistent_product(mock_get_stock, mock_input):
    """SCRUM-30: Test handling nonexistent product"""
    from src.inventory_tracking import receive_new_stock
    
    # Force get_stock_by_id to return None to simulate product not found
    mock_get_stock.return_value = None
    
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
    assert current is not None
    assert current['quantity'] == 50

@patch('builtins.input', side_effect=['1', '10'])
@patch('src.inventory_tracking.adjust_stock')
@patch('src.inventory_tracking.get_stock_by_id')
def test_receive_new_stock_update_failure(mock_get_stock, mock_adjust_stock, mock_input):
    """SCRUM-30: Test handling database update failure"""
    from src.inventory_tracking import receive_new_stock
    
    # Mock get_stock_by_id to return test data
    mock_get_stock.return_value = {'id': 1, 'name': 'Test Product', 'quantity': 50}
    
    # Set up adjust_stock to return False
    mock_adjust_stock.return_value = False
    
    result = receive_new_stock()
    assert result is False, "Function should return False when adjust_stock fails"
    mock_adjust_stock.assert_called_once_with(1, 60)  # 50 + 10

@patch('builtins.input', side_effect=['1'])
def test_view_current_stock_success(mock_input, capsys):
    """SCRUM-11 & SCRUM-32: Test successful stock viewing"""
    from src.inventory_tracking import view_current_stock
    
    result = view_current_stock()
    assert result is True
    
    # Check the output format
    captured = capsys.readouterr()
    assert "Product Name: Test Product" in captured.out
    assert "Current Stock: 50 units" in captured.out

@patch('builtins.input', side_effect=['abc'])
def test_view_current_stock_invalid_id(mock_input, capsys):
    """SCRUM-32: Test handling invalid product ID input"""
    from src.inventory_tracking import view_current_stock
    
    result = view_current_stock()
    assert result is False
    
    captured = capsys.readouterr()
    assert "Error: Product ID must be a number" in captured.out

@patch('builtins.input', side_effect=['999'])
@patch('src.database_manager.get_stock_by_id')
def test_view_current_stock_product_not_found(mock_get_stock, mock_input, capsys):
    """SCRUM-32: Test handling nonexistent product"""
    from src.inventory_tracking import view_current_stock
    
    # Force get_stock_by_id to return None to simulate product not found
    mock_get_stock.return_value = None
    
    result = view_current_stock()
    assert result is False

    captured = capsys.readouterr()
    assert "Error: Product with ID 999 not found" in captured.out or "Error: Product ID 999 not found" in captured.out

@patch('builtins.input', side_effect=['1', '20'])
def test_log_product_loss_success(mock_input):
    """SCRUM-51 & SCRUM-48: Test successful product loss logging"""
    from src.inventory_tracking import log_product_loss
    
    result = log_product_loss()
    assert result is True
    
    # Verify final stock level decreased correctly
    updated = get_stock_by_id(1)
    assert updated is not None
    assert updated['quantity'] == 30  # 50 - 20

@patch('builtins.input', side_effect=['abc', '20'])
def test_log_product_loss_invalid_id(mock_input):
    """SCRUM-48: Test handling invalid product ID input"""
    from src.inventory_tracking import log_product_loss
    
    result = log_product_loss()
    assert result is False

@patch('builtins.input', side_effect=['1', '-5'])
def test_log_product_loss_negative_quantity(mock_input):
    """SCRUM-48: Test handling negative quantity input"""
    from src.inventory_tracking import log_product_loss
    
    result = log_product_loss()
    assert result is False
    
    # Verify stock wasn't changed
    current = get_stock_by_id(1)
    assert current is not None
    assert current['quantity'] == 50

@patch('builtins.input', side_effect=['1', 'abc'])
def test_log_product_loss_invalid_quantity_value_error(mock_input):
    """SCRUM-48: Test handling non-numeric quantity input"""
    from src.inventory_tracking import log_product_loss
    
    result = log_product_loss()
    assert result is False
    
    # Verify stock wasn't changed
    current = get_stock_by_id(1)
    assert current is not None
    assert current['quantity'] == 50

@patch('builtins.input', side_effect=['1', '0'])
def test_log_product_loss_zero_quantity(mock_input):
    """SCRUM-48: Test handling zero quantity input"""
    from src.inventory_tracking import log_product_loss
    
    result = log_product_loss()
    assert result is False
    
    # Verify stock wasn't changed
    current = get_stock_by_id(1)
    assert current is not None
    assert current['quantity'] == 50

@patch('builtins.input', side_effect=['999', '10'])
@patch('src.database_manager.get_stock_by_id')
def test_log_product_loss_nonexistent_product(mock_get_stock, mock_input):
    """SCRUM-48: Test handling nonexistent product"""
    from src.inventory_tracking import log_product_loss

    # Force get_stock_by_id to return None to simulate product not found
    mock_get_stock.return_value = None

    result = log_product_loss()
    assert result is False

@patch('builtins.input', side_effect=['1', '100'])
def test_log_product_loss_quantity_exceeds_stock(mock_input):
    """SCRUM-48 & SCRUM-50: Test handling loss quantity greater than current stock"""
    from src.inventory_tracking import log_product_loss

    result = log_product_loss()
    assert result is False

    # Verify stock wasn't changed
    current = get_stock_by_id(1)
    assert current is not None
    assert current['quantity'] == 50

@patch('builtins.input', side_effect=['1', '20'])
@patch('src.inventory_tracking.adjust_stock')
@patch('src.inventory_tracking.get_stock_by_id')
def test_log_product_loss_update_failure(mock_get_stock, mock_adjust_stock, mock_input):
    """SCRUM-48 & SCRUM-50: Test handling database update failure"""
    from src.inventory_tracking import log_product_loss

    # Mock get_stock_by_id to return test data
    mock_get_stock.return_value = {'id': 1, 'name': 'Test Product', 'quantity': 50}

    # Set up adjust_stock to return False
    mock_adjust_stock.return_value = False

    result = log_product_loss()
    assert result is False, "Function should return False when adjust_stock fails"
    mock_adjust_stock.assert_called_once_with(1, 30)  # 50 - 20

@patch('builtins.input', side_effect=['1', '15'])
def test_log_product_loss_partial_deduction(mock_input):
    """SCRUM-51 & SCRUM-50: Test partial stock deduction"""
    from src.inventory_tracking import log_product_loss

    result = log_product_loss()
    assert result is True

    # Verify stock decreased by exactly 15 units
    updated = get_stock_by_id(1)
    assert updated is not None
    assert updated['quantity'] == 35  # 50 - 15

@patch('builtins.input', side_effect=['1', '50'])
def test_log_product_loss_entire_stock(mock_input):
    """SCRUM-51 & SCRUM-50: Test logging loss of entire stock"""
    from src.inventory_tracking import log_product_loss

    result = log_product_loss()
    assert result is True
    
    # Verify stock is now 0
    updated = get_stock_by_id(1)
    assert updated is not None
    assert updated['quantity'] == 0

# ---------------- SCRUM-70: Product Search Tests ----------------

@patch('builtins.input', return_value='vodka')
@patch('src.inventory_tracking.search_products_by_term')
@patch('builtins.print')
def test_product_search_returns_results(mock_print, mock_search, mock_input):
    """Test that search returns results and prints them."""
    mock_search.return_value = [
        {'id': 1, 'name': 'Vodka', 'price': 12.99, 'quantity_on_hand': 20, 'brand': 'Smirnoff'},
        {'id': 2, 'name': 'Vanilla Vodka', 'price': 14.49, 'quantity_on_hand': 8, 'brand': 'Absolut'},
    ]

    result = search_products()

    mock_search.assert_called_once_with('vodka')
    assert result is True
    
    # Verify output contains product names by checking call arguments
    all_prints = [str(call.args[0]) if call.args else "" for call in mock_print.call_args_list]
    printed_output = " ".join(all_prints)
    assert "Vodka" in printed_output
    assert "Vanilla Vodka" in printed_output


@patch('builtins.input', return_value='unknown')
@patch('src.inventory_tracking.search_products_by_term', return_value=[])
@patch('builtins.print')
def test_product_search_no_results(mock_print, mock_search, mock_input):
    """Test search with no matching products."""
    result = search_products()

    mock_search.assert_called_once_with('unknown')
    assert result is True
    
    # Verify "No products found" message by checking call arguments
    all_prints = [str(call.args[0]) if call.args else "" for call in mock_print.call_args_list]
    printed_output = " ".join(all_prints)
    assert "No products found" in printed_output

@patch('builtins.input', return_value='')
@patch('builtins.print')
def test_product_search_empty_term(mock_print, mock_input):
    """Test search with empty search term."""
    result = search_products()
    
    assert result is False
    
    all_prints = [str(call.args[0]) if call.args else "" for call in mock_print.call_args_list]
    printed_output = " ".join(all_prints)
    assert "Search term cannot be empty" in printed_output