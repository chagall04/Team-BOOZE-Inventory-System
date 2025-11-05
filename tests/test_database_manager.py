# tests/test_database_manager.py
# scrum-17 to scrum-22: database manager tests
# owned by: charlie gallagher

import pytest
import sqlite3
from unittest.mock import patch, MagicMock
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
        assert "already exists" in result
    
    @patch('src.database_manager.get_db_connection')
    def test_create_user_database_error(self, mock_get_db):
        """test handling of database errors during user creation"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("db connection error")
        
        success, result = create_user("user", "pass", "Clerk")
        
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
        
        success, result = delete_user("testuser")
        
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
        mock_cursor.execute.side_effect = Exception("database error")
        
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
        assert "already exists" in result
        mock_conn.close.assert_called_once()
    
    @patch('src.database_manager.get_db_connection')
    def test_insert_product_database_error(self, mock_get_db):
        """test handling of general database errors"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("database connection error")
        
        product_data = {
            'name': 'test product',
            'brand': 'test brand',
            'type': 'spirits',
            'price': 25.99,
            'quantity': 20
        }
        
        success, result = insert_product(product_data)
        
        assert success is False
        assert "database connection error" in result
        mock_conn.close.assert_called_once()
