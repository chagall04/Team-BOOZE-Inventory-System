# tests/test_database_manager.py
"""Tests for database operations including users, products, and transactions."""

import pytest
from unittest.mock import patch, MagicMock
import sqlite3 # Ensure sqlite3 is imported
from src.database_manager import (
    get_user_by_username, create_user, delete_user, insert_product,
    adjust_stock, get_stock_by_id, get_product_details, start_transaction,
    log_item_sale, get_low_stock_report, get_transaction_by_id,
    get_items_for_transaction, process_sale_transaction, search_products_by_term
)

# Helper to mock a row behaving like a dict
def mock_row(data):
    row = MagicMock()
    row.__getitem__.side_effect = data.__getitem__
    return row


class TestGetUserByUsername:
    @patch('src.database_manager.get_db_connection')
    def test_get_user_found(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = mock_row({"password_hash": "hash123", "role": "Manager"})
        
        result = get_user_by_username("testuser")
        
        assert result == {"hash": "hash123", "role": "Manager"}

    @patch('src.database_manager.get_db_connection')
    def test_get_user_not_found(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value.fetchone.return_value = None
        
        result = get_user_by_username("unknown")
        assert result is None
    

class TestCreateUser:
    @patch('src.database_manager.bcrypt')
    @patch('src.database_manager.get_db_connection')
    def test_create_user_success(self, mock_get_conn, mock_bcrypt):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1
        
        mock_bcrypt.hashpw.return_value = b'hashed_secret'
        
        success, result = create_user("newuser", "pass", "Clerk")
        
        assert success is True
        assert result == 1

    @patch('src.database_manager.bcrypt')
    @patch('src.database_manager.get_db_connection')
    def test_create_user_duplicate(self, mock_get_conn, mock_bcrypt):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_bcrypt.hashpw.return_value = b'hashed'
        mock_cursor.execute.side_effect = sqlite3.IntegrityError
        
        success, msg = create_user("existing", "pass", "Clerk")
        
        assert success is False
        assert "already exists" in msg
    

class TestDeleteUser:
    @patch('src.database_manager.get_db_connection')
    def test_delete_user_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        success, msg = delete_user("todelete")
        
        assert success is True
        assert "deleted" in msg

    @patch('src.database_manager.get_db_connection')
    def test_delete_user_not_found(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0
        
        success, msg = delete_user("unknown")
        
        assert success is False
        assert "not found" in msg
    

class TestInsertProduct:
    @patch('src.database_manager.get_db_connection')
    def test_insert_product_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 101
        
        data = {'name': 'New Gin', 'brand': 'BrandX', 'type': 'Gin', 'price': 20.0, 'quantity': 10}
        success, result = insert_product(data)
        
        assert success is True
        assert result == 101
    

class TestInventoryFunctions:
    @patch('src.database_manager.get_db_connection')
    def test_adjust_stock_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        result = adjust_stock(1, 50)
        assert result is True

    @patch('src.database_manager.get_db_connection')
    def test_get_stock_by_id_found(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value.fetchone.return_value = mock_row({"name": "Rum", "quantity_on_hand": 15})
        
        result = get_stock_by_id(1)
        assert result == {"name": "Rum", "quantity": 15}
    

class TestSalesDatabaseFunctions:
    @patch('src.database_manager.get_db_connection')
    def test_process_sale_transaction_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 999
        mock_cursor.fetchone.return_value = mock_row({"quantity_on_hand": 10})
        
        cart = [{'product_id': 1, 'quantity': 2, 'price': 10.0}]
        success, trans_id = process_sale_transaction(cart, 20.0)
        
        assert success is True
        assert trans_id == 999
    

class TestLowStockDatabase:
    @patch('src.database_manager.get_db_connection')
    def test_get_low_stock_report(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [mock_row({"id": 1, "name": "A", "brand": "B", "quantity_on_hand": 2, "price": 10})]
        
        report = get_low_stock_report(5)
        assert len(report) == 1
        assert report[0]['name'] == "A"
    

class TestTransactionDetails:
    @patch('src.database_manager.get_db_connection')
    def test_get_transaction_by_id(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value.fetchone.return_value = mock_row({"transaction_id": 1, "timestamp": "2023-01-01", "total_amount": 100})
        
        result = get_transaction_by_id(1)
        assert result['total_amount'] == 100

    @patch('src.database_manager.get_db_connection')
    def test_get_items_for_transaction(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value.fetchall.return_value = [mock_row({"name": "Beer", "quantity": 6, "price_at_sale": 12.0})]
        
        items = get_items_for_transaction(1)
        assert len(items) == 1
    

class TestSearchProducts:
    @patch('src.database_manager.get_db_connection')
    def test_search_products_by_term(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [mock_row({"id": 1, "name": "Vodka", "brand": "Smirnoff", "quantity_on_hand": 10, "price": 15})]
        
        results = search_products_by_term("vodka")
        
        assert len(results) == 1
        assert results[0]['name'] == "Vodka"
        # Verify wildcards were added
        args = mock_cursor.execute.call_args[0]
        assert "%vodka%" in args[1]

class TestProductDetails:
    @patch('src.database_manager.get_db_connection')
    def test_get_product_details_found(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value.fetchone.return_value = mock_row({
            "id": 1, "name": "Whiskey", "price": 50.0, "quantity_on_hand": 5
        })
        
        result = get_product_details(1)
        assert result["name"] == "Whiskey"
        assert result["price"] == pytest.approx(50.0)

    @patch('src.database_manager.get_db_connection')
    def test_get_product_details_not_found(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value.fetchone.return_value = None
        
        result = get_product_details(999)
        assert result is None

class TestTransactionBasics:
    @patch('src.database_manager.get_db_connection')
    def test_start_transaction_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 123
        
        result = start_transaction(100.0)
        assert result == 123

    @patch('src.database_manager.get_db_connection')
    def test_start_transaction_failure(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("DB Error")
        
        result = start_transaction(100.0)
        assert result is None

    @patch('src.database_manager.get_db_connection')
    def test_log_item_sale_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        result = log_item_sale(1, 2, 1, 10.0)
        assert result is True

    @patch('src.database_manager.get_db_connection')
    def test_log_item_sale_failure(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("DB Error")
        
        result = log_item_sale(1, 2, 1, 10.0)
        assert result is False

class TestProcessSaleTransactionEdgeCases:
    @patch('src.database_manager.get_db_connection')
    def test_process_sale_insufficient_stock(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock stock check returning low quantity
        mock_cursor.fetchone.return_value = mock_row({"quantity_on_hand": 1})
        
        cart = [{'product_id': 1, 'quantity': 5, 'price': 10.0}]
        success, msg = process_sale_transaction(cart, 50.0)
        
        assert success is False
        assert "Insufficient stock" in msg
        mock_conn.rollback.assert_called_once()

    @patch('src.database_manager.get_db_connection')
    def test_process_sale_product_not_found(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock stock check returning None
        mock_cursor.fetchone.return_value = None
        
        cart = [{'product_id': 99, 'quantity': 1, 'price': 10.0}]
        success, msg = process_sale_transaction(cart, 10.0)
        
        assert success is False
        assert "not found" in msg
        mock_conn.rollback.assert_called_once()
