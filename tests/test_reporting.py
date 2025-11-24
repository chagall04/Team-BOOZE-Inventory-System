# tests/test_reporting.py
# scrum-14 to scrum-16: reporting tests
# owned by: charlie gallagher

"""Tests for reporting functionality including low stock reports."""

from unittest.mock import patch
from src.reporting import generate_low_stock_report, format_currency, view_total_inventory_value


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

