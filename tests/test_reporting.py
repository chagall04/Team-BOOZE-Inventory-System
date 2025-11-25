# tests/test_reporting.py
# scrum-14 to scrum-16: reporting tests
# owned by: charlie gallagher

"""Tests for reporting functionality including low stock reports."""

import json
import os
import tempfile
from unittest.mock import patch

from src.reporting import (
    generate_low_stock_report,
    format_currency,
    view_total_inventory_value,
    export_to_csv,
    export_to_json,
    is_protected_filename,
    export_report,
    PROTECTED_FILES
)


class TestLowStockReport:
    """test class for low stock report generation (SCRUM-14, SCRUM-57)"""

    @patch('src.reporting.get_low_stock_report')
    def test_generate_low_stock_report_with_products_below_threshold(self, mock_get_low_stock):
        """test report generation with products below threshold"""
        mock_products = [
            {
                "id": 1,
                "name": "Bushmills Original",
                "brand": "Bushmills",
                "quantity_on_hand": 5,
                "price": 29.00
            },
            {
                "id": 2,
                "name": "Dingle Gin",
                "brand": "Dingle",
                "quantity_on_hand": 10,
                "price": 38.00
            }
        ]
        mock_get_low_stock.return_value = mock_products
        
        report = generate_low_stock_report(threshold=20)
        
        assert report is not None
        assert isinstance(report, str)
        assert "LOW STOCK REPORT" in report
        assert "Threshold: 20" in report
        assert "Bushmills Original" in report
        assert "Dingle Gin" in report
        assert "Total products below threshold: 2" in report
        assert "Reorder" in report
        mock_get_low_stock.assert_called_once_with(20)

    @patch('src.reporting.get_low_stock_report')
    def test_generate_low_stock_report_no_products_below_threshold(self, mock_get_low_stock):
        """test report when no products are below threshold"""
        mock_get_low_stock.return_value = []
        
        report = generate_low_stock_report(threshold=20)
        
        assert report is not None
        assert isinstance(report, str)
        assert "LOW STOCK REPORT" in report
        assert "Good news!" in report
        assert "above the reorder threshold" in report
        mock_get_low_stock.assert_called_once_with(20)

    @patch('src.reporting.get_low_stock_report')
    def test_generate_low_stock_report_default_threshold(self, mock_get_low_stock):
        """test that default threshold is 20 units"""
        mock_get_low_stock.return_value = []
        
        report = generate_low_stock_report()
        
        mock_get_low_stock.assert_called_once_with(20)
        assert "Threshold: 20" in report

    @patch('src.reporting.get_low_stock_report')
    def test_generate_low_stock_report_custom_threshold(self, mock_get_low_stock):
        """test report with custom threshold value"""
        mock_get_low_stock.return_value = []
        
        report = generate_low_stock_report(threshold=50)
        
        mock_get_low_stock.assert_called_once_with(50)
        assert "Threshold: 50" in report

    @patch('src.reporting.get_low_stock_report')
    def test_generate_low_stock_report_formatting(self, mock_get_low_stock):
        """test report formatting and layout"""
        mock_products = [
            {
                "id": 1,
                "name": "Jameson Original",
                "brand": "Jameson",
                "quantity_on_hand": 3,
                "price": 30.50
            }
        ]
        mock_get_low_stock.return_value = mock_products
        
        report = generate_low_stock_report(threshold=20)
        
        # verify report structure
        assert "=" * 70 in report
        assert "-" * 70 in report
        assert "ID" in report
        assert "Product Name" in report
        assert "Brand" in report
        assert "Stock" in report
        assert "Price" in report

    @patch('src.reporting.get_low_stock_report')
    def test_generate_low_stock_report_product_data_alignment(self, mock_get_low_stock):
        """test that product data is correctly aligned in report"""
        mock_products = [
            {
                "id": 5,
                "name": "Powers Gold Label",
                "brand": "Powers",
                "quantity_on_hand": 15,
                "price": 32.00
            }
        ]
        mock_get_low_stock.return_value = mock_products
        
        report = generate_low_stock_report(threshold=20)
        
        # verify product ID is in report
        assert "5" in report
        # verify product name is in report
        assert "Powers Gold Label" in report
        # verify brand is in report
        assert "Powers" in report
        # verify quantity is in report
        assert "15" in report
        # verify price is in report
        assert "32.00" in report

    @patch('src.reporting.get_low_stock_report')
    def test_generate_low_stock_report_truncates_long_names(self, mock_get_low_stock):
        """test that product names longer than 24 chars are truncated"""
        mock_products = [
            {
                "id": 1,
                "name": "This is an extremely long product name that exceeds limits",
                "brand": "BrandNameHere",
                "quantity_on_hand": 5,
                "price": 20.00
            }
        ]
        mock_get_low_stock.return_value = mock_products
        
        report = generate_low_stock_report(threshold=20)
        
        # report should exist and not crash due to long name
        assert report is not None
        assert isinstance(report, str)
        # truncated name should be in report
        assert "This is an extremely lon" in report

    @patch('src.reporting.get_low_stock_report')
    def test_generate_low_stock_report_null_brand_handling(self, mock_get_low_stock):
        """test handling of products with null brand"""
        mock_products = [
            {
                "id": 1,
                "name": "Generic Spirits",
                "brand": None,
                "quantity_on_hand": 8,
                "price": 15.00
            }
        ]
        mock_get_low_stock.return_value = mock_products
        
        report = generate_low_stock_report(threshold=20)
        
        # report should handle None brand gracefully
        assert report is not None
        assert "N/A" in report or "None" not in report

    @patch('src.reporting.get_low_stock_report')
    def test_generate_low_stock_report_sorted_by_stock_ascending(self, mock_get_low_stock):
        """test that products are listed in order of stock level (ascending)"""
        mock_products = [
            {
                "id": 1,
                "name": "Product A",
                "brand": "Brand A",
                "quantity_on_hand": 2,  # lowest
                "price": 10.00
            },
            {
                "id": 2,
                "name": "Product B",
                "brand": "Brand B",
                "quantity_on_hand": 8,  # middle
                "price": 20.00
            },
            {
                "id": 3,
                "name": "Product C",
                "brand": "Brand C",
                "quantity_on_hand": 15,  # highest
                "price": 30.00
            }
        ]
        mock_get_low_stock.return_value = mock_products
        
        report = generate_low_stock_report(threshold=20)
        
        # verify order in report (Product A should appear before Product B, etc.)
        pos_a = report.find("Product A")
        pos_b = report.find("Product B")
        pos_c = report.find("Product C")
        
        assert pos_a < pos_b < pos_c

    @patch('src.reporting.get_low_stock_report')
    def test_generate_low_stock_report_with_zero_stock(self, mock_get_low_stock):
        """test report generation for product with zero stock"""
        mock_products = [
            {
                "id": 1,
                "name": "Out of Stock Item",
                "brand": "Test Brand",
                "quantity_on_hand": 0,
                "price": 25.00
            }
        ]
        mock_get_low_stock.return_value = mock_products
        
        report = generate_low_stock_report(threshold=20)
        
        assert "0" in report
        assert "Out of Stock Item" in report
        assert "Total products below threshold: 1" in report

    @patch('src.reporting.get_low_stock_report')
    def test_generate_low_stock_report_large_threshold(self, mock_get_low_stock):
        """test report with large threshold value"""
        mock_products = [
            {"id": i, "name": f"Product {i}", "brand": "Brand", 
             "quantity_on_hand": i*10, "price": i*5}
            for i in range(1, 6)
        ]
        mock_get_low_stock.return_value = mock_products
        
        report = generate_low_stock_report(threshold=1000)
        
        assert "Threshold: 1000" in report
        assert "Total products below threshold: 5" in report

    @patch('src.reporting.get_low_stock_report')
    def test_generate_low_stock_report_price_formatting(self, mock_get_low_stock):
        """test that prices are formatted with EUR symbol and decimals"""
        mock_products = [
            {
                "id": 1,
                "name": "Premium Spirits",
                "brand": "Premium",
                "quantity_on_hand": 5,
                "price": 99.99
            }
        ]
        mock_get_low_stock.return_value = mock_products
        
        report = generate_low_stock_report(threshold=20)
        
        # verify price is formatted with euro symbol
        assert "€" in report
        assert "99.99" in report


# Format Currency Tests
class TestFormatCurrency:
    """test class for format_currency utility function"""
    
    def test_format_currency_basic_value(self):
        """test formatting a basic decimal value"""
        result = format_currency(1250.00)
        
        assert result == "€1,250.00"
    
    def test_format_currency_zero(self):
        """test formatting zero value"""
        result = format_currency(0.00)
        
        assert result == "€0.00"
    
    def test_format_currency_small_value(self):
        """test formatting small decimal value"""
        result = format_currency(5.99)
        
        assert result == "€5.99"
    
    def test_format_currency_large_value(self):
        """test formatting large value with thousands separator"""
        result = format_currency(123456.78)
        
        assert result == "€123,456.78"
    
    def test_format_currency_integer_value(self):
        """test formatting integer value (should show .00)"""
        result = format_currency(100)
        
        assert result == "€100.00"
    
    def test_format_currency_rounds_to_two_decimals(self):
        """test that value is formatted with exactly two decimal places"""
        result = format_currency(99.999)
        
        # should round to 2 decimals
        assert result == "€100.00"
    
    def test_format_currency_handles_float(self):
        """test formatting float value"""
        result = format_currency(45.5)
        
        assert result == "€45.50"
    
    def test_format_currency_very_large_value(self):
        """test formatting very large value"""
        result = format_currency(9999999.99)
        
        assert result == "€9,999,999.99"
    
    def test_format_currency_one_cent(self):
        """test formatting very small value"""
        result = format_currency(0.01)
        
        assert result == "€0.01"
    
    def test_format_currency_has_euro_symbol(self):
        """test that all formatted values have euro symbol"""
        result = format_currency(100.00)
        
        assert result.startswith("€")
    
    def test_format_currency_negative_value(self):
        """test formatting negative value"""
        result = format_currency(-50.00)
        
        assert result == "€-50.00"


# View Total Inventory Value Tests
class TestViewTotalInventoryValue:
    """test class for view_total_inventory_value report function"""
    
    @patch('src.reporting.get_total_inventory_value')
    @patch('builtins.print')
    def test_view_total_inventory_value_displays_report(self, mock_print, mock_get_total):
        """test that report is displayed to user"""
        mock_get_total.return_value = 5000.00
        
        view_total_inventory_value()
        
        # verify print was called
        assert mock_print.call_count > 0
        mock_get_total.assert_called_once()
    
    @patch('src.reporting.get_total_inventory_value')
    @patch('builtins.print')
    def test_view_total_inventory_value_shows_formatted_value(self, mock_print, mock_get_total):
        """test that formatted currency value is in report"""
        mock_get_total.return_value = 1250.00
        
        view_total_inventory_value()
        
        # get the printed output
        printed_output = ""
        for call in mock_print.call_args_list:
            printed_output += str(call[0][0]) if call[0] else ""
        
        assert "€1,250.00" in printed_output
        assert "TOTAL INVENTORY VALUE REPORT" in printed_output
    
    @patch('src.reporting.get_total_inventory_value')
    @patch('builtins.print')
    def test_view_total_inventory_value_empty_database(self, mock_print, mock_get_total):
        """test report when database is empty"""
        mock_get_total.return_value = 0.00
        
        view_total_inventory_value()
        
        # get the printed output
        printed_output = ""
        for call in mock_print.call_args_list:
            printed_output += str(call[0][0]) if call[0] else ""
        
        assert "€0.00" in printed_output
    
    @patch('src.reporting.get_total_inventory_value')
    @patch('builtins.print')
    def test_view_total_inventory_value_large_value(self, mock_print, mock_get_total):
        """test report with large inventory value"""
        mock_get_total.return_value = 999999.99
        
        view_total_inventory_value()
        
        # get the printed output
        printed_output = ""
        for call in mock_print.call_args_list:
            printed_output += str(call[0][0]) if call[0] else ""
        
        assert "€999,999.99" in printed_output
    
    @patch('src.reporting.get_total_inventory_value')
    @patch('builtins.print')
    def test_view_total_inventory_value_report_format(self, mock_print, mock_get_total):
        """test that report has proper formatting with headers and dividers"""
        mock_get_total.return_value = 2500.50
        
        view_total_inventory_value()
        
        # get the printed output
        printed_output = ""
        for call in mock_print.call_args_list:
            printed_output += str(call[0][0]) if call[0] else ""
        
        # verify report structure
        assert "=" * 70 in printed_output
        assert "TOTAL INVENTORY VALUE REPORT" in printed_output
        assert "Total value of all products in stock:" in printed_output
    
    @patch('src.reporting.get_total_inventory_value')
    @patch('builtins.print')
    def test_view_total_inventory_value_calls_database(self, mock_print, mock_get_total):
        """test that function calls database to get total value"""
        mock_get_total.return_value = 3000.00
        
        view_total_inventory_value()
        
        mock_get_total.assert_called_once()
    
    @patch('src.reporting.get_total_inventory_value')
    @patch('builtins.print')
    def test_view_total_inventory_value_decimal_precision(self, mock_print, mock_get_total):
        """test that decimal values are displayed correctly"""
        mock_get_total.return_value = 1234.56
        
        view_total_inventory_value()
        
        # get the printed output
        printed_output = ""
        for call in mock_print.call_args_list:
            printed_output += str(call[0][0]) if call[0] else ""
        
        assert "€1,234.56" in printed_output


# scrum-16: export to csv tests
class TestExportToCsv:
    """test class for export_to_csv utility function"""
    
    def test_export_to_csv_success(self):
        """test successful csv export with valid data"""
        data = [
            {"id": 1, "name": "Product A", "price": 10.00},
            {"id": 2, "name": "Product B", "price": 20.00}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            success, message = export_to_csv(data, tmp_path)
            
            assert success is True
            assert "Successfully exported" in message
            assert tmp_path in message
            
            # verify file contents
            with open(tmp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "id,name,price" in content
                assert "Product A" in content
                assert "Product B" in content
        finally:
            os.unlink(tmp_path)
    
    def test_export_to_csv_empty_data(self):
        """test csv export with empty data returns error"""
        data = []
        
        success, message = export_to_csv(data, "test.csv")
        
        assert success is False
        assert "No data to export" in message
    
    def test_export_to_csv_single_record(self):
        """test csv export with single record"""
        data = [{"id": 1, "name": "Single Product", "quantity": 50}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            success, message = export_to_csv(data, tmp_path)
            
            assert success is True
            
            with open(tmp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Single Product" in content
        finally:
            os.unlink(tmp_path)
    
    def test_export_to_csv_special_characters(self):
        """test csv export handles special characters"""
        data = [{"id": 1, "name": "Café Latte, Special", "price": 5.50}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            success, message = export_to_csv(data, tmp_path)
            
            assert success is True
            
            with open(tmp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Café" in content
        finally:
            os.unlink(tmp_path)
    
    def test_export_to_csv_file_write_error(self):
        """test csv export handles file write errors"""
        data = [{"id": 1, "name": "Test"}]
        
        # use invalid path to trigger error
        invalid_path = "/nonexistent/directory/test.csv"
        
        success, message = export_to_csv(data, invalid_path)
        
        assert success is False
        assert "Failed to write file" in message


# scrum-16: export to json tests
class TestExportToJson:
    """test class for export_to_json utility function"""
    
    def test_export_to_json_success(self):
        """test successful json export with valid data"""
        data = [
            {"id": 1, "name": "Product A", "price": 10.00},
            {"id": 2, "name": "Product B", "price": 20.00}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            success, message = export_to_json(data, tmp_path)
            
            assert success is True
            assert "Successfully exported" in message
            
            # verify file contents are valid json
            with open(tmp_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                assert len(loaded) == 2
                assert loaded[0]["name"] == "Product A"
        finally:
            os.unlink(tmp_path)
    
    def test_export_to_json_empty_list(self):
        """test json export with empty list"""
        data = []
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            success, message = export_to_json(data, tmp_path)
            
            assert success is True
            
            with open(tmp_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                assert loaded == []
        finally:
            os.unlink(tmp_path)
    
    def test_export_to_json_indentation(self):
        """test json export has proper indentation"""
        data = [{"id": 1, "name": "Test"}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            success, message = export_to_json(data, tmp_path)
            
            assert success is True
            
            with open(tmp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # indented json has newlines
                assert '\n' in content
                # should have 4 space indentation
                assert '    ' in content
        finally:
            os.unlink(tmp_path)
    
    def test_export_to_json_file_write_error(self):
        """test json export handles file write errors"""
        data = [{"id": 1, "name": "Test"}]
        
        # use invalid path to trigger error
        invalid_path = "/nonexistent/directory/test.json"
        
        success, message = export_to_json(data, invalid_path)
        
        assert success is False
        assert "Failed to write file" in message
    
    def test_export_to_json_nested_data(self):
        """test json export handles nested data structures"""
        data = {
            "report": "inventory",
            "items": [
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2"}
            ],
            "total": 2
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            success, message = export_to_json(data, tmp_path)
            
            assert success is True
            
            with open(tmp_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                assert loaded["total"] == 2
        finally:
            os.unlink(tmp_path)
    
    def test_export_to_json_non_serializable_data(self):
        """test json export handles non-serializable data"""
        # sets are not json serializable
        data = {"items": {1, 2, 3}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            success, message = export_to_json(data, tmp_path)
            
            assert success is False
            assert "Failed to serialize data" in message
        finally:
            # clean up if file was partially created
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


# scrum-16: protected filename tests
class TestIsProtectedFilename:
    """test class for is_protected_filename validation"""
    
    def test_is_protected_filename_inventory_db(self):
        """test inventory.db is protected"""
        assert is_protected_filename("inventory.db") is True
    
    def test_is_protected_filename_main_py(self):
        """test main.py is protected"""
        assert is_protected_filename("main.py") is True
    
    def test_is_protected_filename_app_py(self):
        """test app.py is protected"""
        assert is_protected_filename("app.py") is True
    
    def test_is_protected_filename_reporting_py(self):
        """test reporting.py is protected"""
        assert is_protected_filename("reporting.py") is True
    
    def test_is_protected_filename_with_path(self):
        """test protection works with full paths"""
        assert is_protected_filename("/path/to/inventory.db") is True
        assert is_protected_filename("src/app.py") is True
    
    def test_is_protected_filename_case_insensitive(self):
        """test protection is case insensitive"""
        assert is_protected_filename("INVENTORY.DB") is True
        assert is_protected_filename("Main.py") is True
    
    def test_is_protected_filename_valid_names(self):
        """test valid filenames are not protected"""
        assert is_protected_filename("report.csv") is False
        assert is_protected_filename("export.json") is False
        assert is_protected_filename("my_data.csv") is False
    
    def test_is_protected_filename_similar_names(self):
        """test similar but different names are not protected"""
        assert is_protected_filename("inventory_report.csv") is False
        assert is_protected_filename("app_backup.py") is False
    
    def test_protected_files_list_contents(self):
        """test protected files list contains expected files"""
        assert "inventory.db" in PROTECTED_FILES
        assert "main.py" in PROTECTED_FILES
        assert "app.py" in PROTECTED_FILES
        assert "__init__.py" in PROTECTED_FILES


# scrum-16: export report orchestration tests
class TestExportReport:
    """test class for main export_report function"""
    
    @patch('src.reporting.get_low_stock_report')
    @patch('src.reporting.export_to_csv')
    def test_export_report_low_stock_csv(self, mock_csv, mock_get_low_stock):
        """test export low stock report to csv"""
        mock_get_low_stock.return_value = [{"id": 1, "name": "Test"}]
        mock_csv.return_value = (True, "Success")
        
        success, message = export_report('low_stock', 'csv', 'report.csv')
        
        assert success is True
        mock_get_low_stock.assert_called_once()
        mock_csv.assert_called_once()
    
    @patch('src.reporting.get_low_stock_report')
    @patch('src.reporting.export_to_json')
    def test_export_report_low_stock_json(self, mock_json, mock_get_low_stock):
        """test export low stock report to json"""
        mock_get_low_stock.return_value = [{"id": 1, "name": "Test"}]
        mock_json.return_value = (True, "Success")
        
        success, message = export_report('low_stock', 'json', 'report.json')
        
        assert success is True
        mock_get_low_stock.assert_called_once()
        mock_json.assert_called_once()
    
    @patch('src.reporting.get_all_products')
    @patch('src.reporting.export_to_csv')
    def test_export_report_inventory_csv(self, mock_csv, mock_get_all):
        """test export inventory report to csv"""
        mock_get_all.return_value = [{"id": 1, "name": "Test"}]
        mock_csv.return_value = (True, "Success")
        
        success, message = export_report('inventory', 'csv', 'report.csv')
        
        assert success is True
        mock_get_all.assert_called_once()
    
    @patch('src.reporting.get_all_products')
    @patch('src.reporting.export_to_json')
    def test_export_report_inventory_json(self, mock_json, mock_get_all):
        """test export inventory report to json"""
        mock_get_all.return_value = [{"id": 1, "name": "Test"}]
        mock_json.return_value = (True, "Success")
        
        success, message = export_report('inventory', 'json', 'report.json')
        
        assert success is True
        mock_get_all.assert_called_once()
    
    def test_export_report_protected_filename(self):
        """test export fails for protected filename"""
        success, message = export_report('low_stock', 'csv', 'inventory.db')
        
        assert success is False
        assert "protected file" in message.lower()
    
    def test_export_report_invalid_report_type(self):
        """test export fails for invalid report type"""
        success, message = export_report('invalid_type', 'csv', 'report.csv')
        
        assert success is False
        assert "Unknown report type" in message
    
    @patch('src.reporting.get_low_stock_report')
    def test_export_report_invalid_format(self, mock_get_low_stock):
        """test export fails for invalid file format"""
        mock_get_low_stock.return_value = [{"id": 1}]
        
        success, message = export_report('low_stock', 'invalid', 'report.txt')
        
        assert success is False
        assert "Unknown file format" in message
    
    @patch('src.reporting.get_low_stock_report')
    @patch('src.reporting.export_to_csv')
    def test_export_report_csv_failure(self, mock_csv, mock_get_low_stock):
        """test export handles csv failure"""
        mock_get_low_stock.return_value = [{"id": 1}]
        mock_csv.return_value = (False, "Write error")
        
        success, message = export_report('low_stock', 'csv', 'report.csv')
        
        assert success is False
        assert "Write error" in message
