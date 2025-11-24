"""Tests for product management functionality including validation and addition."""

from unittest.mock import patch
import pytest
from src.product_management import add_new_product, validate_product_data, view_all_products

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



def test_view_all_products_displays_all_products(capsys, monkeypatch):
    """
    Test that view_all_products() displays all products correctly
    """
    # Mock database response with multiple products
    mock_products = [
        {
            'id': 1,
            'name': 'Jameson Irish Whiskey',
            'brand': 'Jameson',
            'type': 'Whiskey',
            'abv': 40.0,
            'volume_ml': 700,
            'origin_country': 'Ireland',
            'price': 25.99,
            'quantity_on_hand': 50,
            'description': 'Smooth Irish whiskey'
        },
        {
            'id': 2,
            'name': 'Guinness Draught',
            'brand': 'Guinness',
            'type': 'Stout',
            'abv': 4.2,
            'volume_ml': 500,
            'origin_country': 'Ireland',
            'price': 3.50,
            'quantity_on_hand': 120,
            'description': 'Classic Irish stout'
        },
        {
            'id': 3,
            'name': 'Baileys Irish Cream',
            'brand': 'Baileys',
            'type': 'Liqueur',
            'abv': 17.0,
            'volume_ml': 750,
            'origin_country': 'Ireland',
            'price': 18.75,
            'quantity_on_hand': 30,
            'description': 'Creamy liqueur'
        }
    ]
    
    monkeypatch.setattr('src.product_management.get_all_products', lambda: mock_products)
    
    result = view_all_products()
    
    captured = capsys.readouterr()
    
    assert "=== All Products ===" in captured.out
    assert "ID" in captured.out
    assert "Name" in captured.out
    assert "Brand" in captured.out
    assert "Price (€)" in captured.out
    assert "Stock" in captured.out
    
    # Verify all products are displayed
    assert "1" in captured.out
    assert "Jameson Irish Whiskey" in captured.out
    assert "Jameson" in captured.out
    assert "€25.99" in captured.out
    assert "50" in captured.out
    
    assert "2" in captured.out
    assert "Guinness Draught" in captured.out
    assert "Guinness" in captured.out
    assert "€3.50" in captured.out
    assert "120" in captured.out
    
    assert "3" in captured.out
    assert "Baileys Irish Cream" in captured.out
    assert "Baileys" in captured.out
    assert "€18.75" in captured.out
    assert "30" in captured.out
    
    # Verify total count
    assert "Total products: 3" in captured.out
    
    # Verify function returns True
    assert result is True


def test_view_all_products_empty_inventory(capsys, monkeypatch):
    """
    Test that view_all_products() handles empty inventory
    """
    monkeypatch.setattr('src.product_management.get_all_products', lambda: [])
    
    view_all_products()
    
    captured = capsys.readouterr()
    
    assert "=== All Products ===" in captured.out
    assert "No products found in inventory." in captured.out


def test_view_all_products_single_product(capsys, monkeypatch):
    """
    Test that view_all_products() displays single product correctly
    """
    mock_products = [
        {
            'id': 42,
            'name': 'Test Vodka',
            'brand': 'Test Brand',
            'type': 'Vodka',
            'abv': 37.5,
            'volume_ml': 1000,
            'origin_country': 'Poland',
            'price': 15.00,
            'quantity_on_hand': 10,
            'description': 'Test description'
        }
    ]
    
    monkeypatch.setattr('src.product_management.get_all_products', lambda: mock_products)
    
    result = view_all_products()
    
    captured = capsys.readouterr()
    
    assert "42" in captured.out
    assert "Test Vodka" in captured.out
    assert "Test Brand" in captured.out
    assert "€15.00" in captured.out
    assert "10" in captured.out
    assert "Total products: 1" in captured.out
    assert result is True


def test_view_all_products_price_formatting(capsys, monkeypatch):
    """
    Test that prices are formatted correctly with 2 decimal places
    """
    mock_products = [
        {
            'id': 1,
            'name': 'Product A',
            'brand': 'Brand A',
            'type': 'Type A',
            'abv': 40.0,
            'volume_ml': 700,
            'origin_country': 'Country A',
            'price': 10.5,  # Should display as €10.50
            'quantity_on_hand': 5,
            'description': 'Desc A'
        },
        {
            'id': 2,
            'name': 'Product B',
            'brand': 'Brand B',
            'type': 'Type B',
            'abv': 20.0,
            'volume_ml': 500,
            'origin_country': 'Country B',
            'price': 99.99,  # Should display as €99.99
            'quantity_on_hand': 100,
            'description': 'Desc B'
        }
    ]
    
    monkeypatch.setattr('src.product_management.get_all_products', lambda: mock_products)
    
    view_all_products()
    
    captured = capsys.readouterr()
    
    # Verify price formatting
    assert "€10.50" in captured.out
    assert "€99.99" in captured.out
