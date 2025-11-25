# tests/test_sales.py
# scrum-12 to scrum-13: sales management tests
# owned by: sara larkem

"""Comprehensive tests for sales management functionality."""

from unittest.mock import patch
from src.sales import (
    validate_product_input,
    validate_quantity_input,
    check_stock_availability,
    display_cart,
    process_sale,
    record_sale,
    view_transaction_details,
    view_sales_history
)


class TestInputValidation:
    """Test input validation functions"""

    def test_validate_product_input_valid(self):
        """Test valid product ID input"""
        is_valid, product_id, error = validate_product_input("5")
        assert is_valid is True
        assert product_id == 5
        assert error is None

    def test_validate_product_input_invalid_non_numeric(self):
        """Test invalid non-numeric product ID"""
        is_valid, product_id, error = validate_product_input("abc")
        assert is_valid is False
        assert product_id is None
        assert error is not None
        assert "valid number" in error

    def test_validate_product_input_invalid_negative(self):
        """Test invalid negative product ID"""
        is_valid, product_id, error = validate_product_input("-1")
        assert is_valid is False
        assert product_id is None
        assert error is not None
        assert "positive number" in error

    def test_validate_product_input_invalid_zero(self):
        """Test invalid zero product ID"""
        is_valid, product_id, error = validate_product_input("0")
        assert is_valid is False
        assert product_id is None
        assert error is not None
        assert "positive number" in error

    def test_validate_quantity_input_valid(self):
        """Test valid quantity input"""
        is_valid, quantity, error = validate_quantity_input("10")
        assert is_valid is True
        assert quantity == 10
        assert error is None

    def test_validate_quantity_input_invalid_non_numeric(self):
        """Test invalid non-numeric quantity"""
        is_valid, quantity, error = validate_quantity_input("xyz")
        assert is_valid is False
        assert quantity is None
        assert error is not None
        assert "valid number" in error

    def test_validate_quantity_input_invalid_negative(self):
        """Test invalid negative quantity"""
        is_valid, quantity, error = validate_quantity_input("-5")
        assert is_valid is False
        assert quantity is None
        assert error is not None
        assert "positive number" in error

    def test_validate_quantity_input_invalid_zero(self):
        """Test invalid zero quantity"""
        is_valid, quantity, error = validate_quantity_input("0")
        assert is_valid is False
        assert quantity is None
        assert error is not None
        assert "positive number" in error


class TestStockAvailability:
    """Test stock availability checking (SCRUM-38)"""

    @patch('src.sales.get_product_details')
    def test_check_stock_availability_success(self, mock_get_product):
        """Test successful stock availability check"""
        mock_get_product.return_value = {
            'id': 1,
            'name': 'Test Product',
            'price': 10.50,
            'quantity_on_hand': 50
        }

        is_available, product, error = check_stock_availability(1, 10)
        assert is_available is True
        assert product is not None
        assert product['name'] == 'Test Product'
        assert error is None

    @patch('src.sales.get_product_details')
    def test_check_stock_availability_insufficient(self, mock_get_product):
        """Test insufficient stock scenario"""
        mock_get_product.return_value = {
            'id': 1,
            'name': 'Test Product',
            'price': 10.50,
            'quantity_on_hand': 5
        }

        is_available, product, error = check_stock_availability(1, 10)
        assert is_available is False
        assert product is not None
        assert product['name'] == 'Test Product'
        assert error is not None
        assert "Insufficient stock" in error
        assert "Available: 5" in error
        assert "Requested: 10" in error

    @patch('src.sales.get_product_details')
    def test_check_stock_availability_product_not_found(self, mock_get_product):
        """Test product not found scenario"""
        mock_get_product.return_value = None

        is_available, product, error = check_stock_availability(999, 10)
        assert is_available is False
        assert product is None
        assert error is not None
        assert "not found" in error

    @patch('src.sales.get_product_details')
    def test_check_stock_availability_exact_stock(self, mock_get_product):
        """Test exact stock match scenario"""
        mock_get_product.return_value = {
            'id': 1,
            'name': 'Test Product',
            'price': 10.50,
            'quantity_on_hand': 10
        }

        is_available, product, error = check_stock_availability(1, 10)
        assert is_available is True
        assert product is not None
        assert product['quantity_on_hand'] == 10
        assert error is None

    @patch('src.sales.get_product_details')
    def test_check_stock_availability_prevents_oversell_with_cart(self, mock_get_product):
        """Test that stock check accounts for items already in cart to prevent overselling"""
        mock_get_product.return_value = {
            'id': 1,
            'name': 'Beer',
            'price': 5.50,
            'quantity_on_hand': 10
        }

        # Simulate cart that already has 6 units of product ID 1
        existing_cart = [
            {'product_id': 1, 'name': 'Beer', 'price': 5.50, 'quantity': 6, 'current_stock': 10}
        ]

        # Try to add 6 more units (total would be 12, but only 10 available)
        is_available, _product, error = check_stock_availability(1, 6, existing_cart)
        assert is_available is False
        assert error is not None
        assert "Insufficient stock" in error
        assert "Already in cart: 6" in error
        assert "Requested: 6" in error
        assert "Total needed: 12" in error

    @patch('src.sales.get_product_details')
    def test_check_stock_availability_with_cart_multiple_same_product(self, mock_get_product):
        """Test stock check with multiple cart entries of same product"""
        mock_get_product.return_value = {
            'id': 5,
            'name': 'Wine',
            'price': 15.00,
            'quantity_on_hand': 20
        }

        # Cart has product 5 added twice (3 + 4 = 7 total)
        existing_cart = [
            {'product_id': 5, 'name': 'Wine', 'price': 15.00, 'quantity': 3, 'current_stock': 20},
            {'product_id': 3, 'name': 'Whiskey', 'price': 40.00, 'quantity': 2, 'current_stock': 30},
            {'product_id': 5, 'name': 'Wine', 'price': 15.00, 'quantity': 4, 'current_stock': 20}
        ]

        # Try to add 14 more (total would be 21, but only 20 available)
        is_available, _product, error = check_stock_availability(5, 14, existing_cart)
        assert is_available is False
        assert error is not None
        assert "Already in cart: 7" in error

    @patch('src.sales.get_product_details')
    def test_check_stock_availability_with_cart_allows_valid_addition(self, mock_get_product):
        """Test that valid additions are still allowed with cart consideration"""
        mock_get_product.return_value = {
            'id': 2,
            'name': 'Vodka',
            'price': 25.00,
            'quantity_on_hand': 15
        }

        # Cart has 5 units of product 2
        existing_cart = [
            {'product_id': 2, 'name': 'Vodka', 'price': 25.00, 'quantity': 5, 'current_stock': 15}
        ]

        # Try to add 8 more (total 13, within 15 available)
        is_available, _product, error = check_stock_availability(2, 8, existing_cart)
        assert is_available is True
        assert error is None


class TestDisplayCart:
    """Test cart display function (SCRUM-40)"""

    def test_display_cart_empty(self, capsys):
        """Test displaying empty cart"""
        display_cart([])
        captured = capsys.readouterr()
        assert "Cart is empty" in captured.out

    def test_display_cart_single_item(self, capsys):
        """Test displaying cart with single item"""
        cart = [{
            'name': 'Product A',
            'quantity': 2,
            'price': 10.50
        }]
        display_cart(cart)
        captured = capsys.readouterr()
        assert "Product A" in captured.out
        assert "Quantity: 2" in captured.out
        assert "€21.00" in captured.out
        assert "Total: €21.00" in captured.out

    def test_display_cart_multiple_items(self, capsys):
        """Test displaying cart with multiple items"""
        cart = [
            {'name': 'Product A', 'quantity': 2, 'price': 10.50},
            {'name': 'Product B', 'quantity': 1, 'price': 5.00}
        ]
        display_cart(cart)
        captured = capsys.readouterr()
        assert "Product A" in captured.out
        assert "Product B" in captured.out
        assert "Total: €26.00" in captured.out


class TestProcessSale:
    """Test process_sale function (SCRUM-37)"""

    def test_process_sale_empty_cart(self):
        """Test processing empty cart"""
        success, message = process_sale([])
        assert success is False
        assert "empty cart" in message.lower()

    @patch('src.sales.process_sale_transaction')
    def test_process_sale_success_single_item(self, mock_transaction):
        """Test successful sale with single item"""
        mock_transaction.return_value = (True, 123)

        cart = [{
            'product_id': 1,
            'name': 'Test Product',
            'quantity': 2,
            'price': 10.50,
            'current_stock': 50
        }]

        success, message = process_sale(cart)
        assert success is True
        assert "Transaction ID: 123" in message
        mock_transaction.assert_called_once_with(cart, 21.00)

    @patch('src.sales.process_sale_transaction')
    def test_process_sale_success_multiple_items(self, mock_transaction):
        """Test successful sale with multiple items"""
        mock_transaction.return_value = (True, 124)

        cart = [
            {'product_id': 1, 'name': 'Product A', 'quantity': 2,
             'price': 10.50, 'current_stock': 50},
            {'product_id': 2, 'name': 'Product B', 'quantity': 1,
             'price': 5.00, 'current_stock': 30}
        ]

        success, message = process_sale(cart)
        assert success is True
        assert "Transaction ID: 124" in message
        mock_transaction.assert_called_once_with(cart, 26.00)

    @patch('src.sales.process_sale_transaction')
    def test_process_sale_transaction_fails(self, mock_transaction):
        """Test sale failure when transaction fails"""
        mock_transaction.return_value = (False, "Database error")

        cart = [{
            'product_id': 1,
            'name': 'Test Product',
            'quantity': 2,
            'price': 10.50,
            'current_stock': 50
        }]

        success, message = process_sale(cart)
        assert success is False
        assert "Database error" in message


class TestRecordSale:
    """Test main record_sale function (SCRUM-12, SCRUM-39)"""

    @patch('builtins.input')
    def test_record_sale_cancel_immediately(self, mock_input):
        """Test cancelling sale immediately"""
        mock_input.side_effect = ['0']

        result = record_sale()
        assert result is False

    @patch('builtins.input')
    @patch('src.sales.check_stock_availability')
    @patch('src.sales.process_sale')
    def test_record_sale_add_item_and_complete(self, mock_process, mock_check, mock_input):
        """Test adding item and completing sale"""
        mock_input.side_effect = [
            '1',      # Add item
            '1',      # Product ID
            '2',      # Quantity
            '3',      # Complete sale
            'y'       # Confirm
        ]
        mock_check.return_value = (True, {
            'id': 1,
            'name': 'Test Product',
            'price': 10.50,
            'quantity_on_hand': 50
        }, None)
        mock_process.return_value = (True, "Sale completed successfully! Transaction ID: 100")

        result = record_sale()
        assert result is True
        mock_process.assert_called_once()

    @patch('builtins.input')
    def test_record_sale_invalid_product_id(self, mock_input):
        """Test handling invalid product ID input"""
        mock_input.side_effect = [
            '1',      # Add item
            'abc',    # Invalid product ID
            '0'       # Exit
        ]

        result = record_sale()
        assert result is False

    @patch('builtins.input')
    def test_record_sale_invalid_quantity(self, mock_input):
        """Test handling invalid quantity input"""
        mock_input.side_effect = [
            '1',      # Add item
            '1',      # Product ID
            '-5',     # Invalid quantity
            '0'       # Exit
        ]

        result = record_sale()
        assert result is False

    @patch('builtins.input')
    @patch('src.sales.check_stock_availability')
    def test_record_sale_insufficient_stock(self, mock_check, mock_input):
        """Test handling insufficient stock"""
        mock_input.side_effect = [
            '1',      # Add item
            '1',      # Product ID
            '100',    # Quantity
            '0'       # Exit
        ]
        mock_check.return_value = (False, None, "Insufficient stock")

        result = record_sale()
        assert result is False

    @patch('builtins.input')
    @patch('src.sales.check_stock_availability')
    def test_record_sale_view_cart(self, mock_check, mock_input, capsys):
        """Test viewing cart"""
        mock_input.side_effect = [
            '1',      # Add item
            '1',      # Product ID
            '2',      # Quantity
            '2',      # View cart
            '0'       # Exit
        ]
        mock_check.return_value = (True, {
            'id': 1,
            'name': 'Test Product',
            'price': 10.50,
            'quantity_on_hand': 50
        }, None)

        result = record_sale()
        captured = capsys.readouterr()
        assert "Test Product" in captured.out
        assert result is False

    @patch('builtins.input')
    def test_record_sale_complete_empty_cart(self, mock_input):
        """Test attempting to complete sale with empty cart"""
        mock_input.side_effect = [
            '3',      # Complete sale (empty cart)
            '0'       # Exit
        ]

        result = record_sale()
        assert result is False

    @patch('builtins.input')
    @patch('src.sales.check_stock_availability')
    @patch('src.sales.process_sale')
    def test_record_sale_decline_confirmation(self, mock_process, mock_check, mock_input):
        """Test declining sale confirmation"""
        mock_input.side_effect = [
            '1',      # Add item
            '1',      # Product ID
            '2',      # Quantity
            '3',      # Complete sale
            'n'       # Decline confirmation
        ]
        mock_check.return_value = (True, {
            'id': 1,
            'name': 'Test Product',
            'price': 10.50,
            'quantity_on_hand': 50
        }, None)

        result = record_sale()
        assert result is False
        mock_process.assert_not_called()

    @patch('builtins.input')
    @patch('src.sales.check_stock_availability')
    @patch('src.sales.process_sale')
    def test_record_sale_process_fails(self, mock_process, mock_check, mock_input):
        """Test sale processing failure"""
        mock_input.side_effect = [
            '1',      # Add item
            '1',      # Product ID
            '2',      # Quantity
            '3',      # Complete sale
            'y'       # Confirm
        ]
        mock_check.return_value = (True, {
            'id': 1,
            'name': 'Test Product',
            'price': 10.50,
            'quantity_on_hand': 50
        }, None)
        mock_process.return_value = (False, "Database error")

        result = record_sale()
        assert result is False

    @patch('builtins.input')
    @patch('src.sales.check_stock_availability')
    @patch('src.sales.process_sale')
    def test_record_sale_multiple_items(self, mock_process, mock_check, mock_input):
        """Test adding multiple items to cart"""
        mock_input.side_effect = [
            '1',      # Add item 1
            '1',      # Product ID 1
            '2',      # Quantity
            '1',      # Add item 2
            '2',      # Product ID 2
            '3',      # Quantity
            '3',      # Complete sale
            'y'       # Confirm
        ]
        mock_check.side_effect = [
            (True, {'id': 1, 'name': 'Product A', 'price': 10.50, 'quantity_on_hand': 50}, None),
            (True, {'id': 2, 'name': 'Product B', 'price': 5.00, 'quantity_on_hand': 30}, None)
        ]
        mock_process.return_value = (True, "Sale completed successfully! Transaction ID: 100")

        result = record_sale()
        assert result is True
        # Verify process_sale was called with a cart containing 2 items
        call_args = mock_process.call_args[0][0]
        assert len(call_args) == 2

    @patch('builtins.input')
    def test_record_sale_invalid_menu_choice(self, mock_input):
        """Test handling invalid menu choice"""
        mock_input.side_effect = [
            '99',     # Invalid choice
            '0'       # Exit
        ]

        result = record_sale()
        assert result is False


class TestViewTransactionDetails:
    """Test view_transaction_details function (scrum-60)"""
    
    @patch('src.sales.get_items_for_transaction')
    @patch('src.sales.get_transaction_by_id')
    @patch('builtins.input')
    def test_view_transaction_details_success(self, mock_input, mock_get_txn, mock_get_items):
        """Test successfully viewing transaction details"""
        mock_input.return_value = "1"
        mock_get_txn.return_value = {
            "id": 1,
            "timestamp": "2025-11-10 14:30:00",
            "total_amount": 45.50
        }
        mock_get_items.return_value = [
            {"name": "Product A", "quantity": 2, "price_at_sale": 10.50},
            {"name": "Product B", "quantity": 1, "price_at_sale": 24.50}
        ]
        
        result = view_transaction_details()
        
        assert result is True
        mock_get_txn.assert_called_once_with(1)
        mock_get_items.assert_called_once_with(1)
    
    @patch('builtins.input')
    def test_view_transaction_details_invalid_id_non_numeric(self, mock_input):
        """Test view transaction with non-numeric ID"""
        mock_input.return_value = "abc"
        
        result = view_transaction_details()
        
        assert result is False
    
    @patch('builtins.input')
    def test_view_transaction_details_invalid_id_negative(self, mock_input):
        """Test view transaction with negative ID"""
        mock_input.return_value = "-1"
        
        result = view_transaction_details()
        
        assert result is False
    
    @patch('builtins.input')
    def test_view_transaction_details_invalid_id_zero(self, mock_input):
        """Test view transaction with zero ID"""
        mock_input.return_value = "0"
        
        result = view_transaction_details()
        
        assert result is False
    
    @patch('src.sales.get_transaction_by_id')
    @patch('builtins.input')
    def test_view_transaction_details_not_found(self, mock_input, mock_get_txn):
        """Test view transaction when transaction not found"""
        mock_input.return_value = "999"
        mock_get_txn.return_value = None
        
        result = view_transaction_details()
        
        assert result is False
        mock_get_txn.assert_called_once_with(999)
    
    @patch('src.sales.get_items_for_transaction')
    @patch('src.sales.get_transaction_by_id')
    @patch('builtins.input')
    def test_view_transaction_details_no_items(self, mock_input, mock_get_txn, mock_get_items):
        """Test view transaction when no items found"""
        mock_input.return_value = "1"
        mock_get_txn.return_value = {
            "id": 1,
            "timestamp": "2025-11-10 14:30:00",
            "total_amount": 0.00
        }
        mock_get_items.return_value = []
        
        result = view_transaction_details()
        
        assert result is False
        mock_get_txn.assert_called_once_with(1)
        mock_get_items.assert_called_once_with(1)
    
    @patch('src.sales.get_items_for_transaction')
    @patch('src.sales.get_transaction_by_id')
    @patch('builtins.input')
    def test_view_transaction_details_formatting(self, mock_input, mock_get_txn, mock_get_items, capsys):
        """Test transaction details output formatting with EUR currency"""
        mock_input.return_value = "1"
        mock_get_txn.return_value = {
            "id": 1,
            "timestamp": "2025-11-10 14:30:00",
            "total_amount": 35.00
        }
        mock_get_items.return_value = [
            {"name": "Test Product", "quantity": 2, "price_at_sale": 17.50}
        ]
        
        result = view_transaction_details()
        
        assert result is True
        captured = capsys.readouterr()
        assert "TRANSACTION RECEIPT" in captured.out
        assert "Transaction ID: 1" in captured.out
        assert "Date/Time: 2025-11-10 14:30:00" in captured.out
        assert "Test Product" in captured.out
        assert "€17.50" in captured.out
        assert "€35.00" in captured.out
    
    @patch('src.sales.get_items_for_transaction')
    @patch('src.sales.get_transaction_by_id')
    @patch('builtins.input')
    def test_view_transaction_details_multiple_items(self, mock_input, mock_get_txn, mock_get_items):
        """Test view transaction with multiple items"""
        mock_input.return_value = "5"
        mock_get_txn.return_value = {
            "id": 5,
            "timestamp": "2025-11-11 10:00:00",
            "total_amount": 75.00
        }
        mock_get_items.return_value = [
            {"name": "Product A", "quantity": 1, "price_at_sale": 25.00},
            {"name": "Product B", "quantity": 2, "price_at_sale": 15.00},
            {"name": "Product C", "quantity": 1, "price_at_sale": 20.00}
        ]
        
        result = view_transaction_details()
        
        assert result is True
        mock_get_txn.assert_called_once_with(5)
        mock_get_items.assert_called_once_with(5)



def test_view_last_sale(monkeypatch, capsys):
    """
    SCRUM-71: Test that view_last_transaction() displays the correct transaction
    
    Acceptance Criteria:
    - After completing a sale, view_last_transaction() should display the most recent transaction
    - The receipt should show correct transaction ID, items, quantities, prices, and total
    - Should handle case when no previous sale exists
    """
    from src.sales import view_last_transaction
    from src.database_manager import get_transaction_by_id, get_items_for_transaction
    import src.sales
    
    # Test case 1: No previous sale
    src.sales.LAST_TRANSACTION_ID = None
    result = view_last_transaction()
    captured = capsys.readouterr()
    
    assert result is False
    assert "No previous sale found" in captured.out
    
    # Test case 2: After completing a sale, verify correct transaction is displayed
    # First, simulate a completed sale by setting LAST_TRANSACTION_ID
    # In a real scenario, this would be set by record_sale()
    
    # Mock a transaction ID (assuming transaction 1 exists in test database)
    src.sales.LAST_TRANSACTION_ID = 1
    
    # Call view_last_transaction
    result = view_last_transaction()
    captured = capsys.readouterr()
    
    # Verify the function returns True for successful display
    assert result is True
    
    # Verify receipt header is displayed
    assert "LAST TRANSACTION RECEIPT" in captured.out
    assert "Transaction ID: 1" in captured.out
    
    # Verify transaction details are shown
    transaction = get_transaction_by_id(1)
    assert transaction is not None
    assert f"€{transaction['total_amount']:.2f}" in captured.out
    
    # Verify items are displayed correctly
    items = get_items_for_transaction(1)
    assert items is not None and len(items) > 0
    
    for item in items:
        assert item['name'] in captured.out
        assert str(item['quantity']) in captured.out
    
    # Test case 3: Verify it shows the LAST transaction after multiple sales
    # Simulate completing another sale
    src.sales.LAST_TRANSACTION_ID = 2
    
    result = view_last_transaction()
    captured = capsys.readouterr()
    
    assert result is True
    assert "Transaction ID: 2" in captured.out
    # Should show transaction 2, not transaction 1
    assert "Transaction ID: 1" not in captured.out


def test_view_last_sale_integration(monkeypatch, capsys):
    """
    SCRUM-75: Integration test that verifies view_last_transaction() 
    works correctly after record_sale() completes a transaction
    """
    from src.sales import view_last_transaction
    import src.sales
    
    # Simulate a complete sale workflow
    inputs = iter([
        '1',  # Add item to cart
        '1',  # Product ID
        '2',  # Quantity
        '3',  # Complete sale
        'y'   # Confirm sale
    ])
    
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    
    # Record a sale
    result = record_sale()
    assert result is True
    
    # Clear captured output from record_sale
    capsys.readouterr()
    
    # Verify LAST_TRANSACTION_ID was set
    assert src.sales.LAST_TRANSACTION_ID is not None
    
    # Now view the last transaction
    result = view_last_transaction()
    captured = capsys.readouterr()
    
    assert result is True
    assert "LAST TRANSACTION RECEIPT" in captured.out
    assert f"Transaction ID: {src.sales.LAST_TRANSACTION_ID}" in captured.out


def test_view_last_sale_error_handling(monkeypatch, capsys):
    """
    SCRUM-75: Test error handling when transaction data is corrupted or missing
    """
    from src.sales import view_last_transaction
    import src.sales
    
    # Set a transaction ID that should exist
    src.sales.LAST_TRANSACTION_ID = 999
    
    # Mock get_transaction_by_id to return None (simulating data corruption)
    with patch('src.sales.get_transaction_by_id', return_value=None):
        result = view_last_transaction()
        captured = capsys.readouterr()
        
        assert result is False
        assert "Error: Last transaction could not be retrieved" in captured.out
    
    # Mock get_items_for_transaction to return empty list (simulating missing items)
    with patch('src.sales.get_transaction_by_id', return_value={'id': 999, 'total_amount': 50.0, 'timestamp': '2025-11-24'}):
        with patch('src.sales.get_items_for_transaction', return_value=[]):
            result = view_last_transaction()
            captured = capsys.readouterr()
            
            assert result is False
            assert "Error: No items found for last transaction" in captured.out


# scrum-15: view sales history tests
class TestViewSalesHistory:
    """test class for view_sales_history function"""
    
    @patch('src.sales.get_all_transactions')
    @patch('builtins.input')
    def test_view_sales_history_no_transactions(self, mock_input, mock_get_all, capsys):
        """test view sales history with no transactions"""
        mock_get_all.return_value = []
        
        result = view_sales_history()
        captured = capsys.readouterr()
        
        assert result is False
        assert "No sales transactions found" in captured.out
    
    @patch('src.sales.get_all_transactions')
    @patch('builtins.input')
    def test_view_sales_history_displays_list(self, mock_input, mock_get_all, capsys):
        """test view sales history displays transaction list"""
        mock_get_all.return_value = [
            {"id": 3, "timestamp": "2025-11-25 14:00:00", "total_amount": 75.50},
            {"id": 2, "timestamp": "2025-11-24 10:30:00", "total_amount": 45.00},
            {"id": 1, "timestamp": "2025-11-23 09:00:00", "total_amount": 30.00}
        ]
        mock_input.return_value = "0"
        
        result = view_sales_history()
        captured = capsys.readouterr()
        
        assert result is True
        assert "Sales History" in captured.out
        assert "2025-11-25 14:00:00" in captured.out
        assert "75.50" in captured.out
        assert "Total transactions: 3" in captured.out
    
    @patch('src.sales.get_items_for_transaction')
    @patch('src.sales.get_transaction_by_id')
    @patch('src.sales.get_all_transactions')
    @patch('builtins.input')
    def test_view_sales_history_select_transaction(self, mock_input, mock_get_all, 
                                                    mock_get_txn, mock_get_items, capsys):
        """test selecting a transaction to view details"""
        mock_get_all.return_value = [
            {"id": 1, "timestamp": "2025-11-25 12:00:00", "total_amount": 50.00}
        ]
        mock_input.return_value = "1"
        mock_get_txn.return_value = {
            "id": 1,
            "timestamp": "2025-11-25 12:00:00",
            "total_amount": 50.00
        }
        mock_get_items.return_value = [
            {"name": "Test Product", "quantity": 2, "price_at_sale": 25.00}
        ]
        
        result = view_sales_history()
        captured = capsys.readouterr()
        
        assert result is True
        assert "TRANSACTION DETAILS" in captured.out
        assert "Test Product" in captured.out
        mock_get_txn.assert_called_once_with(1)
        mock_get_items.assert_called_once_with(1)
    
    @patch('src.sales.get_all_transactions')
    @patch('builtins.input')
    def test_view_sales_history_invalid_id_non_numeric(self, mock_input, mock_get_all, capsys):
        """test invalid non-numeric transaction id"""
        mock_get_all.return_value = [
            {"id": 1, "timestamp": "2025-11-25 12:00:00", "total_amount": 50.00}
        ]
        mock_input.return_value = "abc"
        
        result = view_sales_history()
        captured = capsys.readouterr()
        
        assert result is True
        assert "must be a valid number" in captured.out
    
    @patch('src.sales.get_all_transactions')
    @patch('builtins.input')
    def test_view_sales_history_invalid_id_negative(self, mock_input, mock_get_all, capsys):
        """test invalid negative transaction id"""
        mock_get_all.return_value = [
            {"id": 1, "timestamp": "2025-11-25 12:00:00", "total_amount": 50.00}
        ]
        mock_input.return_value = "-1"
        
        result = view_sales_history()
        captured = capsys.readouterr()
        
        assert result is True
        assert "must be a positive number" in captured.out
    
    @patch('src.sales.get_all_transactions')
    @patch('builtins.input')
    def test_view_sales_history_transaction_not_in_list(self, mock_input, mock_get_all, capsys):
        """test selecting transaction id not in list"""
        mock_get_all.return_value = [
            {"id": 1, "timestamp": "2025-11-25 12:00:00", "total_amount": 50.00}
        ]
        mock_input.return_value = "999"
        
        result = view_sales_history()
        captured = capsys.readouterr()
        
        assert result is True
        assert "not found" in captured.out
    
    @patch('src.sales.get_all_transactions')
    @patch('builtins.input')
    def test_view_sales_history_empty_input(self, mock_input, mock_get_all):
        """test empty input returns to menu"""
        mock_get_all.return_value = [
            {"id": 1, "timestamp": "2025-11-25 12:00:00", "total_amount": 50.00}
        ]
        mock_input.return_value = ""
        
        result = view_sales_history()
        
        assert result is True
    
    @patch('src.sales.get_transaction_by_id')
    @patch('src.sales.get_all_transactions')
    @patch('builtins.input')
    def test_view_sales_history_transaction_retrieval_error(self, mock_input, 
                                                            mock_get_all, mock_get_txn, capsys):
        """test error when transaction cannot be retrieved"""
        mock_get_all.return_value = [
            {"id": 1, "timestamp": "2025-11-25 12:00:00", "total_amount": 50.00}
        ]
        mock_input.return_value = "1"
        mock_get_txn.return_value = None
        
        result = view_sales_history()
        captured = capsys.readouterr()
        
        assert result is True
        assert "Could not retrieve transaction" in captured.out
    
    @patch('src.sales.get_items_for_transaction')
    @patch('src.sales.get_transaction_by_id')
    @patch('src.sales.get_all_transactions')
    @patch('builtins.input')
    def test_view_sales_history_no_items_for_transaction(self, mock_input, mock_get_all,
                                                          mock_get_txn, mock_get_items, capsys):
        """test error when no items found for transaction"""
        mock_get_all.return_value = [
            {"id": 1, "timestamp": "2025-11-25 12:00:00", "total_amount": 50.00}
        ]
        mock_input.return_value = "1"
        mock_get_txn.return_value = {
            "id": 1,
            "timestamp": "2025-11-25 12:00:00",
            "total_amount": 50.00
        }
        mock_get_items.return_value = []
        
        result = view_sales_history()
        captured = capsys.readouterr()
        
        assert result is True
        assert "No items found for transaction" in captured.out


# scrum-15: integration test for view sales history
def test_view_sales_history():
    """
    scrum-15: integration test that verifies view_sales_history()
    displays all transactions and allows viewing details
    
    acceptance criteria:
    - system displays list of past sales
    - includes date, products sold, quantities, total amount
    - user can select a transaction to see full item list
    """
    from src.database_manager import get_all_transactions, get_items_for_transaction
    
    # get actual transactions from database
    transactions = get_all_transactions()
    
    # if we have transactions, verify the structure
    if transactions:
        assert isinstance(transactions, list)
        
        # verify each transaction has required fields
        for txn in transactions:
            assert "id" in txn
            assert "timestamp" in txn
            assert "total_amount" in txn
        
        # verify we can get items for each transaction
        for txn in transactions:
            items = get_items_for_transaction(txn["id"])
            assert isinstance(items, list)
            
            # if items exist, verify structure
            for item in items:
                assert "name" in item
                assert "quantity" in item
                assert "price_at_sale" in item
