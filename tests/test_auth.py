# tests/test_auth.py
# scrum-17 to scrum-22: authentication tests
# owned by: charlie gallagher

"""Tests for user authentication and account management."""

import sqlite3
from unittest.mock import patch
import pytest
import bcrypt
from src.auth import login, create_account, delete_account



class TestLogin:
    """test class for login functionality"""

    @patch('src.auth.get_user_by_username')
    def test_login_success_manager(self, mock_get_user):
        """test successful login for manager role"""
        real_hash = bcrypt.hashpw(b"manager123", bcrypt.gensalt()).decode('utf-8')
        mock_get_user.return_value = {
            "hash": real_hash,
            "role": "Manager"
        }

        role = login("manager", "manager123")

        assert role == "Manager"

    @patch('src.auth.get_user_by_username')
    def test_login_success_clerk(self, mock_get_user):
        """test successful login for clerk role"""
        real_hash = bcrypt.hashpw(b"clerk123", bcrypt.gensalt()).decode('utf-8')
        mock_get_user.return_value = {
            "hash": real_hash,
            "role": "Clerk"
        }

        role = login("clerk", "clerk123")

        assert role == "Clerk"

    @patch('src.auth.get_user_by_username')
    def test_login_failure_wrong_password(self, mock_get_user):
        """test failed login with wrong password"""
        real_hash = bcrypt.hashpw(b"manager123", bcrypt.gensalt()).decode('utf-8')
        mock_get_user.return_value = {
            "hash": real_hash,
            "role": "Manager"
        }

        role = login("manager", "wrongpassword")

        assert role is None

    @patch('src.auth.get_user_by_username')
    def test_login_failure_user_not_found(self, mock_get_user):
        """test failed login with non-existent user"""
        mock_get_user.return_value = None

        role = login("nosuchuser", "password")

        assert role is None


class TestCreateAccount:
    """test class for account creation functionality"""
    
    @patch('src.auth.create_user')
    def test_create_account_success(self, mock_create_user):
        """test successful account creation"""
        mock_create_user.return_value = (True, 1)
        
        success, message = create_account("newuser", "password123", "Clerk")
        
        assert success is True
        assert "created successfully" in message
        mock_create_user.assert_called_once_with("newuser", "password123", "Clerk")
    
    @patch('src.auth.create_user')
    def test_create_account_username_too_short(self, mock_create_user):
        """test account creation fails with short username"""
        success, message = create_account("ab", "password123", "Clerk")
        
        assert success is False
        assert "3 characters" in message
        mock_create_user.assert_not_called()
    
    @patch('src.auth.create_user')
    def test_create_account_password_too_short(self, mock_create_user):
        """test account creation fails with short password"""
        success, message = create_account("validuser", "12345", "Clerk")
        
        assert success is False
        assert "6 characters" in message
        mock_create_user.assert_not_called()
    
    @patch('src.auth.create_user')
    def test_create_account_invalid_role(self, mock_create_user):
        """test account creation fails with invalid role"""
        success, message = create_account("validuser", "password123", "Admin")
        
        assert success is False
        assert "Manager or Clerk" in message
        mock_create_user.assert_not_called()
    
    @patch('src.auth.create_user')
    def test_create_account_database_error(self, mock_create_user):
        """test account creation handles database errors"""
        mock_create_user.return_value = (False, "username already exists")
        
        success, message = create_account("existinguser", "password123", "Clerk")
        
        assert success is False
        assert "username already exists" in message


class TestDeleteAccount:
    """test class for account deletion functionality"""
    
    @patch('src.auth.delete_user')
    @patch('src.auth.get_user_by_username')
    def test_delete_account_success(self, mock_get_user, mock_delete_user):
        """test successful account deletion"""
        real_hash = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode('utf-8')
        mock_get_user.return_value = {
            "hash": real_hash,
            "role": "Clerk"
        }
        mock_delete_user.return_value = (True, "user deleted")

        success, _message = delete_account("testuser", "password123")

        assert success is True
        mock_delete_user.assert_called_once_with("testuser")

    @patch('src.auth.delete_user')
    @patch('src.auth.get_user_by_username')
    def test_delete_account_wrong_password(self, mock_get_user, mock_delete_user):
        """test account deletion fails with wrong password"""
        real_hash = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode('utf-8')
        mock_get_user.return_value = {
            "hash": real_hash,
            "role": "Clerk"
        }
        
        success, message = delete_account("testuser", "wrongpassword")
        
        assert success is False
        assert "incorrect password" in message
        mock_delete_user.assert_not_called()
    
    @patch('src.auth.delete_user')
    @patch('src.auth.get_user_by_username')
    def test_delete_account_user_not_found(self, mock_get_user, mock_delete_user):
        """test account deletion fails for non-existent user"""
        mock_get_user.return_value = None
        
        success, message = delete_account("nosuchuser", "password123")
        
        assert success is False
        assert "user not found" in message
        mock_delete_user.assert_not_called()
    
    @patch('src.auth.delete_user')
    @patch('src.auth.get_user_by_username')
    def test_delete_account_default_accounts_protected(self, mock_get_user, mock_delete_user):
        """test cannot delete default accounts"""
        success, message = delete_account("manager", "password123")
        
        assert success is False
        assert "cannot delete default accounts" in message
        mock_get_user.assert_not_called()
        mock_delete_user.assert_not_called()
        
        success, message = delete_account("clerk", "password123")
        
        assert success is False
        assert "cannot delete default accounts" in message
    
    @patch('src.auth.delete_user')
    @patch('src.auth.get_user_by_username')
    def test_delete_account_empty_username(self, mock_get_user, mock_delete_user):
        """test account deletion fails with empty username"""
        success, message = delete_account("", "password123")

        assert success is False
        assert "username is required" in message
        mock_get_user.assert_not_called()
        mock_delete_user.assert_not_called()


# Integration Tests
@pytest.fixture
def setup_test_database(tmp_path):
    """
    pytest fixture. runs before each test function.
    creates fresh, temporary database for each test.
    """
    # use temporary file for database
    db_path = tmp_path / "test_inventory.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # create necessary 'users' table
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    );
    """)

    # add default users with known passwords
    manager_pass = bcrypt.hashpw(b"manager123", bcrypt.gensalt())
    clerk_pass = bcrypt.hashpw(b"clerk123", bcrypt.gensalt())

    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                   ("manager", manager_pass.decode('utf-8'), "Manager"))
    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                   ("clerk", clerk_pass.decode('utf-8'), "Clerk"))

    conn.commit()
    conn.close()

    # return path to test database
    return str(db_path)


class TestLoginIntegration:
    """integration tests for login with real database"""

    def test_login_integration_success_manager(self, setup_test_database, monkeypatch):
        """tests full login flow for manager against real test database"""
        # override db_name in database_manager module to use test db
        monkeypatch.setattr('src.database_manager.DB_NAME', setup_test_database)

        # call login function with correct credentials
        role = login("manager", "manager123")

        # check result
        assert role == "Manager"

    def test_login_integration_success_clerk(self, setup_test_database, monkeypatch):
        """tests full login flow for clerk against real test database"""
        monkeypatch.setattr('src.database_manager.DB_NAME', setup_test_database)

        role = login("clerk", "clerk123")

        assert role == "Clerk"

    def test_login_integration_failure_wrong_password(self, setup_test_database, monkeypatch):
        """tests login flow with wrong password"""
        monkeypatch.setattr('src.database_manager.DB_NAME', setup_test_database)

        role = login("manager", "wrongpassword")

        assert role is None

    def test_login_integration_failure_user_not_found(self, setup_test_database, monkeypatch):
        """tests login flow with user that does not exist"""
        monkeypatch.setattr('src.database_manager.DB_NAME', setup_test_database)

        role = login("nosuchuser", "password")

        assert role is None
