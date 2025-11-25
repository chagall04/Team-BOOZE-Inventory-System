# tests/test_database_manager.py
# scrum-17 to scrum-22: database manager tests
# owned by: charlie gallagher

"""Tests for database operations including users, products, and transactions."""

import sqlite3
from unittest.mock import patch, MagicMock

import pytest

from src.database_manager import (
    get_user_by_username,
    create_user,
    delete_user,
    insert_product,
    get_all_products,
    search_products_by_term
)



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


# SCRUM-45 Get All Products Tests
@patch('src.database_manager.get_db_connection')
def test_get_all_products_returns_all_products(mock_get_db):
    """Test that get_all_products() retrieves all products from database"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock three products
    mock_rows = [
        {
            'id': 1,
            'name': 'Test Beer',
            'brand': 'Test Brand 2',
            'type': 'Beer',
            'abv': 5.0,
            'volume_ml': 500,
            'origin_country': 'Germany',
            'price': 4.50,
            'quantity_on_hand': 100,
            'description': 'Test beer description'
        },
        {
            'id': 2,
            'name': 'Test Whiskey',
            'brand': 'Test Brand 1',
            'type': 'Whiskey',
            'abv': 40.0,
            'volume_ml': 700,
            'origin_country': 'Ireland',
            'price': 30.00,
            'quantity_on_hand': 25,
            'description': 'Test whiskey description'
        },
        {
            'id': 3,
            'name': 'Test Wine',
            'brand': 'Test Brand 3',
            'type': 'Wine',
            'abv': 12.5,
            'volume_ml': 750,
            'origin_country': 'France',
            'price': 15.99,
            'quantity_on_hand': 50,
            'description': 'Test wine description'
        }
    ]
    
    mock_cursor.fetchall.return_value = mock_rows
    
    products = get_all_products()
    
    # Verify all products are returned
    assert len(products) == 3
    
    # Verify all fields are present for first product
    assert products[0]['id'] == 1
    assert products[0]['name'] == 'Test Beer'
    assert products[0]['brand'] == 'Test Brand 2'
    assert products[0]['type'] == 'Beer'
    assert products[0]['abv'] == pytest.approx(5.0)
    assert products[0]['volume_ml'] == 500
    assert products[0]['origin_country'] == 'Germany'
    assert products[0]['price'] == pytest.approx(4.50)
    assert products[0]['quantity_on_hand'] == 100
    assert products[0]['description'] == 'Test beer description'
    
    # Verify SQL query ordered by name
    call_args = mock_cursor.execute.call_args[0][0]
    assert 'ORDER BY name ASC' in call_args
    mock_conn.close.assert_called_once()


@patch('src.database_manager.get_db_connection')
def test_get_all_products_empty_database(mock_get_db):
    """Test that get_all_products() returns empty list when no products exist"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []
    
    products = get_all_products()
    
    assert not products
    assert isinstance(products, list)
    mock_conn.close.assert_called_once()


@patch('src.database_manager.get_db_connection')
def test_get_all_products_with_null_optional_fields(mock_get_db):
    """Test that get_all_products() handles products with null optional fields"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    mock_rows = [{
        'id': 1,
        'name': 'Minimal Product',
        'brand': 'Minimal Brand',
        'type': 'Spirit',
        'abv': None,
        'volume_ml': None,
        'origin_country': None,
        'price': 20.00,
        'quantity_on_hand': 10,
        'description': None
    }]
    
    mock_cursor.fetchall.return_value = mock_rows
    
    products = get_all_products()
    
    assert len(products) == 1
    assert products[0]['name'] == 'Minimal Product'
    assert products[0]['abv'] is None
    assert products[0]['volume_ml'] is None
    assert products[0]['origin_country'] is None
    assert products[0]['description'] is None
    assert products[0]['price'] == pytest.approx(20.00)
    assert products[0]['quantity_on_hand'] == 10
    mock_conn.close.assert_called_once()


@patch('src.database_manager.get_db_connection')
def test_get_all_products_returns_dictionaries(mock_get_db):
    """Test that get_all_products() returns list of dictionaries"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    mock_rows = [{
        'id': 1,
        'name': 'Test Product',
        'brand': 'Test Brand',
        'type': 'Test Type',
        'abv': None,
        'volume_ml': None,
        'origin_country': None,
        'price': 10.00,
        'quantity_on_hand': 5,
        'description': None
    }]
    
    mock_cursor.fetchall.return_value = mock_rows
    
    products = get_all_products()
    
    assert isinstance(products, list)
    assert len(products) == 1
    assert isinstance(products[0], dict)
    
    # Verify dictionary keys
    expected_keys = {'id', 'name', 'brand', 'type', 'abv', 'volume_ml', 
                     'origin_country', 'price', 'quantity_on_hand', 'description'}
    assert set(products[0].keys()) == expected_keys
    mock_conn.close.assert_called_once()


@patch('src.database_manager.get_db_connection')
def test_get_all_products_handles_database_error(mock_get_db):
    """Test that get_all_products() returns empty list on database error"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = sqlite3.Error("Simulated database error")
    
    products = get_all_products()
    
    assert not products
    assert isinstance(products, list)
    mock_conn.close.assert_called_once()


# Total Inventory Value Tests
class TestGetTotalInventoryValue:
    """test class for get_total_inventory_value database function"""
    
    @patch('src.database_manager.get_db_connection')
    def test_get_total_inventory_value_success(self, mock_get_db):
        """test successful calculation of total inventory value"""
        from src.database_manager import get_total_inventory_value
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # simulate SUM result (e.g., 5 products * 10 EUR * 50 quantity = 2500.00)
        mock_cursor.fetchone.return_value = [2500.00]
        
        result = get_total_inventory_value()
        
        assert result == pytest.approx(2500.00, rel=1e-6)
        mock_cursor.execute.assert_called_once_with("SELECT SUM(price * quantity_on_hand) FROM booze")
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_total_inventory_value_empty_database(self, mock_get_db):
        """test that empty database returns 0.00"""
        from src.database_manager import get_total_inventory_value
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # empty database returns NULL from SUM
        mock_cursor.fetchone.return_value = [None]
        
        result = get_total_inventory_value()
        
        assert result == pytest.approx(0.00, rel=1e-6)
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_total_inventory_value_null_result(self, mock_get_db):
        """test that NULL result from query returns 0.00"""
        from src.database_manager import get_total_inventory_value
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # NULL result
        mock_cursor.fetchone.return_value = None
        
        result = get_total_inventory_value()
        
        assert result == pytest.approx(0.00, rel=1e-6)
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_total_inventory_value_database_error(self, mock_get_db):
        """test that database error returns 0.00"""
        from src.database_manager import get_total_inventory_value
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database connection error")
        
        result = get_total_inventory_value()
        
        assert result == pytest.approx(0.00, rel=1e-6)
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_total_inventory_value_returns_float(self, mock_get_db):
        """test that result is always a float"""
        from src.database_manager import get_total_inventory_value
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # database might return integer
        mock_cursor.fetchone.return_value = [1250]
        
        result = get_total_inventory_value()
        
        assert isinstance(result, float)
        assert result == pytest.approx(1250.00, rel=1e-6)
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_total_inventory_value_zero_stock(self, mock_get_db):
        """test calculation when all products have zero stock"""
        from src.database_manager import get_total_inventory_value
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # all products have 0 quantity_on_hand
        mock_cursor.fetchone.return_value = [0.00]
        
        result = get_total_inventory_value()
        
        assert result == pytest.approx(0.00, rel=1e-6)
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_total_inventory_value_large_value(self, mock_get_db):
        """test calculation with large inventory value"""
        from src.database_manager import get_total_inventory_value
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # large inventory value
        mock_cursor.fetchone.return_value = [123456.78]
        
        result = get_total_inventory_value()
        
        assert result == pytest.approx(123456.78, rel=1e-6)
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_total_inventory_value_decimal_precision(self, mock_get_db):
        """test that decimal values are handled correctly"""
        from src.database_manager import get_total_inventory_value
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # value with decimal precision
        mock_cursor.fetchone.return_value = [1234.56]
        
        result = get_total_inventory_value()
        
        assert result == pytest.approx(1234.56, rel=1e-6)
        assert isinstance(result, float)
        mock_conn.close.assert_called_once()


# Low Stock Report Database Tests
class TestGetLowStockReport:
    """test class for get_low_stock_report database function"""
    
    @patch('src.database_manager.get_db_connection')
    def test_get_low_stock_report_returns_products_below_threshold(self, mock_get_db):
        """test retrieving products below threshold"""
        from src.database_manager import get_low_stock_report
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_rows = [
            {
                "id": 1,
                "name": "Low Stock Item",
                "brand": "Test Brand",
                "quantity_on_hand": 5,
                "price": 10.50
            },
            {
                "id": 2,
                "name": "Another Low Item",
                "brand": "Another Brand",
                "quantity_on_hand": 15,
                "price": 20.00
            }
        ]
        mock_cursor.fetchall.return_value = mock_rows
        
        result = get_low_stock_report(20)
        
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Low Stock Item"
        assert result[0]["quantity_on_hand"] == 5
        assert result[1]["id"] == 2
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_low_stock_report_empty_result(self, mock_get_db):
        """test when no products below threshold"""
        from src.database_manager import get_low_stock_report
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        result = get_low_stock_report(20)
        
        assert result == []
        assert isinstance(result, list)
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_low_stock_report_database_error(self, mock_get_db):
        """test error handling returns empty list"""
        from src.database_manager import get_low_stock_report
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        
        result = get_low_stock_report(20)
        
        assert result == []
        mock_conn.close.assert_called_once()


# Transaction Detail Database Tests
class TestGetTransactionById:
    """test class for get_transaction_by_id database function"""
    
    @patch('src.database_manager.get_db_connection')
    def test_get_transaction_by_id_success(self, mock_get_db):
        """test successful retrieval of transaction"""
        from src.database_manager import get_transaction_by_id
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_row = {
            "transaction_id": 123,
            "timestamp": "2025-11-24 12:00:00",
            "total_amount": 50.00
        }
        mock_cursor.fetchone.return_value = mock_row
        
        result = get_transaction_by_id(123)
        
        assert result is not None
        assert result["id"] == 123
        assert result["timestamp"] == "2025-11-24 12:00:00"
        assert result["total_amount"] == pytest.approx(50.00)
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_transaction_by_id_not_found(self, mock_get_db):
        """test transaction not found returns None"""
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
        """test database error returns None"""
        from src.database_manager import get_transaction_by_id
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        
        result = get_transaction_by_id(123)
        
        assert result is None
        mock_conn.close.assert_called_once()


class TestGetItemsForTransaction:
    """test class for get_items_for_transaction database function"""
    
    @patch('src.database_manager.get_db_connection')
    def test_get_items_for_transaction_success(self, mock_get_db):
        """test successful retrieval of transaction items"""
        from src.database_manager import get_items_for_transaction
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_rows = [
            {
                "name": "Product A",
                "quantity": 2,
                "price_at_sale": 10.00
            },
            {
                "name": "Product B",
                "quantity": 1,
                "price_at_sale": 25.00
            }
        ]
        mock_cursor.fetchall.return_value = mock_rows
        
        result = get_items_for_transaction(123)
        
        assert len(result) == 2
        assert result[0]["name"] == "Product A"
        assert result[0]["quantity"] == 2
        assert result[0]["price_at_sale"] == pytest.approx(10.00)
        assert result[1]["name"] == "Product B"
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_items_for_transaction_no_items(self, mock_get_db):
        """test transaction with no items returns empty list"""
        from src.database_manager import get_items_for_transaction
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        result = get_items_for_transaction(123)
        
        assert result == []
        assert isinstance(result, list)
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_get_items_for_transaction_database_error(self, mock_get_db):
        """test database error returns empty list"""
        from src.database_manager import get_items_for_transaction
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        
        result = get_items_for_transaction(123)
        
        assert result == []
        mock_conn.close.assert_called_once()


# SCRUM-67 Product Search Database Tests
class TestSearchProductsByTerm:
    """test class for search_products_by_term database function"""
    
    @patch('src.database_manager.get_db_connection')
    def test_search_products_by_term_success(self, mock_get_db):
        """test successful product search"""
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_rows = [
            {
                "id": 1,
                "name": "Vodka",
                "brand": "Smirnoff",
                "quantity_on_hand": 10,
                "price": 15.00
            },
            {
                "id": 2,
                "name": "Flavored Vodka",
                "brand": "Absolut",
                "quantity_on_hand": 5,
                "price": 18.00
            }
        ]
        mock_cursor.fetchall.return_value = mock_rows
        
        result = search_products_by_term("vodka")
        
        assert len(result) == 2
        assert result[0]["name"] == "Vodka"
        assert result[1]["name"] == "Flavored Vodka"
        # Verify wildcards were added
        call_args = mock_cursor.execute.call_args[0]
        assert "%vodka%" in call_args[1]
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_search_products_by_term_no_results(self, mock_get_db):
        """test search with no matching products"""
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        result = search_products_by_term("unknownbrand")
        
        assert not result
        assert isinstance(result, list)
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_search_products_by_term_database_error(self, mock_get_db):
        """test error handling returns empty list"""
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        
        
        result = search_products_by_term("vodka")
        
        assert not result
        mock_conn.close.assert_called_once()
