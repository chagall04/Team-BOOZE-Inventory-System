# tests/test_app.py
# scrum-17 to scrum-22: app tests
# owned by: charlie gallagher

import pytest
from unittest.mock import patch, MagicMock
from src.app import main, show_manager_menu, show_clerk_menu


class TestMain:
    """test class for main application entry point"""
    
    @patch('src.app.login')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_manager_login_success(self, mock_print, mock_input, mock_login):
        """test successful manager login flow"""
        mock_input.side_effect = ["manager", "manager123", "0"]
        mock_login.return_value = "Manager"
        
        main()
        
        mock_login.assert_called_once_with("manager", "manager123")
    
    @patch('src.app.login')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_clerk_login_success(self, mock_print, mock_input, mock_login):
        """test successful clerk login flow"""
        mock_input.side_effect = ["clerk", "clerk123", "0"]
        mock_login.return_value = "Clerk"
        
        main()
        
        mock_login.assert_called_once_with("clerk", "clerk123")
    
    @patch('src.app.login')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_login_failure(self, mock_print, mock_input, mock_login):
        """test failed login shows access denied"""
        mock_input.side_effect = ["baduser", "badpass"]
        mock_login.return_value = None
        
        main()
        
        mock_login.assert_called_once_with("baduser", "badpass")


class TestManagerMenu:
    """test class for manager menu"""
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_manager_menu_logout(self, mock_print, mock_input):
        """test manager can logout"""
        mock_input.return_value = "0"
        
        show_manager_menu()
        
        # verify logout was called
        mock_input.assert_called()
    
    @patch('src.app.add_new_product')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_manager_menu_add_product(self, mock_print, mock_input, mock_add_product):
        """test manager can access add product"""
        mock_input.side_effect = ["1", "0"]
        
        show_manager_menu()
        
        mock_add_product.assert_called_once()


class TestClerkMenu:
    """test class for clerk menu"""
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_clerk_menu_logout(self, mock_print, mock_input):
        """test clerk can logout"""
        mock_input.return_value = "0"
        
        show_clerk_menu()
        
        mock_input.assert_called()
