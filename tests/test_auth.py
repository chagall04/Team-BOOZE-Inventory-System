# tests/test_auth.py
# scrum-17 to scrum-22: authentication tests
# owned by: charlie gallagher

import pytest
import bcrypt
from unittest.mock import patch
from src.auth import login


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