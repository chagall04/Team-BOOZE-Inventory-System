# tests/test_auth.py
import pytest
import bcrypt
from unittest.mock import patch
from src.auth import login

@patch('src.auth.get_user_by_username')
def test_login_success_manager(mock_get_user):
    """
    Tests a successful login for a Manager.
    Mocks the database call.
    """
    # Create a real bcrypt hash for "manager123"
    real_hash = bcrypt.hashpw(b"manager123", bcrypt.gensalt()).decode('utf-8')
    
    # Configure the mock to return a fake manager user
    mock_get_user.return_value = {
        "hash": real_hash,
        "role": "Manager"
    }
    
    # Call the function
    role = login("manager", "manager123")
    
    # Check the result
    assert role == "Manager"

@patch('src.auth.get_user_by_username')
def test_login_success_clerk(mock_get_user):
    """
    Tests a successful login for a Clerk.
    Mocks the database call.
    """
    # Create a real bcrypt hash for "clerk123"
    real_hash = bcrypt.hashpw(b"clerk123", bcrypt.gensalt()).decode('utf-8')
    
    # Configure the mock to return a fake clerk user
    mock_get_user.return_value = {
        "hash": real_hash,
        "role": "Clerk"
    }
    
    role = login("clerk", "clerk123")
    
    assert role == "Clerk"

@patch('src.auth.get_user_by_username')
def test_login_failure_wrong_password(mock_get_user):
    """
    Tests a failed login due to a wrong password.
    Mocks the database call.
    """
    # Create a real bcrypt hash for "manager123"
    real_hash = bcrypt.hashpw(b"manager123", bcrypt.gensalt()).decode('utf-8')
    
    # Configure the mock to return a real user
    mock_get_user.return_value = {
        "hash": real_hash,
        "role": "Manager"
    }
    
    # Call the function with the wrong password
    role = login("manager", "wrongpassword")
    
    # Check the result
    assert role is None

@patch('src.auth.get_user_by_username')
def test_login_failure_user_not_found(mock_get_user):
    """
    Tests a failed login due to a user not existing.
    Mocks the database call.
    """
    # Configure the mock to return None, as if the user wasn't found
    mock_get_user.return_value = None
    
    # Call the function
    role = login("nosuchuser", "password")
    
    # Check the result
    assert role is None