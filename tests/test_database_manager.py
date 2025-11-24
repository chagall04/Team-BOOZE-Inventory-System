# tests/test_database_manager.py
# scrum-17 to scrum-22: database manager tests
# owned by: charlie gallagher

"""Tests for database operations including users, products, and transactions."""

import sqlite3
import pytest
from unittest.mock import patch, MagicMock
from src.database_manager import get_all_products, get_user_by_username, create_user, delete_user, insert_product



class TestGetUserByUsername:
    """test class for getting user by username"""
    
    @patch('src.database_manager.get_db_connection')
    def test_get_user_by_username_success(self, mock_get_db):
        """test successfully retrieving user data"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # simulate row returned from database
        mock_row = {"password_hash": "hashed_password", "role": "Manager"}
        mock_cursor.fetchone.return_value = mock_row
        
        result = get_user_by_username("manager")
        
        assert result is not None
        assert result["hash"] == "hashed_password"
        assert result["role"] == "Manager"
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_user_by_username_not_found(self, mock_get_db):
        """test user not found returns none"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        result = get_user_by_username("nonexistent")
        
        assert result is None
        mock_conn.close.assert_called_once()


class TestCreateUser:
    """test class for creating users"""
    
    @patch('src.database_manager.get_db_connection')
    def test_create_user_success(self, mock_get_db):
        """test successful user creation"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1
        
        success, result = create_user("newuser", "password123", "Clerk")
        
        assert success is True
        assert result == 1
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_create_user_duplicate_username(self, mock_get_db):
        """test creating user with duplicate username fails"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed")
        
        success, result = create_user("existing", "password123", "Clerk")
        
        assert success is False
        assert result is not None
        assert isinstance(result, str)
        assert "already exists" in result
    
    @patch('src.database_manager.get_db_connection')
    def test_create_user_database_error(self, mock_get_db):
        """test handling of database errors during user creation"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("db connection error")

        success, _result = create_user("user", "pass", "Clerk")

        assert success is False


class TestDeleteUser:
    """test class for deleting users"""
    
    @patch('src.database_manager.get_db_connection')
    def test_delete_user_success(self, mock_get_db):
        """test successful user deletion"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1

        success, _result = delete_user("testuser")

        assert success is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('src.database_manager.get_db_connection')
    def test_delete_user_not_found(self, mock_get_db):
        """test deleting non-existent user"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0
        
        success, result = delete_user("nonexistent")
        
        assert success is False
        assert "not found" in result
    
    @patch('src.database_manager.get_db_connection')
    def test_delete_user_database_error(self, mock_get_db):
        """test handling of database errors during deletion"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("database error")
        
        success, result = delete_user("testuser")
        
        assert success is False
        assert "database error" in result
        mock_conn.close.assert_called_once()


class TestDatabaseConnection:
    """test class for database connection"""
    
    def test_get_db_connection_returns_connection(self):
        """test that get_db_connection returns a valid connection"""
        from src.database_manager import get_db_connection
        
        conn = get_db_connection()
        
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        conn.close()


class TestInsertProduct:
    """test class for inserting products (lucy's code)"""
    
    @patch('src.database_manager.get_db_connection')
    def test_insert_product_success_with_all_fields(self, mock_get_db):
        """test successful product insertion with all fields"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1
        
        product_data = {
            'name': 'test beer',
            'brand': 'test brand',
            'type': 'beer',
            'price': 4.99,
            'quantity': 50,
            'abv': 4.5,
            'volume_ml': 500,
            'origin_country': 'ireland',
            'description': 'test description'
        }
        
        success, result = insert_product(product_data)
        
        assert success is True
        assert result == 1
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_insert_product_success_with_required_fields_only(self, mock_get_db):
        """test successful product insertion with only required fields"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 2
        
        product_data = {
            'name': 'test wine',
            'brand': 'test brand',
            'type': 'wine',
            'price': 15.99,
            'quantity': 30
        }
        
        success, result = insert_product(product_data)
        
        assert success is True
        assert result == 2
        # verify optional fields are handled as None
        call_args = mock_cursor.execute.call_args[0]
        assert call_args[1][3] is None  # abv
        assert call_args[1][4] is None  # volume_ml
        assert call_args[1][5] is None  # origin_country
        assert call_args[1][8] is None  # description
    
    @patch('src.database_manager.get_db_connection')
    def test_insert_product_duplicate_name(self, mock_get_db):
        """test product insertion fails with duplicate name"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed")
        
        product_data = {
            'name': 'existing product',
            'brand': 'test brand',
            'type': 'beer',
            'price': 4.99,
            'quantity': 50
        }
        
        success, result = insert_product(product_data)
        
        assert success is False
        assert result is not None
        assert isinstance(result, str)
        assert "already exists" in result
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_insert_product_database_error(self, mock_get_db):
        """test handling of general database errors"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("database connection error")
        
        product_data = {
            'name': 'test product',
            'brand': 'test brand',
            'type': 'spirits',
            'price': 25.99,
            'quantity': 20
        }
        
        success, result = insert_product(product_data)
        
        assert success is False
        assert result is not None
        assert isinstance(result, str)
        assert "database connection error" in result
        mock_conn.close.assert_called_once()


# SCRUM-12 Sales Transaction Database Tests
class TestSalesDatabaseFunctions:
    """test class for sales transaction database functions"""
    
    @patch('src.database_manager.get_db_connection')
    def test_get_product_details_success(self, mock_get_db):
        """test successfully retrieving product details"""
        from src.database_manager import get_product_details
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_row = {
            "id": 1,
            "name": "Test Product",
            "price": 10.50,
            "quantity_on_hand": 50
        }
        mock_cursor.fetchone.return_value = mock_row
        
        result = get_product_details(1)
        
        assert result is not None
        assert result["id"] == 1
        assert result["name"] == "Test Product"
        assert abs(result["price"] - 10.50) < 0.01
        assert result["quantity_on_hand"] == 50
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_product_details_not_found(self, mock_get_db):
        """test product not found returns None"""
        from src.database_manager import get_product_details
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        result = get_product_details(999)
        
        assert result is None
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_start_transaction_success(self, mock_get_db):
        """test successful transaction creation"""
        from src.database_manager import start_transaction
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 123
        
        result = start_transaction(50.00)
        
        assert result == 123
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_start_transaction_failure(self, mock_get_db):
        """test transaction creation failure"""
        from src.database_manager import start_transaction
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        
        result = start_transaction(50.00)
        
        assert result is None
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_log_item_sale_success(self, mock_get_db):
        """test successfully logging item sale"""
        from src.database_manager import log_item_sale
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        result = log_item_sale(123, 1, 2, 10.50)
        
        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_log_item_sale_failure(self, mock_get_db):
        """test item sale logging failure"""
        from src.database_manager import log_item_sale
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        
        result = log_item_sale(123, 1, 2, 10.50)
        
        assert result is False
        mock_conn.close.assert_called_once()

    @patch('src.database_manager.get_db_connection')
    def test_process_sale_transaction_success_single_item(self, mock_get_db):
        """test successful transaction with single item"""
        from src.database_manager import process_sale_transaction
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 100
        mock_cursor.fetchone.return_value = {'quantity_on_hand': 50}
        
        cart = [{'product_id': 1, 'quantity': 3, 'price': 21.00}]
        success, result = process_sale_transaction(cart, 21.00)
        
        assert success is True
        assert result == 100
        assert mock_cursor.execute.call_count == 5
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.database_manager.get_db_connection')
    def test_process_sale_transaction_success_multiple_items(self, mock_get_db):
        """test successful transaction with multiple items"""
        from src.database_manager import process_sale_transaction
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 101
        mock_cursor.fetchone.side_effect = [
            {'quantity_on_hand': 50},
            {'quantity_on_hand': 30}
        ]
        
        cart = [
            {'product_id': 1, 'quantity': 3, 'price': 21.00},
            {'product_id': 2, 'quantity': 1, 'price': 5.00}
        ]
        success, result = process_sale_transaction(cart, 26.00)
        
        assert success is True
        assert result == 101
        assert mock_cursor.execute.call_count == 8
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.database_manager.get_db_connection')
    def test_process_sale_transaction_product_not_found(self, mock_get_db):
        """test transaction failure when product not found"""
        from src.database_manager import process_sale_transaction
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 102
        mock_cursor.fetchone.return_value = None
        
        cart = [{'product_id': 999, 'quantity': 1, 'price': 10.00}]
        success, result = process_sale_transaction(cart, 10.00)
        
        assert success is False
        assert "Product 999 not found" in str(result)
        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.database_manager.get_db_connection')
    def test_process_sale_transaction_database_error(self, mock_get_db):
        """test transaction failure with database error"""
        from src.database_manager import process_sale_transaction
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database connection lost")
        
        cart = [{'product_id': 1, 'quantity': 1, 'price': 10.00}]
        success, result = process_sale_transaction(cart, 10.00)
        
        assert success is False
        assert "Database connection lost" in str(result)
        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.database_manager.get_db_connection')
    def test_process_sale_transaction_calculates_stock_correctly(self, mock_get_db):
        """test that new stock is calculated correctly"""
        from src.database_manager import process_sale_transaction
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 103
        mock_cursor.fetchone.return_value = {'quantity_on_hand': 50}

        cart = [{'product_id': 1, 'quantity': 3, 'price': 21.00}]
        success, _result = process_sale_transaction(cart, 21.00)

        assert success is True
        # verify UPDATE was called with correct new_stock (50 - 3 = 47)
        update_calls = [call for call in mock_cursor.execute.call_args_list
                       if 'UPDATE booze' in str(call)]
        assert len(update_calls) > 0
        assert (47, 1) in [call[0][1] for call in update_calls]

    @patch('src.database_manager.get_db_connection')
    def test_process_sale_transaction_prevents_negative_stock(self, mock_get_db):
        """test that race condition protection prevents negative stock"""
        from src.database_manager import process_sale_transaction
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 104
        # simulate race condition: stock was reduced to 2 by another transaction
        mock_cursor.fetchone.return_value = {'quantity_on_hand': 2}

        # try to sell 5 units when only 2 are available
        cart = [{'product_id': 1, 'quantity': 5, 'price': 10.00}]
        success, error_msg = process_sale_transaction(cart, 50.00)

        assert success is False
        assert isinstance(error_msg, str)
        assert "Insufficient stock" in error_msg
        assert "product 1" in error_msg
        # verify rollback was called
        mock_conn.rollback.assert_called_once()
        # verify UPDATE was never called (transaction failed before update)
        update_calls = [call for call in mock_cursor.execute.call_args_list
                       if 'UPDATE booze' in str(call)]
        assert len(update_calls) == 0


# SCRUM-14 Low Stock Report Database Tests
class TestLowStockDatabase:
    """test class for low stock report database functions (SCRUM-56)"""
    
    @patch('src.database_manager.get_db_connection')
    def test_get_low_stock_report_below_threshold(self, mock_get_db):
        """test retrieving products below threshold"""
        from src.database_manager import get_low_stock_report
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_rows = [
            {"id": 1, "name": "Product A", "brand": "Brand A", "quantity_on_hand": 5, "price": 25.00},
            {"id": 2, "name": "Product B", "brand": "Brand B", "quantity_on_hand": 10, "price": 30.00}
        ]
        mock_cursor.fetchall.return_value = mock_rows
        
        result = get_low_stock_report(20)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert abs(result[0]["price"] - 25.00) < 0.01
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_low_stock_report_no_products_below_threshold(self, mock_get_db):
        """test when no products are below threshold"""
        from src.database_manager import get_low_stock_report
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        result = get_low_stock_report(20)
        
        assert len(result) == 0
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_low_stock_report_with_custom_threshold(self, mock_get_db):
        """test with custom threshold value"""
        from src.database_manager import get_low_stock_report
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        get_low_stock_report(50)
        
        call_args = mock_cursor.execute.call_args[0]
        assert (50,) in call_args
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_low_stock_report_database_error_returns_empty_list(self, mock_get_db):
        """test that database errors return empty list"""
        from src.database_manager import get_low_stock_report
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        
        result = get_low_stock_report(20)
        
        assert not result
        mock_conn.close.assert_called_once()


# Additional inventory functions tests
class TestInventoryFunctions:
    """test class for inventory functions"""
    
    @patch('src.database_manager.get_db_connection')
    def test_adjust_stock_success(self, mock_get_db):
        """test successfully adjusting stock"""
        from src.database_manager import adjust_stock
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        result = adjust_stock(1, 50)
        
        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_adjust_stock_no_update(self, mock_get_db):
        """test adjust stock when product not found"""
        from src.database_manager import adjust_stock
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0
        
        result = adjust_stock(999, 50)
        
        assert result is False
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_adjust_stock_database_error(self, mock_get_db):
        """test adjust stock database error handling"""
        from src.database_manager import adjust_stock
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        
        result = adjust_stock(1, 50)
        
        assert result is False
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_stock_by_id_success(self, mock_get_db):
        """test successfully getting stock by id"""
        from src.database_manager import get_stock_by_id
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_row = {"name": "Test Product", "quantity_on_hand": 50}
        mock_cursor.fetchone.return_value = mock_row
        
        result = get_stock_by_id(1)
        
        assert result is not None
        assert result["name"] == "Test Product"
        assert result["quantity"] == 50
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_stock_by_id_not_found(self, mock_get_db):
        """test get stock by id when product not found"""
        from src.database_manager import get_stock_by_id
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        result = get_stock_by_id(999)
        
        assert result is None
        mock_conn.close.assert_called_once()


class TestTransactionDetails:
    """test class for transaction detail retrieval functions (scrum-60)"""
    
    @patch('src.database_manager.get_db_connection')
    def test_get_transaction_by_id_success(self, mock_get_db):
        """test successfully retrieving transaction by id"""
        from src.database_manager import get_transaction_by_id
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_row = {
            "transaction_id": 1,
            "timestamp": "2025-11-10 14:30:00",
            "total_amount": 45.50
        }
        mock_cursor.fetchone.return_value = mock_row
        
        result = get_transaction_by_id(1)
        
        assert result is not None
        assert result["id"] == 1
        assert result["timestamp"] == "2025-11-10 14:30:00"
        assert abs(result["total_amount"] - 45.50) < 0.01
        mock_cursor.execute.assert_called_once_with(
            "SELECT transaction_id, timestamp, total_amount FROM transactions WHERE transaction_id = ?",
            (1,)
        )
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_transaction_by_id_not_found(self, mock_get_db):
        """test get transaction by id when transaction not found"""
        from src.database_manager import get_transaction_by_id
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        result = get_transaction_by_id(999)
        
        assert result is None
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_transaction_by_id_database_error(self, mock_get_db):
        """test get transaction by id handles database error"""
        from src.database_manager import get_transaction_by_id
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        
        result = get_transaction_by_id(1)
        
        assert result is None
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_items_for_transaction_success(self, mock_get_db):
        """test successfully retrieving items for transaction"""
        from src.database_manager import get_items_for_transaction
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_rows = [
            {"name": "Product A", "quantity": 2, "price_at_sale": 10.50},
            {"name": "Product B", "quantity": 1, "price_at_sale": 24.50}
        ]
        mock_cursor.fetchall.return_value = mock_rows
        
        result = get_items_for_transaction(1)
        
        assert len(result) == 2
        assert result[0]["name"] == "Product A"
        assert result[0]["quantity"] == 2
        assert abs(result[0]["price_at_sale"] - 10.50) < 0.01
        assert result[1]["name"] == "Product B"
        assert result[1]["quantity"] == 1
        assert abs(result[1]["price_at_sale"] - 24.50) < 0.01
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_items_for_transaction_empty(self, mock_get_db):
        """test get items for transaction when no items found"""
        from src.database_manager import get_items_for_transaction
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        result = get_items_for_transaction(999)
        
        assert not result
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_items_for_transaction_database_error(self, mock_get_db):
        """test get items for transaction handles database error"""
        from src.database_manager import get_items_for_transaction
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        
        result = get_items_for_transaction(1)
        
        assert not result
        mock_conn.close.assert_called_once()


def test_get_all_products_returns_all_products():
    """
    Test that get_all_products() retrieves all products from database
    """

    product1 = {
        'name': 'Test Whiskey',
        'brand': 'Test Brand 1',
        'type': 'Whiskey',
        'abv': 40.0,
        'volume_ml': 700,
        'origin_country': 'Ireland',
        'price': 30.00,
        'quantity': 25,
        'description': 'Test whiskey description'
    }
    
    product2 = {
        'name': 'Test Beer',
        'brand': 'Test Brand 2',
        'type': 'Beer',
        'abv': 5.0,
        'volume_ml': 500,
        'origin_country': 'Germany',
        'price': 4.50,
        'quantity': 100,
        'description': 'Test beer description'
    }
    
    product3 = {
        'name': 'Test Wine',
        'brand': 'Test Brand 3',
        'type': 'Wine',
        'abv': 12.5,
        'volume_ml': 750,
        'origin_country': 'France',
        'price': 15.99,
        'quantity': 50,
        'description': 'Test wine description'
    }
    
    insert_product(product1)
    insert_product(product2)
    insert_product(product3)
    
    # Retrieve all products
    products = get_all_products()
    
    # Verify all products are returned
    assert len(products) == 3
    
    # Verify products are sorted alphabetically by name
    assert products[0]['name'] == 'Test Beer'
    assert products[1]['name'] == 'Test Whiskey'
    assert products[2]['name'] == 'Test Wine'
    
    # Verify all fields are present for first product
    assert 'id' in products[0]
    assert products[0]['name'] == 'Test Beer'
    assert products[0]['brand'] == 'Test Brand 2'
    assert products[0]['type'] == 'Beer'
    assert products[0]['abv'] == pytest.approx(5.0)
    assert products[0]['volume_ml'] == 500
    assert products[0]['origin_country'] == 'Germany'
    assert products[0]['price'] == pytest.approx(4.50)
    assert products[0]['quantity_on_hand'] == 100
    assert products[0]['description'] == 'Test beer description'


def test_get_all_products_empty_database():
    """
    Test that get_all_products() returns empty list when no products exist
    """
    products = get_all_products()
    
    assert not products
    assert isinstance(products, list)


def test_get_all_products_with_null_optional_fields():
    """
    Test that get_all_products() handles products with null optional fields
    """
    product = {
        'name': 'Minimal Product',
        'brand': 'Minimal Brand',
        'type': 'Spirit',
        'abv': None,
        'volume_ml': None,
        'origin_country': None,
        'price': 20.00,
        'quantity': 10,
        'description': None
    }
    
    insert_product(product)
    products = get_all_products()
    
    assert len(products) == 1
    assert products[0]['name'] == 'Minimal Product'
    assert products[0]['abv'] is None
    assert products[0]['volume_ml'] is None
    assert products[0]['origin_country'] is None
    assert products[0]['description'] is None
    assert products[0]['price'] == pytest.approx(20.00)
    assert products[0]['quantity_on_hand'] == 10


def test_get_all_products_returns_dictionaries():
    """
    Test that get_all_products() returns list of dictionaries
    """
    product = {
        'name': 'Test Product',
        'brand': 'Test Brand',
        'type': 'Test Type',
        'price': 10.00,
        'quantity': 5
    }
    
    insert_product(product)
    products = get_all_products()
    
    assert isinstance(products, list)
    assert len(products) == 1
    assert isinstance(products[0], dict)
    
    # Verify dictionary keys
    expected_keys = {'id', 'name', 'brand', 'type', 'abv', 'volume_ml', 
                     'origin_country', 'price', 'quantity_on_hand', 'description'}
    assert set(products[0].keys()) == expected_keys


def test_get_all_products_handles_database_error(monkeypatch):
    """
    Test that get_all_products() returns empty list on database error
    """
    def mock_connect(*args, **kwargs):
        raise sqlite3.Error("Simulated database error")
    
    monkeypatch.setattr('sqlite3.connect', mock_connect)
    
    products = get_all_products()
    
    assert not products
    assert isinstance(products, list)
