# tests/test_app.py
# scrum-17 to scrum-22: app tests
# owned by: charlie gallagher

"""Tests for main application entry point and menu systems."""

from unittest.mock import patch
from src.app import (
    main,
    show_manager_menu,
    show_clerk_menu,
    show_account_menu,
    handle_create_account,
    handle_delete_account,
    handle_export_report,
    handle_view_low_stock_report
)



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
    @patch('src.app.getpass')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_create_account_success(self, mock_print, mock_input, mock_getpass, mock_create):
        """test successful account creation"""
        mock_input.side_effect = ["newuser", "Clerk"]
        mock_getpass.return_value = "password123"
        mock_create.return_value = (True, "account created successfully")
        
        result = handle_create_account()
        
        assert result is True
        mock_create.assert_called_once_with("newuser", "password123", "Clerk")
    
    @patch('src.app.create_account')
    @patch('src.app.getpass')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_create_account_failure(self, mock_print, mock_input, mock_getpass, mock_create):
        """test failed account creation"""
        mock_input.side_effect = ["ab", "Clerk"]
        mock_getpass.return_value = "12345"
        mock_create.return_value = (False, "username must be at least 3 characters")
        
        result = handle_create_account()
        
        assert result is False


class TestHandleDeleteAccount:
    """test class for delete account handler"""
    
    @patch('src.app.delete_account')
    @patch('src.app.getpass')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_delete_account_success(self, mock_print, mock_input, mock_getpass, mock_delete):
        """test successful account deletion with confirmation"""
        mock_input.side_effect = ["testuser", "yes"]
        mock_getpass.return_value = "password123"
        mock_delete.return_value = (True, "user deleted")
        
        result = handle_delete_account()
        
        assert result is True
        mock_delete.assert_called_once_with("testuser", "password123")
    
    @patch('src.app.delete_account')
    @patch('src.app.getpass')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_delete_account_failure(self, mock_print, mock_input, mock_getpass, mock_delete):
        """test failed account deletion"""
        mock_input.side_effect = ["testuser", "yes"]
        mock_getpass.return_value = "wrongpass"
        mock_delete.return_value = (False, "incorrect password")
        
        result = handle_delete_account()
        
        assert result is False
    
    @patch('src.app.delete_account')
    @patch('src.app.getpass')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_delete_account_cancelled(self, mock_print, mock_input, mock_getpass, mock_delete):
        """test account deletion cancelled by user"""
        mock_input.side_effect = ["testuser", "no"]
        mock_getpass.return_value = "password123"
        
        result = handle_delete_account()
        
        assert result is False
        mock_delete.assert_not_called()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_delete_account_quit_username(self, mock_print, mock_input):
        """test quitting at username prompt"""
        mock_input.side_effect = ["Q"]
        
        result = handle_delete_account()
        
        assert result is False


class TestMain:
    """test class for main application entry point"""
    
    @patch('src.app.confirm_action', return_value=True)
    @patch('src.app.show_account_menu')
    @patch('src.app.login')
    @patch('src.app.getpass')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_manager_login_success(self, mock_print, mock_input, mock_getpass, mock_login, mock_menu, mock_confirm):
        """test successful manager login flow"""
        mock_menu.side_effect = ["1", "0"]
        mock_input.side_effect = ["manager", "0"]
        mock_getpass.return_value = "manager123"
        mock_login.return_value = "Manager"
        
        main()
        
        mock_login.assert_called_once_with("manager", "manager123")
    
    @patch('src.app.confirm_action', return_value=True)
    @patch('src.app.show_account_menu')
    @patch('src.app.login')
    @patch('src.app.getpass')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_clerk_login_success(self, mock_print, mock_input, mock_getpass, mock_login, mock_menu, mock_confirm):
        """test successful clerk login flow"""
        mock_menu.side_effect = ["1", "0"]
        mock_input.side_effect = ["clerk", "0"]
        mock_getpass.return_value = "clerk123"
        mock_login.return_value = "Clerk"
        
        main()
        
        mock_login.assert_called_once_with("clerk", "clerk123")
    
    @patch('src.app.confirm_action', return_value=True)
    @patch('src.app.show_account_menu')
    @patch('src.app.login')
    @patch('src.app.getpass')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_login_failure(self, mock_print, mock_input, mock_getpass, mock_login, mock_menu, mock_confirm):
        """test failed login shows access denied"""
        mock_menu.side_effect = ["1", "0"]
        mock_input.side_effect = ["baduser"]
        mock_getpass.return_value = "badpass"
        mock_login.return_value = None
        
        main()
        
        mock_login.assert_called_once_with("baduser", "badpass")
    
    @patch('src.app.confirm_action', return_value=True)
    @patch('src.app.show_account_menu')
    @patch('src.app.handle_create_account')
    @patch('builtins.print')
    def test_main_create_account_flow(self, mock_print, mock_handle_create, mock_menu, mock_confirm):
        """test create account menu option"""
        mock_menu.side_effect = ["2", "0"]
        mock_handle_create.return_value = True
        
        main()
        
        mock_handle_create.assert_called_once()
    
    @patch('src.app.confirm_action', return_value=True)
    @patch('src.app.show_account_menu')
    @patch('src.app.handle_delete_account')
    @patch('builtins.print')
    def test_main_delete_account_flow(self, mock_print, mock_handle_delete, mock_menu, mock_confirm):
        """test delete account menu option"""
        mock_menu.side_effect = ["3", "0"]
        mock_handle_delete.return_value = True
        
        main()
        
        mock_handle_delete.assert_called_once()
    
    @patch('src.app.confirm_action', return_value=True)
    @patch('src.app.show_account_menu')
    @patch('builtins.print')
    def test_main_invalid_menu_choice(self, mock_print, mock_menu, mock_confirm):
        """test invalid menu choice"""
        mock_menu.side_effect = ["9", "0"]
        
        main()
        
        # verify it loops back without crashing
        assert mock_menu.call_count == 2
    
    @patch('src.app.confirm_action')
    @patch('src.app.show_account_menu')
    @patch('builtins.print')
    def test_main_exit_cancelled(self, mock_print, mock_menu, mock_confirm):
        """test exit confirmation cancelled returns to menu"""
        mock_menu.side_effect = ["0", "0"]
        mock_confirm.side_effect = [False, True]  # first cancel, then confirm
        
        main()
        
        # confirm_action called twice (cancelled then accepted)
        assert mock_confirm.call_count == 2


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
    
    @patch('src.app.generate_low_stock_report')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_manager_menu_view_inventory_report(self, mock_print, mock_input, mock_report):
        """test manager can access inventory report (SCRUM-14, SCRUM-58)"""
        mock_input.side_effect = ["4", "20", "0"]
        mock_report.return_value = "Low Stock Report"
        
        show_manager_menu()
        
        mock_input.assert_called()
        mock_report.assert_called_once_with(20)
    
    @patch('src.app.generate_low_stock_report')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_manager_menu_view_inventory_report_invalid_threshold(self, mock_print, mock_input, mock_report):
        """test manager menu handles invalid threshold input (SCRUM-14, SCRUM-58)"""
        mock_input.side_effect = ["4", "invalid", "0"]
        mock_report.return_value = "Low Stock Report"
        
        show_manager_menu()
        
        mock_input.assert_called()
        # should call with default threshold of 20 due to ValueError
        mock_report.assert_called_once_with(20)
    
    @patch('src.app.view_sales_history')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_manager_menu_view_sales_history(self, mock_print, mock_input, mock_view_history):
        """test manager can access sales history (scrum-15)"""
        mock_input.side_effect = ["6", "0"]
        mock_view_history.return_value = True
        
        show_manager_menu()
        
        mock_view_history.assert_called_once()
        mock_input.assert_called()
    
    @patch('src.app.view_total_inventory_value')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_manager_menu_view_total_inventory_value(self, mock_print, mock_input, mock_view_total):
        """test manager can access total inventory value report"""
        mock_input.side_effect = ["5", "0"]
        
        show_manager_menu()
        
        mock_view_total.assert_called_once()
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
    
    @patch('src.app.receive_new_stock')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_clerk_menu_receive_stock(self, mock_print, mock_input, mock_receive_stock):
        """test clerk can access receive stock"""
        mock_input.side_effect = ["2", "0"]
        
        show_clerk_menu()
        
        mock_receive_stock.assert_called_once()
        mock_input.assert_called()
    
    @patch('src.app.view_current_stock')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_clerk_menu_view_stock(self, mock_print, mock_input, mock_view_stock):
        """test clerk can access view stock"""
        mock_input.side_effect = ["3", "0"]
        
        show_clerk_menu()
        
        mock_view_stock.assert_called_once()
        mock_input.assert_called()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_clerk_menu_invalid_choice(self, mock_print, mock_input):
        """test clerk menu handles invalid choice"""
        mock_input.side_effect = ["9", "0"]
        
        show_clerk_menu()
        
        mock_input.assert_called()
    
    @patch('src.app.log_product_loss')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_clerk_menu_log_product_loss(self, mock_print, mock_input, mock_log_loss):
        """test clerk can access log product loss (scrum-10)"""
        mock_input.side_effect = ["5", "0"]
        
        show_clerk_menu()
        
        mock_log_loss.assert_called_once()
        mock_input.assert_called()

    @patch('src.app.view_transaction_details')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_clerk_menu_view_transaction_details(self, mock_print, mock_input, mock_view_txn):
        """test clerk can access view transaction details (scrum-64)"""
        mock_input.side_effect = ["6", "0"]
        
        show_clerk_menu()
        
        mock_view_txn.assert_called_once()
        mock_input.assert_called()

    @patch('src.app.view_last_transaction')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_clerk_menu_view_last_sale(self, mock_print, mock_input, mock_view_last):
        """test clerk can access view last sale (SCRUM-71)"""
        mock_input.side_effect = ["7", "0"]
        
        show_clerk_menu()
        
        mock_view_last.assert_called_once()
        mock_input.assert_called()


class TestManagerMenuTransactionDetails:
    """test class for manager menu transaction details (scrum-64)"""
    
    @patch('src.app.view_transaction_details')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_manager_menu_view_transaction_details(self, mock_print, mock_input, mock_view_txn):
        """test manager can access view transaction details"""
        mock_input.side_effect = ["7", "0"]
        
        show_manager_menu()
        
        mock_view_txn.assert_called_once()
        mock_input.assert_called()


# scrum-16: export report handler tests
class TestHandleExportReport:
    """test class for handle_export_report menu flow"""
    
    @patch('src.app.export_report')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_export_report_low_stock_csv_success(self, mock_print, mock_input, mock_export):
        """test successful low stock csv export"""
        mock_input.side_effect = ["1", "15", "1", "my_report"]  # report, threshold, format, filename
        mock_export.return_value = (True, "Successfully exported to my_report.csv")
        
        result = handle_export_report()
        
        assert result is True
        mock_export.assert_called_once_with('low_stock', 'csv', 'my_report.csv', 15)
    
    @patch('src.app.export_report')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_export_report_low_stock_json_success(self, mock_print, mock_input, mock_export):
        """test successful low stock json export with default threshold"""
        mock_input.side_effect = ["1", "", "2", "my_report"]  # report, empty threshold (default), format, filename
        mock_export.return_value = (True, "Successfully exported to my_report.json")
        
        result = handle_export_report()
        
        assert result is True
        mock_export.assert_called_once_with('low_stock', 'json', 'my_report.json', 20)
    
    @patch('src.app.export_report')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_export_report_inventory_csv_success(self, mock_print, mock_input, mock_export):
        """test successful inventory csv export"""
        mock_input.side_effect = ["2", "1", "inventory_export"]  # no threshold prompt for inventory
        mock_export.return_value = (True, "Successfully exported")
        
        result = handle_export_report()
        
        assert result is True
        mock_export.assert_called_once_with('inventory', 'csv', 'inventory_export.csv', 20)
    
    @patch('src.app.export_report')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_export_report_inventory_json_success(self, mock_print, mock_input, mock_export):
        """test successful inventory json export"""
        mock_input.side_effect = ["2", "2", "inventory_export"]  # no threshold prompt for inventory
        mock_export.return_value = (True, "Successfully exported")
        
        result = handle_export_report()
        
        assert result is True
        mock_export.assert_called_once_with('inventory', 'json', 'inventory_export.json', 20)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_export_report_invalid_report_choice(self, mock_print, mock_input):
        """test invalid report type choice"""
        mock_input.side_effect = ["9"]
        
        result = handle_export_report()
        
        assert result is False
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_export_report_invalid_format_choice(self, mock_print, mock_input):
        """test invalid format choice"""
        mock_input.side_effect = ["1", "20", "9"]  # report, threshold, invalid format
        
        result = handle_export_report()
        
        assert result is False
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_export_report_empty_filename(self, mock_print, mock_input):
        """test empty filename returns error"""
        mock_input.side_effect = ["1", "20", "1", ""]  # report, threshold, format, empty filename
        
        result = handle_export_report()
        
        assert result is False
    
    @patch('src.app.export_report')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_export_report_export_failure(self, mock_print, mock_input, mock_export):
        """test export failure returns false"""
        mock_input.side_effect = ["1", "20", "1", "report"]  # report, threshold, format, filename
        mock_export.return_value = (False, "No data to export")
        
        result = handle_export_report()
        
        assert result is False
    
    @patch('src.app.export_report')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_export_report_filename_with_extension(self, mock_print, mock_input, mock_export):
        """test filename with extension is not duplicated"""
        mock_input.side_effect = ["1", "20", "1", "report.csv"]  # report, threshold, format, filename
        mock_export.return_value = (True, "Success")
        
        result = handle_export_report()
        
        assert result is True
        mock_export.assert_called_once_with('low_stock', 'csv', 'report.csv', 20)
    
    @patch('src.app.export_report')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_export_report_json_with_extension(self, mock_print, mock_input, mock_export):
        """test json filename with extension is not duplicated"""
        mock_input.side_effect = ["2", "2", "data.json"]  # no threshold for inventory
        mock_export.return_value = (True, "Success")
        
        result = handle_export_report()
        
        assert result is True
        mock_export.assert_called_once_with('inventory', 'json', 'data.json', 20)


class TestManagerMenuExportReport:
    """test class for export report in manager menu (scrum-16)"""
    
    @patch('src.app.handle_export_report')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_manager_menu_export_report(self, mock_print, mock_input, mock_export):
        """test manager can access export report option"""
        mock_input.side_effect = ["8", "0"]
        mock_export.return_value = True
        
        show_manager_menu()
        
        mock_export.assert_called_once()
        mock_input.assert_called()


# scrum-58: view low stock report handler tests
class TestHandleViewLowStockReport:
    """test class for handle_view_low_stock_report function"""
    
    @patch('src.app.generate_low_stock_report')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_view_low_stock_report_with_threshold(self, mock_print, mock_input, mock_report):
        """test low stock report with user-provided threshold"""
        mock_input.return_value = "30"
        mock_report.return_value = "Low Stock Report"
        
        handle_view_low_stock_report()
        
        mock_report.assert_called_once_with(30)
        mock_print.assert_called()
    
    @patch('src.app.generate_low_stock_report')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_view_low_stock_report_default_threshold(self, mock_print, mock_input, mock_report):
        """test low stock report uses default threshold when empty input"""
        mock_input.return_value = ""
        mock_report.return_value = "Low Stock Report"
        
        handle_view_low_stock_report()
        
        mock_report.assert_called_once_with(20)
    
    @patch('src.app.generate_low_stock_report')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_handle_view_low_stock_report_invalid_threshold(self, mock_print, mock_input, mock_report):
        """test low stock report handles invalid threshold"""
        mock_input.return_value = "invalid"
        mock_report.return_value = "Low Stock Report"
        
        handle_view_low_stock_report()
        
        mock_report.assert_called_once_with(20)
