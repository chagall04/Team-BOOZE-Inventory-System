import unittest
from unittest.mock import patch
from src.product_management import add_new_product, validate_product_data

class TestProductManagement(unittest.TestCase):
    """Test cases for Product Management functionality (SCRUM-27)"""
    
    def test_validate_product_data(self):
        """Test the client-side validation function"""
        # Test valid data with optional fields
        is_valid, errors = validate_product_data(
            "Beer X", "Brand Y", "Beer", "5.99", "10", "4.5", "500"
        )
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Test valid data without optional fields
        is_valid, errors = validate_product_data(
            "Beer X", "Brand Y", "Beer", "5.99", "10"
        )
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Test invalid price
        is_valid, errors = validate_product_data(
            "Beer X", "Brand Y", "Beer", "-5.99", "10"
        )
        self.assertFalse(is_valid)
        self.assertIn("Price must be non-negative", errors)
        
        # Test invalid quantity
        is_valid, errors = validate_product_data(
            "Beer X", "Brand Y", "Beer", "5.99", "-10"
        )
        self.assertFalse(is_valid)
        self.assertIn("Initial stock quantity must be non-negative", errors)
        
        # Test invalid ABV
        is_valid, errors = validate_product_data(
            "Beer X", "Brand Y", "Beer", "5.99", "10", "101", "500"
        )
        self.assertFalse(is_valid)
        self.assertIn("ABV must be between 0 and 100", errors)
        
        # Test empty name
        is_valid, errors = validate_product_data(
            "", "Brand Y", "Beer", "5.99", "10"
        )
        self.assertFalse(is_valid)
        self.assertIn("Product name is required", errors)

    @patch('builtins.input')
    @patch('src.product_management.insert_product')
    def test_add_new_product_success(self, mock_insert, mock_input):
        """Test successful product addition"""
        # Mock user inputs including optional fields
        mock_input.side_effect = [
            "Test Beer",    # name
            "Test Brand",   # brand
            "Beer",        # type
            "4.99",        # price
            "50",          # quantity
            "4.5",         # abv (optional)
            "500",         # volume_ml (optional)
            "Ireland",     # origin (optional)
            "Test beer description"  # description (optional)
        ]
        
        # Mock successful database insertion
        mock_insert.return_value = (True, 1)  # Success, ID = 1
        
        # Call the function
        result = add_new_product()
        
        # Verify success
        self.assertTrue(result)
        
        # Verify database was called with correct data
        mock_insert.assert_called_once()
        call_args = mock_insert.call_args[0][0]
        self.assertEqual(call_args['name'], "Test Beer")
        self.assertEqual(call_args['price'], 4.99)
        self.assertEqual(call_args['quantity'], 50)
        self.assertEqual(call_args['abv'], 4.5)
        self.assertEqual(call_args['volume_ml'], 500)
        self.assertEqual(call_args['origin_country'], "Ireland")
        self.assertEqual(call_args['description'], "Test beer description")

    @patch('builtins.input')
    @patch('src.product_management.insert_product')
    def test_add_new_product_db_error(self, mock_insert, mock_input):
        """Test handling of database errors"""
        # Mock user inputs
        mock_input.side_effect = [
            "Test Beer",  # name
            "Test Brand", # brand
            "Beer",      # type
            "4.99",      # price
            "50",        # quantity
            "",          # abv (optional)
            "",          # volume_ml (optional)
            "",          # origin (optional)
            ""          # description (optional)
        ]
        
        # Mock database error
        mock_insert.return_value = (False, "Product name already exists")
        
        # Call the function
        result = add_new_product()
        
        # Verify failure
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()