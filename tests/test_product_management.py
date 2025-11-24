"""Tests for product management functionality including validation and addition."""

from unittest.mock import patch, MagicMock
import sqlite3
import pytest
from src.product_management import add_new_product, validate_product_data

# Test data for validation scenarios
@pytest.mark.parametrize("test_id, name, brand, type_, price, quantity, abv, volume_ml, expected_valid, error_message", [
    # Test ID 1: Valid data with all fields
    (
        "valid_full",
        "Test Beer", "Test Brand", "Beer", "4.99", "50", "4.5", "500",
        True, None
    ),
    # Test ID 2: Valid data with required fields only
    (
        "valid_required",
        "Test Wine", "Test Brand", "Wine", "15.99", "30", "", "",
        True, None
    ),
    # Test ID 3: Invalid - negative price
    (
        "invalid_price",
        "Test Gin", "Test Brand", "Gin", "-5.99", "20", "", "",
        False, "Price must be non-negative"
    ),
    # Test ID 4: Invalid - missing name
    (
        "invalid_name",
        "", "Test Brand", "Whiskey", "25.99", "40", "", "",
        False, "Product name is required"
    ),
    # Test ID 5: Invalid - ABV over 100
    (
        "invalid_abv",
        "Test Vodka", "Test Brand", "Vodka", "20.99", "30", "101", "",
        False, "ABV must be between 0 and 100"
    )
])
def test_validate_product_data(test_id, name, brand, type_, price, quantity, abv, volume_ml, expected_valid, error_message):
    """Test product data validation with various scenarios"""
    is_valid, errors = validate_product_data(name, brand, type_, price, quantity, abv, volume_ml)
    assert is_valid == expected_valid
    if error_message:
        assert error_message in errors

@pytest.mark.parametrize("optional_fields", [True, False])
def test_add_new_product_success(optional_fields):
    """Test successful product addition with and without optional fields"""
    with patch('builtins.input') as mock_input:
        with patch('src.product_management.insert_product') as mock_insert:
            # Setup mock inputs
            inputs = [
                "Test Product",  # name
                "Test Brand",    # brand
                "Beer",         # type
                "4.99",         # price
                "50"           # quantity
            ]
            if optional_fields:
                inputs.extend(["4.5", "500", "Ireland", "Test description"])
            else:
                inputs.extend(["", "", "", ""])
                
            mock_input.side_effect = inputs
            mock_insert.return_value = (True, 1)
            
            # Execute
            result = add_new_product()

            # Verify
            assert result is True
            mock_insert.assert_called_once()

            # Verify data sent to database
            call_args = mock_insert.call_args[0][0]
            assert call_args['name'] == "Test Product"
            assert call_args['price'] == pytest.approx(4.99, rel=1e-6)
            assert call_args['quantity'] == 50

def test_add_new_product_db_error():
    """Test handling of database errors during product addition"""
    with patch('builtins.input') as mock_input:
        with patch('src.product_management.insert_product') as mock_insert:
            # Setup mocks
            mock_input.side_effect = [
                "Test Product",  # name
                "Test Brand",    # brand
                "Beer",         # type
                "4.99",         # price
                "50",          # quantity
                "",            # abv (optional)
                "",            # volume_ml (optional)
                "",            # origin (optional)
                ""            # description (optional)
            ]
            mock_insert.return_value = (False, "Product name already exists")

            # Execute
            result = add_new_product()

            # Verify
            assert result is False
            mock_insert.assert_called_once()
@pytest.mark.parametrize("test_id,name,brand,type_,price,quantity,abv,volume,expected_valid,expected_error", [
    # Happy paths
    ("valid_full", "Beer X", "Brand Y", "Beer", "5.99", "10", "4.5", "500", True, None),
    ("valid_required", "Beer X", "Brand Y", "Beer", "5.99", "10", None, None, True, None),
    
    # Price validation
    ("invalid_price_negative", "Beer X", "Brand Y", "Beer", "-5.99", "10", None, None, False, "Price must be non-negative"),
    ("invalid_price_text", "Beer X", "Brand Y", "Beer", "abc", "10", None, None, False, "Price must be a valid number"),
    
    # Quantity validation
    ("invalid_quantity_negative", "Beer X", "Brand Y", "Beer", "5.99", "-10", None, None, False, "Initial stock quantity must be non-negative"),
    ("invalid_quantity_text", "Beer X", "Brand Y", "Beer", "5.99", "abc", None, None, False, "Initial stock must be a valid whole number"),
    
    # ABV validation
    ("invalid_abv_over", "Beer X", "Brand Y", "Beer", "5.99", "10", "101", "500", False, "ABV must be between 0 and 100"),
    ("invalid_abv_negative", "Beer X", "Brand Y", "Beer", "5.99", "10", "-5", "500", False, "ABV must be between 0 and 100"),
    
    # Volume validation
    ("invalid_volume_zero", "Beer X", "Brand Y", "Beer", "5.99", "10", "4.5", "0", False, "Volume must be greater than 0"),
    
    # Required field validation
    ("invalid_empty_name", "", "Brand Y", "Beer", "5.99", "10", None, None, False, "Product name is required"),
    ("invalid_whitespace_name", "   ", "Brand Y", "Beer", "5.99", "10", None, None, False, "Product name is required"),
    
    # Edge cases
    ("valid_high_price", "Beer X", "Brand Y", "Beer", "999999.99", "10", None, None, True, None),
    ("valid_high_quantity", "Beer X", "Brand Y", "Beer", "5.99", "999999", None, None, True, None),
    ("valid_max_abv", "Beer X", "Brand Y", "Beer", "5.99", "10", "100", None, True, None),
])
def test_validate_product_data_edge_cases(test_id, name, brand, type_, price, quantity, abv, volume, expected_valid, expected_error):
    """Test product data validation with edge case scenarios"""
    is_valid, errors = validate_product_data(name, brand, type_, price, quantity, abv, volume)
    assert is_valid == expected_valid
    if expected_error:
        assert expected_error in errors
    else:
        assert len(errors) == 0

@pytest.mark.parametrize("test_id,mock_inputs,db_result,expected_success", [
    ("success_full", [
        "Test Beer",    # name
        "Test Brand",   # brand
        "Beer",         # type
        "4.99",        # price
        "50",          # quantity
        "4.5",         # abv
        "500",         # volume_ml
        "Ireland",     # origin
        "Test beer description"  # description
    ], (True, 1), True),
    
    ("success_required_only", [
        "Test Beer",    # name
        "Test Brand",   # brand
        "Beer",         # type
        "4.99",        # price
        "50",          # quantity
        "",            # abv
        "",            # volume_ml
        "",            # origin
        ""            # description
    ], (True, 2), True),
    
    ("failure_db_error", [
        "Test Beer",    # name
        "Test Brand",   # brand
        "Beer",         # type
        "4.99",        # price
        "50",          # quantity
        "",            # abv
        "",            # volume_ml
        "",            # origin
        ""            # description
    ], (False, "Product already exists"), False),
])
def test_add_new_product(test_id, mock_inputs, db_result, expected_success):
    """Test adding new products with various scenarios"""
    with patch('builtins.input', side_effect=mock_inputs):
        with patch('src.product_management.insert_product', return_value=db_result):
            result = add_new_product()
            assert result == expected_success

# Additional integration tests
def test_add_new_product_data_validation():
    """Test that add_new_product correctly processes the data before database insertion"""
    mock_inputs = [
        "Test Beer",    # name
        "Test Brand",   # brand
        "Beer",         # type
        "4.99",        # price
        "50",          # quantity
        "4.5",         # abv
        "500",         # volume_ml
        "Ireland",     # origin
        "Test beer description"  # description
    ]
    
    with patch('builtins.input', side_effect=mock_inputs):
        with patch('src.product_management.insert_product') as mock_insert:
            mock_insert.return_value = (True, 1)
            add_new_product()
            
            # Verify the data was properly processed
            call_args = mock_insert.call_args[0][0]
            assert call_args['name'].strip() == "Test Beer"
            # Check data types
            assert isinstance(call_args['price'], float)
            assert isinstance(call_args['quantity'], int)
            assert isinstance(call_args['abv'], float)
            assert isinstance(call_args['volume_ml'], int)
            
            # Check values with appropriate comparison methods
            assert call_args['price'] == pytest.approx(4.99, rel=1e-6)
            assert call_args['quantity'] == 50
            assert call_args['abv'] == pytest.approx(4.5, rel=1e-6)
            assert call_args['volume_ml'] == 500

def test_validate_numeric_value_direct():
    """Test numeric validation function directly to cover edge cases"""
    from src.product_management import validate_numeric_value

    # Test invalid numeric input for non-Initial stock fields
    errors, value = validate_numeric_value("abc", "Custom Field", int)
    assert errors == ["Custom Field must be a valid number"]
    assert value is None

def test_add_new_product_validation_failure():
    """Test validation failure in add_new_product"""
    mock_inputs = [
        "",  # Empty name (will fail validation)
        "Test Brand", 
        "Beer",
        "4.99",
        "50",
        "",
        "",
        "",
        ""
    ]

    with patch('builtins.input', side_effect=mock_inputs), \
         patch('builtins.print') as mock_print:
        result = add_new_product()
        assert result is False
        mock_print.assert_any_call("\nError: Invalid product data:")
        mock_print.assert_any_call("- Product name is required")

def test_add_new_product_db_failure():
    """Test database failure in add_new_product"""
    mock_inputs = [
        "Test Beer",
        "Test Brand",
        "Beer",
        "4.99",
        "50",
        "",
        "",
        "",
        ""
    ]

    with patch('builtins.input', side_effect=mock_inputs), \
         patch('src.product_management.insert_product', return_value=(False, "Database error")), \
         patch('builtins.print') as mock_print:
        result = add_new_product()
        assert result is False
        mock_print.assert_any_call("\nError: Failed to add product - Database error")


# SCRUM-6 Update Product Tests
class TestLookupProductById:
    """test class for lookup_product_by_id function"""
    
    @patch('sqlite3.connect')
    def test_lookup_product_by_id_success(self, mock_connect):
        """Test successfully looking up a product by ID"""
        from src.product_management import lookup_product_by_id
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_row = (1, 'Test Beer', 'Test Brand', 'Beer', 5.99, 50, 4.5, 500, 'Ireland', 'Description')
        mock_cursor.fetchone.return_value = mock_row
        
        success, product = lookup_product_by_id(1)
        
        assert success is True
        assert product['id'] == 1
        assert product['name'] == 'Test Beer'
        assert product['brand'] == 'Test Brand'
        assert product['type'] == 'Beer'
        assert product['price'] == pytest.approx(5.99, rel=1e-6)
        assert product['quantity'] == 50
        assert product['abv'] == pytest.approx(4.5, rel=1e-6)
        assert product['volume_ml'] == 500
        assert product['origin_country'] == 'Ireland'
        assert product['description'] == 'Description'
        mock_conn.close.assert_called_once()
    
    @patch('sqlite3.connect')
    def test_lookup_product_by_id_not_found(self, mock_connect):
        """Test looking up non-existent product"""
        from src.product_management import lookup_product_by_id
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        success, message = lookup_product_by_id(999)
        
        assert success is False
        assert "No product found with ID: 999" in message
        mock_conn.close.assert_called_once()
    
    @patch('sqlite3.connect')
    def test_lookup_product_by_id_database_error(self, mock_connect):
        """Test database error during lookup"""
        from src.product_management import lookup_product_by_id
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Connection failed")
        
        success, message = lookup_product_by_id(1)
        
        assert success is False
        assert "Database error" in message
        mock_conn.close.assert_called_once()


class TestUpdateProductCli:
    """test class for update_product_cli function"""
    
    @patch('src.product_management.lookup_product_by_id')
    @patch('src.database_manager.update_product')
    @patch('builtins.input')
    def test_update_product_cli_success_all_fields(self, mock_input, mock_update, mock_lookup):
        """Test successful update of all product fields"""
        from src.product_management import update_product_cli
        
        # Mock product lookup
        mock_lookup.return_value = (True, {
            'id': 1,
            'name': 'Old Name',
            'brand': 'Old Brand',
            'type': 'Beer',
            'price': 5.99,
            'quantity': 50,
            'abv': 4.5,
            'volume_ml': 500,
            'origin_country': 'Ireland',
            'description': 'Old description'
        })
        
        # Mock user inputs
        mock_input.side_effect = [
            '1',  # product id
            'New Name',  # name
            'New Brand',  # brand
            'Lager',  # type
            '6.99',  # price
            '100',  # quantity
            '5.0',  # abv
            '330',  # volume_ml
            'Germany',  # origin_country
            'New description'  # description
        ]
        
        # Mock database update
        mock_update.return_value = (True, "Product updated successfully")
        
        result = update_product_cli()
        
        assert result is True
        mock_update.assert_called_once()
        
        # Verify update data
        call_args = mock_update.call_args[0]
        assert call_args[0] == 1  # product_id
        update_data = call_args[1]
        assert update_data['name'] == 'New Name'
        assert update_data['brand'] == 'New Brand'
        assert update_data['type'] == 'Lager'
        assert update_data['price'] == pytest.approx(6.99, rel=1e-6)
        assert update_data['quantity_on_hand'] == 100
        assert update_data['abv'] == pytest.approx(5.0, rel=1e-6)
        assert update_data['volume_ml'] == 330
        assert update_data['origin_country'] == 'Germany'
        assert update_data['description'] == 'New description'
    
    @patch('src.product_management.lookup_product_by_id')
    @patch('src.database_manager.update_product')
    @patch('builtins.input')
    def test_update_product_cli_partial_update(self, mock_input, mock_update, mock_lookup):
        """Test updating only some fields (keeping others)"""
        from src.product_management import update_product_cli
        
        mock_lookup.return_value = (True, {
            'id': 1,
            'name': 'Test Beer',
            'brand': 'Test Brand',
            'type': 'Beer',
            'price': 5.99,
            'quantity': 50,
            'abv': 4.5,
            'volume_ml': 500,
            'origin_country': 'Ireland',
            'description': 'Description'
        })
        
        # User presses Enter to keep current values for most fields
        mock_input.side_effect = [
            '1',  # product id
            '',  # name (keep current)
            '',  # brand (keep current)
            '',  # type (keep current)
            '7.99',  # price (update)
            '',  # quantity (keep current)
            '',  # abv (keep current)
            '',  # volume_ml (keep current)
            '',  # origin_country (keep current)
            'Updated description'  # description (update)
        ]
        
        mock_update.return_value = (True, "Product updated successfully")
        
        result = update_product_cli()
        
        assert result is True
        mock_update.assert_called_once()
        
        # Verify only updated fields are in update_data
        call_args = mock_update.call_args[0]
        update_data = call_args[1]
        assert update_data['price'] == pytest.approx(7.99, rel=1e-6)
        assert update_data['description'] == 'Updated description'
        # Other fields should not be in update_data
        assert 'name' not in update_data
        assert 'brand' not in update_data
    
    @patch('builtins.input')
    def test_update_product_cli_invalid_product_id(self, mock_input):
        """Test handling of invalid product ID"""
        from src.product_management import update_product_cli
        
        mock_input.return_value = 'abc'  # Invalid ID
        
        result = update_product_cli()
        
        assert result is False
    
    @patch('src.product_management.lookup_product_by_id')
    @patch('builtins.input')
    def test_update_product_cli_product_not_found(self, mock_input, mock_lookup):
        """Test handling of non-existent product"""
        from src.product_management import update_product_cli
        
        mock_input.return_value = '999'
        mock_lookup.return_value = (False, "No product found with ID: 999")
        
        result = update_product_cli()
        
        assert result is False
    
    @patch('src.product_management.lookup_product_by_id')
    @patch('builtins.input')
    def test_update_product_cli_validation_error_negative_price(self, mock_input, mock_lookup):
        """Test validation error for negative price"""
        from src.product_management import update_product_cli
        
        mock_lookup.return_value = (True, {
            'id': 1,
            'name': 'Test Beer',
            'brand': 'Test Brand',
            'type': 'Beer',
            'price': 5.99,
            'quantity': 50,
            'abv': 4.5,
            'volume_ml': 500,
            'origin_country': 'Ireland',
            'description': 'Description'
        })
        
        mock_input.side_effect = [
            '1',  # product id
            '',  # name
            '',  # brand
            '',  # type
            '-5.99',  # invalid price
            '',  # quantity
            '',  # abv
            '',  # volume_ml
            '',  # origin_country
            ''   # description
        ]
        
        result = update_product_cli()
        
        assert result is False
    
    @patch('src.product_management.lookup_product_by_id')
    @patch('builtins.input')
    def test_update_product_cli_validation_error_invalid_abv(self, mock_input, mock_lookup):
        """Test validation error for ABV over 100"""
        from src.product_management import update_product_cli
        
        mock_lookup.return_value = (True, {
            'id': 1,
            'name': 'Test Beer',
            'brand': 'Test Brand',
            'type': 'Beer',
            'price': 5.99,
            'quantity': 50,
            'abv': 4.5,
            'volume_ml': 500,
            'origin_country': None,
            'description': None
        })
        
        mock_input.side_effect = [
            '1',  # product id
            '',  # name
            '',  # brand
            '',  # type
            '',  # price
            '',  # quantity
            '101',  # invalid ABV
            '',  # volume_ml
            '',  # origin_country
            ''   # description
        ]
        
        result = update_product_cli()
        
        assert result is False
    
    @patch('src.product_management.lookup_product_by_id')
    @patch('builtins.input')
    def test_update_product_cli_no_changes(self, mock_input, mock_lookup):
        """Test when user doesn't provide any changes"""
        from src.product_management import update_product_cli
        
        mock_lookup.return_value = (True, {
            'id': 1,
            'name': 'Test Beer',
            'brand': 'Test Brand',
            'type': 'Beer',
            'price': 5.99,
            'quantity': 50,
            'abv': None,
            'volume_ml': None,
            'origin_country': None,
            'description': None
        })
        
        # User presses Enter for all fields
        mock_input.side_effect = ['1'] + [''] * 9
        
        result = update_product_cli()
        
        assert result is False
    
    @patch('src.product_management.lookup_product_by_id')
    @patch('src.database_manager.update_product')
    @patch('builtins.input')
    def test_update_product_cli_database_error(self, mock_input, mock_update, mock_lookup):
        """Test handling of database error during update"""
        from src.product_management import update_product_cli
        
        mock_lookup.return_value = (True, {
            'id': 1,
            'name': 'Test Beer',
            'brand': 'Test Brand',
            'type': 'Beer',
            'price': 5.99,
            'quantity': 50,
            'abv': None,
            'volume_ml': None,
            'origin_country': None,
            'description': None
        })
        
        mock_input.side_effect = [
            '1',  # product id
            '',  # name
            '',  # brand
            '',  # type
            '6.99',  # price
            '',  # quantity
            '',  # abv
            '',  # volume_ml
            '',  # origin_country
            ''   # description
        ]
        
        mock_update.return_value = (False, "Database error")
        
        result = update_product_cli()
        
        assert result is False
    
    @patch('src.product_management.lookup_product_by_id')
    @patch('src.database_manager.update_product')
    @patch('builtins.input')
    def test_update_product_cli_clear_optional_fields(self, mock_input, mock_update, mock_lookup):
        """Test clearing optional fields by entering blank"""
        from src.product_management import update_product_cli
        
        mock_lookup.return_value = (True, {
            'id': 1,
            'name': 'Test Beer',
            'brand': 'Test Brand',
            'type': 'Beer',
            'price': 5.99,
            'quantity': 50,
            'abv': 4.5,
            'volume_ml': 500,
            'origin_country': 'Ireland',
            'description': 'Description'
        })
        
        # User enters blank to clear optional fields but keeps required fields
        mock_input.side_effect = [
            '1',  # product id
            '',  # name (keep)
            '',  # brand (keep)
            '',  # type (keep)
            '6.99',  # price (update to see something changed)
            '',  # quantity (keep)
            '',  # abv (clear)
            '',  # volume_ml (clear)
            '',  # origin_country (clear)
            ''   # description (clear)
        ]
        
        mock_update.return_value = (True, "Product updated successfully")
        
        result = update_product_cli()
        
        assert result is True
        
        # Verify optional fields are set to None and price is updated
        call_args = mock_update.call_args[0]
        update_data = call_args[1]
        assert update_data.get('price') == pytest.approx(6.99, rel=1e-6)
        assert update_data.get('abv') is None
        assert update_data.get('volume_ml') is None
        assert update_data.get('origin_country') is None
        assert update_data.get('description') is None
    
    @patch('src.product_management.lookup_product_by_id')
    @patch('builtins.input')
    def test_update_product_cli_validation_empty_required_field(self, mock_input, mock_lookup):
        """Test validation error when required field is set to empty"""
        from src.product_management import update_product_cli
        
        mock_lookup.return_value = (True, {
            'id': 1,
            'name': 'Test Beer',
            'brand': 'Test Brand',
            'type': 'Beer',
            'price': 5.99,
            'quantity': 50,
            'abv': None,
            'volume_ml': None,
            'origin_country': None,
            'description': None
        })
        
        mock_input.side_effect = [
            '1',  # product id
            '   ',  # name (whitespace only - invalid)
            '',  # brand
            '',  # type
            '',  # price
            '',  # quantity
            '',  # abv
            '',  # volume_ml
            '',  # origin_country
            ''   # description
        ]
        
        result = update_product_cli()
        
        assert result is False
    
    @patch('src.product_management.lookup_product_by_id')
    @patch('builtins.input')
    def test_update_product_cli_validation_quantity_non_integer(self, mock_input, mock_lookup):
        """Test validation error for non-integer quantity"""
        from src.product_management import update_product_cli
        
        mock_lookup.return_value = (True, {
            'id': 1,
            'name': 'Test Beer',
            'brand': 'Test Brand',
            'type': 'Beer',
            'price': 5.99,
            'quantity': 50,
            'abv': None,
            'volume_ml': None,
            'origin_country': None,
            'description': None
        })
        
        mock_input.side_effect = [
            '1',  # product id
            '',  # name
            '',  # brand
            '',  # type
            '',  # price
            'abc',  # quantity (invalid)
            '',  # abv
            '',  # volume_ml
            '',  # origin_country
            ''   # description
        ]
        
        result = update_product_cli()
        
        assert result is False
    
    @patch('src.product_management.lookup_product_by_id')
    @patch('builtins.input')
    def test_update_product_cli_validation_volume_non_integer(self, mock_input, mock_lookup):
        """Test validation error for non-integer volume"""
        from src.product_management import update_product_cli
        
        mock_lookup.return_value = (True, {
            'id': 1,
            'name': 'Test Beer',
            'brand': 'Test Brand',
            'type': 'Beer',
            'price': 5.99,
            'quantity': 50,
            'abv': None,
            'volume_ml': None,
            'origin_country': None,
            'description': None
        })
        
        mock_input.side_effect = [
            '1',  # product id
            '',  # name
            '',  # brand
            '',  # type
            '',  # price
            '',  # quantity
            '',  # abv
            'not_a_number',  # volume_ml (invalid)
            '',  # origin_country
            ''   # description
        ]
        
        result = update_product_cli()
        
        assert result is False
    
    @patch('src.product_management.lookup_product_by_id')
    @patch('builtins.input')
    def test_update_product_cli_validation_price_text(self, mock_input, mock_lookup):
        """Test validation error for non-numeric price"""
        from src.product_management import update_product_cli
        
        mock_lookup.return_value = (True, {
            'id': 1,
            'name': 'Test Beer',
            'brand': 'Test Brand',
            'type': 'Beer',
            'price': 5.99,
            'quantity': 50,
            'abv': None,
            'volume_ml': None,
            'origin_country': None,
            'description': None
        })
        
        mock_input.side_effect = [
            '1',  # product id
            '',  # name
            '',  # brand
            '',  # type
            'abc',  # price (invalid)
            '',  # quantity
            '',  # abv
            '',  # volume_ml
            '',  # origin_country
            ''   # description
        ]
        
        result = update_product_cli()
        
        assert result is False
    
    @patch('src.product_management.lookup_product_by_id')
    @patch('builtins.input')
    def test_update_product_cli_validation_abv_text(self, mock_input, mock_lookup):
        """Test validation error for non-numeric ABV"""
        from src.product_management import update_product_cli
        
        mock_lookup.return_value = (True, {
            'id': 1,
            'name': 'Test Beer',
            'brand': 'Test Brand',
            'type': 'Beer',
            'price': 5.99,
            'quantity': 50,
            'abv': None,
            'volume_ml': None,
            'origin_country': None,
            'description': None
        })
        
        mock_input.side_effect = [
            '1',  # product id
            '',  # name
            '',  # brand
            '',  # type
            '',  # price
            '',  # quantity
            'not_a_number',  # abv (invalid)
            '',  # volume_ml
            '',  # origin_country
            ''   # description
        ]
        
        result = update_product_cli()
        
        assert result is False
    
    @patch('src.product_management.lookup_product_by_id')
    @patch('builtins.input')
    def test_update_product_cli_validation_negative_quantity(self, mock_input, mock_lookup):
        """Test validation error for negative quantity"""
        from src.product_management import update_product_cli
        
        mock_lookup.return_value = (True, {
            'id': 1,
            'name': 'Test Beer',
            'brand': 'Test Brand',
            'type': 'Beer',
            'price': 5.99,
            'quantity': 50,
            'abv': None,
            'volume_ml': None,
            'origin_country': None,
            'description': None
        })
        
        mock_input.side_effect = [
            '1',  # product id
            '',  # name
            '',  # brand
            '',  # type
            '',  # price
            '-10',  # quantity (negative)
            '',  # abv
            '',  # volume_ml
            '',  # origin_country
            ''   # description
        ]
        
        result = update_product_cli()
        
        assert result is False
    
    @patch('src.product_management.lookup_product_by_id')
    @patch('builtins.input')
    def test_update_product_cli_validation_volume_zero(self, mock_input, mock_lookup):
        """Test validation error for zero volume"""
        from src.product_management import update_product_cli
        
        mock_lookup.return_value = (True, {
            'id': 1,
            'name': 'Test Beer',
            'brand': 'Test Brand',
            'type': 'Beer',
            'price': 5.99,
            'quantity': 50,
            'abv': None,
            'volume_ml': None,
            'origin_country': None,
            'description': None
        })
        
        mock_input.side_effect = [
            '1',  # product id
            '',  # name
            '',  # brand
            '',  # type
            '',  # price
            '',  # quantity
            '',  # abv
            '0',  # volume_ml (zero - invalid)
            '',  # origin_country
            ''   # description
        ]
        
        result = update_product_cli()
        
        assert result is False
