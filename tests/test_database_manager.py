# tests/test_database_manager.py
# scrum-17 to scrum-22: database manager tests
# owned by: charlie gallagher

"""Tests for database operations including users, products, and transactions."""

import sqlite3
from unittest.mock import patch, MagicMock
import pytest
from src.database_manager import get_user_by_username, create_user, delete_user, insert_product



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
        assert result["price"] == pytest.approx(10.50, rel=1e-6)
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


# SCRUM-6 Update Product Database Tests
class TestUpdateProductFunctions:
    """test class for update product database functions"""
    
    @patch('src.database_manager.get_db_connection')
    def test_update_product_details_success_all_fields(self, mock_get_db):
        """test successful update of all product fields"""
        from src.database_manager import update_product_details
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        update_data = {
            'name': 'Updated Beer',
            'brand': 'Updated Brand',
            'type': 'Lager',
            'price': 6.99,
            'quantity_on_hand': 100,
            'abv': 5.0,
            'volume_ml': 330,
            'origin_country': 'Germany',
            'description': 'Updated description'
        }
        
        success, message = update_product_details(1, update_data)
        
        assert success is True
        assert message == "Product updated successfully"
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_update_product_details_partial_update(self, mock_get_db):
        """test updating only some fields"""
        from src.database_manager import update_product_details
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        update_data = {
            'price': 7.99,
            'description': 'New description only'
        }
        
        success, message = update_product_details(1, update_data)
        
        assert success is True
        assert message == "Product updated successfully"
        # Verify SQL contains only the updated fields
        call_args = mock_cursor.execute.call_args[0]
        assert 'price = ?' in call_args[0]
        assert 'description = ?' in call_args[0]
        mock_conn.commit.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_update_product_details_product_not_found(self, mock_get_db):
        """test updating non-existent product"""
        from src.database_manager import update_product_details
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0
        
        update_data = {'price': 9.99}
        
        success, message = update_product_details(999, update_data)
        
        assert success is False
        assert message == "Product not found"
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_update_product_details_no_valid_fields(self, mock_get_db):
        """test update with no valid fields to update"""
        from src.database_manager import update_product_details
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        update_data = {}
        
        success, _ = update_product_details(1, update_data)
        
        assert success is False
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_update_product_details_invalid_fields_ignored(self, mock_get_db):
        """test that invalid field names are ignored"""
        from src.database_manager import update_product_details
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        update_data = {
            'price': 8.99,
            'invalid_field': 'should be ignored',
            'another_bad_field': 123
        }
        
        success, _ = update_product_details(1, update_data)
        
        assert success is True
        # Verify only valid field was included in SQL
        call_args = mock_cursor.execute.call_args[0]
        assert 'price = ?' in call_args[0]
        assert 'invalid_field' not in call_args[0]
    
    @patch('src.database_manager.get_db_connection')
    def test_update_product_details_database_error(self, mock_get_db):
        """test handling of database errors during update"""
        from src.database_manager import update_product_details
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database constraint violation")
        
        update_data = {'price': 10.99}
        
        success, message = update_product_details(1, update_data)
        
        assert success is False
        assert "Database error" in message
        assert "Database constraint violation" in message
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_update_product_details_with_none_values(self, mock_get_db):
        """test updating fields to None (clearing optional fields)"""
        from src.database_manager import update_product_details
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        update_data = {
            'abv': None,
            'description': None
        }
        
        success, _ = update_product_details(1, update_data)
        
        assert success is True
        # Verify None values are included
        call_args = mock_cursor.execute.call_args[0]
        assert None in call_args[1]
    
    @patch('src.database_manager.get_db_connection')
    def test_update_product_alias_function(self, mock_get_db):
        """test that update_product alias works correctly"""
        from src.database_manager import update_product
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        update_data = {'price': 5.99}
        
        success, _ = update_product(1, update_data)
        
        assert success is True


# SCRUM-9/SCRUM-11 Inventory Tracking Database Tests
class TestInventoryTrackingFunctions:
    """test class for inventory tracking database functions"""
    
    @patch('src.database_manager.get_db_connection')
    def test_adjust_stock_database_error(self, mock_get_db):
        """test handling of database error during stock adjustment"""
        from src.database_manager import adjust_stock
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        
        result = adjust_stock(1, 100)
        
        assert result is False
        mock_conn.close.assert_called_once()
