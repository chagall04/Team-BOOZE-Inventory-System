# tests/test_app.py
# scrum-17 to scrum-22: app tests
# owned by: charlie gallagher

import pytest
from unittest.mock import patch, MagicMock
from src.app import main, show_manager_menu, show_clerk_menu, show_account_menu, handle_create_account, handle_delete_account


class TestAccountMenu:
    """test class for account menu"""
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_show_account_menu_returns_choice(self, mock_print, mock_input):
        """test account menu returns user choice"""
        mock_input.return_value = "1"
        
        choice = show_account_menu()
        
        assert choice == "1"


class TestHandleCreateAccount:
    """test class for create account handler"""
    
    @patch('src.app.create_account')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_create_account_success(self, mock_print, mock_input, mock_create):
        """test successful account creation"""
        mock_input.side_effect = ["newuser", "password123", "Clerk"]
        mock_create.return_value = (True, "account created successfully")
        
        result = handle_create_account()
        
        assert result is True
        mock_create.assert_called_once_with("newuser", "password123", "Clerk")
    
    @patch('src.app.create_account')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_create_account_failure(self, mock_print, mock_input, mock_create):
        """test failed account creation"""
        mock_input.side_effect = ["ab", "12345", "Clerk"]
        mock_create.return_value = (False, "username must be at least 3 characters")
        
        result = handle_create_account()
        
        assert result is False


class TestHandleDeleteAccount:
    """test class for delete account handler"""
    
    @patch('src.app.delete_account')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_delete_account_success(self, mock_print, mock_input, mock_delete):
        """test successful account deletion"""
        mock_input.side_effect = ["testuser", "password123"]
        mock_delete.return_value = (True, "user deleted")
        
        result = handle_delete_account()
        
        assert result is True
        mock_delete.assert_called_once_with("testuser", "password123")
    
    @patch('src.app.delete_account')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_delete_account_failure(self, mock_print, mock_input, mock_delete):
        """test failed account deletion"""
        mock_input.side_effect = ["testuser", "wrongpass"]
        mock_delete.return_value = (False, "incorrect password")
        
        result = handle_delete_account()
        
        assert result is False


class TestMain:
    """test class for main application entry point"""
    
    @patch('src.app.show_account_menu')
    @patch('src.app.login')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_manager_login_success(self, mock_print, mock_input, mock_login, mock_menu):
        """test successful manager login flow"""
        mock_menu.side_effect = ["1", "0"]
        mock_input.side_effect = ["manager", "manager123", "0"]
        mock_login.return_value = "Manager"
        
        main()
        
        mock_login.assert_called_once_with("manager", "manager123")
    
    @patch('src.app.show_account_menu')
    @patch('src.app.login')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_clerk_login_success(self, mock_print, mock_input, mock_login, mock_menu):
        """test successful clerk login flow"""
        mock_menu.side_effect = ["1", "0"]
        mock_input.side_effect = ["clerk", "clerk123", "0"]
        mock_login.return_value = "Clerk"
        
        main()
        
        mock_login.assert_called_once_with("clerk", "clerk123")
    
    @patch('src.app.show_account_menu')
    @patch('src.app.login')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_login_failure(self, mock_print, mock_input, mock_login, mock_menu):
        """test failed login shows access denied"""
        mock_menu.side_effect = ["1", "0"]
        mock_input.side_effect = ["baduser", "badpass"]
        mock_login.return_value = None
        
        main()
        
        mock_login.assert_called_once_with("baduser", "badpass")
    
    @patch('src.app.show_account_menu')
    @patch('src.app.handle_create_account')
    @patch('builtins.print')
    def test_main_create_account_flow(self, mock_print, mock_handle_create, mock_menu):
        """test create account menu option"""
        mock_menu.side_effect = ["2", "0"]
        mock_handle_create.return_value = True
        
        main()
        
        mock_handle_create.assert_called_once()
    
    @patch('src.app.show_account_menu')
    @patch('src.app.handle_delete_account')
    @patch('builtins.print')
    def test_main_delete_account_flow(self, mock_print, mock_handle_delete, mock_menu):
        """test delete account menu option"""
        mock_menu.side_effect = ["3", "0"]
        mock_handle_delete.return_value = True
        
        main()
        
        mock_handle_delete.assert_called_once()
    
    @patch('src.app.show_account_menu')
    @patch('builtins.print')
    def test_main_invalid_menu_choice(self, mock_print, mock_menu):
        """test invalid menu choice"""
        mock_menu.side_effect = ["9", "0"]
        
        main()
        
        # verify it loops back without crashing
        assert mock_menu.call_count == 2


class TestManagerMenu:
    """test class for manager menu"""
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_manager_menu_logout(self, mock_print, mock_input):
        """test manager can logout"""
        mock_input.return_value = "0"
        
        show_manager_menu()
        
        mock_input.assert_called()
    
    @patch('src.app.add_new_product')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_manager_menu_add_product(self, mock_print, mock_input, mock_add_product):
        """test manager can access add product"""
        mock_input.side_effect = ["1", "0"]
        
        show_manager_menu()
        
        mock_add_product.assert_called_once()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_manager_menu_view_inventory_report(self, mock_print, mock_input):
        """test manager can access inventory report (not yet implemented)"""
        mock_input.side_effect = ["2", "0"]
        
        show_manager_menu()
        
        mock_input.assert_called()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_manager_menu_view_sales_history(self, mock_print, mock_input):
        """test manager can access sales history (not yet implemented)"""
        mock_input.side_effect = ["3", "0"]
        
        show_manager_menu()
        
        mock_input.assert_called()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_manager_menu_invalid_choice(self, mock_print, mock_input):
        """test manager menu handles invalid choice"""
        mock_input.side_effect = ["9", "0"]
        
        show_manager_menu()
        
        mock_input.assert_called()


class TestClerkMenu:
    """test class for clerk menu"""
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_clerk_menu_logout(self, mock_print, mock_input):
        """test clerk can logout"""
        mock_input.return_value = "0"
        
        show_clerk_menu()
        
        mock_input.assert_called()
    
    @patch('src.app.record_sale')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_clerk_menu_record_sale(self, mock_print, mock_input, mock_record_sale):
        """test clerk can access record sale"""
        mock_input.side_effect = ["1", "0"]
        mock_record_sale.return_value = True
        
        show_clerk_menu()
        
        mock_record_sale.assert_called_once()
        mock_input.assert_called()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_clerk_menu_receive_stock(self, mock_print, mock_input):
        """test clerk can access receive stock (not yet implemented)"""
        mock_input.side_effect = ["2", "0"]
        
        show_clerk_menu()
        
        mock_input.assert_called()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_clerk_menu_view_stock(self, mock_print, mock_input):
        """test clerk can access view stock (not yet implemented)"""
        mock_input.side_effect = ["3", "0"]
        
        show_clerk_menu()
        
        mock_input.assert_called()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_clerk_menu_invalid_choice(self, mock_print, mock_input):
        """test clerk menu handles invalid choice"""
        mock_input.side_effect = ["9", "0"]
        
        show_clerk_menu()
        
        mock_input.assert_called()
