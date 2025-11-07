# tests/test_sales.py
# scrum-12 to scrum-13: sales management tests
# owned by: sara larkem

import pytest
from unittest.mock import patch, MagicMock
from src.sales import (
    validate_product_input,
    validate_quantity_input,
    check_stock_availability,
    display_cart,
    process_sale,
    record_sale
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
        assert "valid number" in error
    
    def test_validate_product_input_invalid_negative(self):
        """Test invalid negative product ID"""
        is_valid, product_id, error = validate_product_input("-1")
        assert is_valid is False
        assert product_id is None
        assert "positive number" in error
    
    def test_validate_product_input_invalid_zero(self):
        """Test invalid zero product ID"""
        is_valid, product_id, error = validate_product_input("0")
        assert is_valid is False
        assert product_id is None
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
        assert "valid number" in error
    
    def test_validate_quantity_input_invalid_negative(self):
        """Test invalid negative quantity"""
        is_valid, quantity, error = validate_quantity_input("-5")
        assert is_valid is False
        assert quantity is None
        assert "positive number" in error
    
    def test_validate_quantity_input_invalid_zero(self):
        """Test invalid zero quantity"""
        is_valid, quantity, error = validate_quantity_input("0")
        assert is_valid is False
        assert quantity is None
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
        assert product['name'] == 'Test Product'
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
        assert product['quantity_on_hand'] == 10
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
        assert "$21.00" in captured.out
        assert "Total: $21.00" in captured.out
    
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
        assert "Total: $26.00" in captured.out


class TestProcessSale:
    """Test process_sale function (SCRUM-37)"""
    
    def test_process_sale_empty_cart(self):
        """Test processing empty cart"""
        success, message = process_sale([])
        assert success is False
        assert "empty cart" in message.lower()
    
    @patch('src.sales.start_transaction')
    @patch('src.sales.log_item_sale')
    @patch('src.sales.adjust_stock')
    def test_process_sale_success_single_item(self, mock_adjust, mock_log, mock_start):
        """Test successful sale with single item"""
        mock_start.return_value = 123
        mock_log.return_value = True
        mock_adjust.return_value = True
        
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
        mock_start.assert_called_once_with(21.00)
        mock_log.assert_called_once_with(123, 1, 2, 10.50)
        mock_adjust.assert_called_once_with(1, 48)
    
    @patch('src.sales.start_transaction')
    @patch('src.sales.log_item_sale')
    @patch('src.sales.adjust_stock')
    def test_process_sale_success_multiple_items(self, mock_adjust, mock_log, mock_start):
        """Test successful sale with multiple items"""
        mock_start.return_value = 124
        mock_log.return_value = True
        mock_adjust.return_value = True
        
        cart = [
            {'product_id': 1, 'name': 'Product A', 'quantity': 2, 'price': 10.50, 'current_stock': 50},
            {'product_id': 2, 'name': 'Product B', 'quantity': 1, 'price': 5.00, 'current_stock': 30}
        ]
        
        success, message = process_sale(cart)
        assert success is True
        assert "Transaction ID: 124" in message
        mock_start.assert_called_once_with(26.00)
        assert mock_log.call_count == 2
        assert mock_adjust.call_count == 2
    
    @patch('src.sales.start_transaction')
    def test_process_sale_transaction_creation_fails(self, mock_start):
        """Test sale failure when transaction creation fails"""
        mock_start.return_value = None
        
        cart = [{
            'product_id': 1,
            'name': 'Test Product',
            'quantity': 2,
            'price': 10.50,
            'current_stock': 50
        }]
        
        success, message = process_sale(cart)
        assert success is False
        assert "Failed to create transaction" in message
    
    @patch('src.sales.start_transaction')
    @patch('src.sales.log_item_sale')
    def test_process_sale_log_item_fails(self, mock_log, mock_start):
        """Test sale failure when logging item fails"""
        mock_start.return_value = 125
        mock_log.return_value = False
        
        cart = [{
            'product_id': 1,
            'name': 'Test Product',
            'quantity': 2,
            'price': 10.50,
            'current_stock': 50
        }]
        
        success, message = process_sale(cart)
        assert success is False
        assert "Failed to log sale" in message
    
    @patch('src.sales.start_transaction')
    @patch('src.sales.log_item_sale')
    @patch('src.sales.adjust_stock')
    def test_process_sale_adjust_stock_fails(self, mock_adjust, mock_log, mock_start):
        """Test sale failure when stock adjustment fails"""
        mock_start.return_value = 126
        mock_log.return_value = True
        mock_adjust.return_value = False
        
        cart = [{
            'product_id': 1,
            'name': 'Test Product',
            'quantity': 2,
            'price': 10.50,
            'current_stock': 50
        }]
        
        success, message = process_sale(cart)
        assert success is False
        assert "Failed to update stock" in message


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
    @patch('src.sales.check_stock_availability')
    def test_record_sale_complete_empty_cart(self, mock_check, mock_input):
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

