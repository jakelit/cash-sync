"""
Integration tests for AutoCategorizer class.

This module contains integration tests for the AutoCategorizer class,
covering component interactions with ExcelHandler and transaction data.
"""

import pytest
from unittest.mock import Mock, patch
import pandas as pd

from excel_finance_tools.auto_categorizer import AutoCategorizer

@pytest.fixture
def mock_excel_handler():
    """Mock ExcelHandler for integration testing."""
    with patch('excel_finance_tools.auto_categorizer.ExcelHandler') as mock_handler:
        mock_instance = mock_handler.return_value
        mock_instance.excel_file = "test.xlsx"
        mock_instance.existing_columns = ['Date', 'Description', 'Amount', 'Category', 'Account', 'Tags']
        mock_instance.existing_df = pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
            'Description': ['WALMART GROCERY', 'SHELL GAS STATION', 'STARBUCKS COFFEE', 'ALREADY CATEGORIZED'],
            'Amount': [150.00, 45.50, 5.75, 25.00],
            'Category': ['', '', '', 'Entertainment'],
            'Account': ['Checking', 'Checking', 'Checking', 'Checking'],
            'Tags': ['', '', '', '']
        })
        yield mock_instance

class TestAutoCategorizerIntegration:
    """Test integration with ExcelHandler and transaction data."""

    # ===== BASIC FUNCTIONALITY TESTS (TC043-TC048) =====

    @pytest.mark.integration
    def test_single_rule_match(self, mock_excel_handler):
        """TC043: Test single rule match - Category assigned, auto-fill applied."""
        categorizer = AutoCategorizer("test.xlsx")
        mock_excel_handler.get_autocat_rules.return_value = pd.DataFrame([
            {'Category': 'Groceries', 'Description Contains': 'WALMART', 'Tags': 'shopping'}
        ])
        with patch.object(mock_excel_handler, 'update_cell') as mock_update, \
             patch.object(mock_excel_handler, 'save'):
            success, message = categorizer.run_auto_categorization()
            assert success is True
            assert "categorized" in message.lower()
            
            # Verify that update_cell was called
            update_calls = mock_update.call_args_list
            assert len(update_calls) >= 2
            
            # Verify the specific category was applied
            category_updates = [call for call in update_calls if call[0][1] == 'Category']
            assert len(category_updates) > 0
            applied_category = category_updates[0][0][2]
            assert applied_category == 'Groceries', f"Expected 'Groceries' but got '{applied_category}'"
            
            # Verify the specific auto-fill was applied
            tag_updates = [call for call in update_calls if call[0][1] == 'Tags']
            assert len(tag_updates) > 0
            applied_tag = tag_updates[0][0][2]
            assert applied_tag == 'shopping', f"Expected 'shopping' but got '{applied_tag}'"

    @pytest.mark.integration
    def test_multiple_rules_first_match(self, mock_excel_handler):
        """TC044: Test multiple rules, first match - First rule applied, others ignored."""
        categorizer = AutoCategorizer("test.xlsx")
        mock_excel_handler.get_autocat_rules.return_value = pd.DataFrame([
            {'Category': 'Groceries', 'Description Contains': 'WALMART', 'Tags': 'shopping'},
            {'Category': 'Food', 'Description Contains': 'WALMART', 'Tags': 'food'}
        ])
        with patch.object(mock_excel_handler, 'update_cell') as mock_update, \
             patch.object(mock_excel_handler, 'save'):
            success, message = categorizer.run_auto_categorization()
            assert success is True
            
            # Verify that update_cell was called
            update_calls = mock_update.call_args_list
            assert len(update_calls) > 0
            
            # Find the category update call and verify it's the first rule's category
            category_updates = [call for call in update_calls if call[0][1] == 'Category']
            assert len(category_updates) > 0
            
            # Verify the first rule's category ('Groceries') was applied, not the second rule's ('Food')
            applied_category = category_updates[0][0][2]  # The category value that was set
            assert applied_category == 'Groceries', f"Expected 'Groceries' but got '{applied_category}'"
            
            # Verify the first rule's auto-fill ('shopping') was applied
            tag_updates = [call for call in update_calls if call[0][1] == 'Tags']
            assert len(tag_updates) > 0
            applied_tag = tag_updates[0][0][2]  # The tag value that was set
            assert applied_tag == 'shopping', f"Expected 'shopping' but got '{applied_tag}'"

    @pytest.mark.integration
    def test_complex_rule_combination(self, mock_excel_handler):
        """TC048: Test complex rule combination - All conditions must match."""
        categorizer = AutoCategorizer("test.xlsx")
        mock_excel_handler.get_autocat_rules.return_value = pd.DataFrame([
            {
                'Category': 'Coffee',
                'Description Contains': 'STARBUCKS',
                'Amount Max': 20,
                'Tags': 'food'
            }
        ])
        with patch.object(mock_excel_handler, 'update_cell') as mock_update, \
             patch.object(mock_excel_handler, 'save'):
            success, message = categorizer.run_auto_categorization()
            assert success is True
            
            # Verify that update_cell was called
            update_calls = mock_update.call_args_list
            assert len(update_calls) >= 2
            
            # Verify the specific category was applied (both conditions must match)
            category_updates = [call for call in update_calls if call[0][1] == 'Category']
            assert len(category_updates) > 0
            applied_category = category_updates[0][0][2]
            assert applied_category == 'Coffee', f"Expected 'Coffee' but got '{applied_category}'"
            
            # Verify the specific auto-fill was applied
            tag_updates = [call for call in update_calls if call[0][1] == 'Tags']
            assert len(tag_updates) > 0
            applied_tag = tag_updates[0][0][2]
            assert applied_tag == 'food', f"Expected 'food' but got '{applied_tag}'"

    # ===== EDGE CASES TESTS (TC045-TC047) =====

    @pytest.mark.integration
    def test_no_rules_match(self, mock_excel_handler):
        """TC045: Test no rules match - No changes made."""
        categorizer = AutoCategorizer("test.xlsx")
        mock_excel_handler.get_autocat_rules.return_value = pd.DataFrame([
            {'Category': 'Electronics', 'Description Contains': 'BEST BUY', 'Tags': 'tech'}
        ])
        with patch.object(mock_excel_handler, 'update_cell') as mock_update, \
             patch.object(mock_excel_handler, 'save'):
            success, message = categorizer.run_auto_categorization()
            assert success is True
            assert "no updates" in message.lower() or "no new transactions" in message.lower()
            mock_update.assert_not_called()

    @pytest.mark.integration
    def test_empty_category_rule(self, mock_excel_handler):
        """TC046: Test empty category rule - Only auto-fill applied."""
        categorizer = AutoCategorizer("test.xlsx")
        mock_excel_handler.get_autocat_rules.return_value = pd.DataFrame([
            {'Category': '', 'Description Contains': 'WALMART', 'Tags': 'shopping'}
        ])
        with patch.object(mock_excel_handler, 'update_cell') as mock_update, \
             patch.object(mock_excel_handler, 'save'):
            success, message = categorizer.run_auto_categorization()
            assert success is True
            update_calls = mock_update.call_args_list
            tag_updates = [call for call in update_calls if call[0][1] == 'Tags']
            category_updates = [call for call in update_calls if call[0][1] == 'Category']
            assert len(tag_updates) > 0
            assert all(call[0][2] == '' for call in category_updates)

    @pytest.mark.integration
    def test_all_transactions_categorized(self, mock_excel_handler):
        """TC047: Test all transactions categorized - No changes made."""
        categorizer = AutoCategorizer("test.xlsx")
        # All transactions already categorized
        mock_excel_handler.existing_df = pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02'],
            'Description': ['WALMART GROCERY', 'SHELL GAS'],
            'Amount': [150.00, 45.50],
            'Category': ['Groceries', 'Gas'],
            'Account': ['Checking', 'Checking']
        })
        mock_excel_handler.get_autocat_rules.return_value = pd.DataFrame([
            {'Category': 'Groceries', 'Description Contains': 'WALMART', 'Tags': 'shopping'}
        ])
        with patch.object(mock_excel_handler, 'update_cell') as mock_update, \
             patch.object(mock_excel_handler, 'save'):
            success, message = categorizer.run_auto_categorization()
            assert success is True
            assert "no uncategorized" in message.lower()
            mock_update.assert_not_called()

    # ===== WARNING TESTS (TC049, TC052) =====

    @pytest.mark.integration
    def test_invalid_auto_fill_column(self, mock_excel_handler):
        """TC049: Test invalid auto-fill column - Auto-fill ignored, logged."""
        categorizer = AutoCategorizer("test.xlsx")
        mock_excel_handler.get_autocat_rules.return_value = pd.DataFrame([
            {
                'Category': 'Groceries',
                'Description Contains': 'WALMART',
                'Invalid Column': 'some value'
            }
        ])
        with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger, \
             patch.object(mock_excel_handler, 'update_cell') as mock_update, \
             patch.object(mock_excel_handler, 'save'):
            success, message = categorizer.run_auto_categorization()
            assert success is True
            mock_logger.warning.assert_called()
            warning_call = mock_logger.warning.call_args[0][0]
            assert "not a valid rule or auto-fill column" in warning_call
            update_calls = mock_update.call_args_list
            category_updates = [call for call in update_calls if call[0][1] == 'Category']
            assert len(category_updates) > 0

    @pytest.mark.integration
    def test_invalid_rule_syntax(self, mock_excel_handler):
        """TC052: Test invalid rule syntax - Rule ignored, processing continues."""
        categorizer = AutoCategorizer("test.xlsx")
        # Mock rules with invalid syntax that should be ignored
        mock_excel_handler.get_autocat_rules.return_value = pd.DataFrame([
            {
                'Category': 'Groceries',
                'Description Contains': 'WALMART',  # Valid rule
                'Invalid Column Name': 'some value'  # Invalid syntax
            }
        ])
        
        with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger, \
             patch.object(mock_excel_handler, 'update_cell') as mock_update, \
             patch.object(mock_excel_handler, 'save'):
            success, message = categorizer.run_auto_categorization()
            
            # Should still succeed and process valid rules
            assert success is True
            assert "categorized" in message.lower()
            
            # Should log warning about invalid column
            mock_logger.warning.assert_called()
            warning_calls = [call[0][0] for call in mock_logger.warning.call_args_list]
            assert any("not a valid rule or auto-fill column" in call for call in warning_calls)
            
            # Should still update categories for valid rules
            update_calls = mock_update.call_args_list
            category_updates = [call for call in update_calls if call[0][1] == 'Category']
            assert len(category_updates) > 0

    @pytest.mark.integration
    def test_empty_autocat_worksheet(self, mock_excel_handler):
        """TC053: Test empty AutoCat worksheet - Returns True with warning message."""
        categorizer = AutoCategorizer("test.xlsx")
        # Mock empty AutoCat worksheet (empty DataFrame)
        mock_excel_handler.get_autocat_rules.return_value = pd.DataFrame()
        
        with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger, \
             patch.object(mock_excel_handler, 'update_cell') as mock_update, \
             patch.object(mock_excel_handler, 'save'):
            success, message = categorizer.run_auto_categorization()
            
            # Should return True with warning message
            assert success is True
            assert "No valid categorization rules found in 'AutoCat' sheet." in message
            
            # Should log warning
            mock_logger.warning.assert_called()
            warning_call = mock_logger.warning.call_args[0][0]
            assert "No valid categorization rules found in 'AutoCat' sheet." in warning_call
            
            # Should not make any updates since no rules exist
            mock_update.assert_not_called()

    # ===== EXCEPTION HANDLING TESTS (TC050-TC051, TC054-TC057) =====

    @pytest.mark.integration
    def test_corrupted_excel_file(self, mock_excel_handler):
        """TC050: Test corrupted Excel file - Returns False with appropriate exception."""
        categorizer = AutoCategorizer("test.xlsx")
        # Mock load_workbook to raise OSError (corrupted file)
        mock_excel_handler.load_workbook.side_effect = OSError("Invalid Excel file format")
        
        with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
            success, message = categorizer.run_auto_categorization()
            
            # Should return False with error message
            assert success is False
            assert "An error occurred:" in message
            assert "Invalid Excel file format" in message
            
            # Should log error
            mock_logger.error.assert_called()
            error_call = mock_logger.error.call_args[0][0]
            assert "An error occurred during auto-categorization:" in error_call

    @pytest.mark.integration
    def test_permission_denied(self, mock_excel_handler):
        """TC051: Test permission denied - Returns False with PermissionError."""
        categorizer = AutoCategorizer("test.xlsx")
        # Mock load_workbook to raise PermissionError
        mock_excel_handler.load_workbook.side_effect = PermissionError("Access denied")
        
        with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
            success, message = categorizer.run_auto_categorization()
            
            # Should return False with error message
            assert success is False
            assert "An error occurred:" in message
            assert "Access denied" in message
            
            # Should log error
            mock_logger.error.assert_called()
            error_call = mock_logger.error.call_args[0][0]
            assert "An error occurred during auto-categorization:" in error_call

    @pytest.mark.integration
    def test_missing_category_column(self, mock_excel_handler):
        """TC054: Test missing Category column - Returns False with ValueError message."""
        categorizer = AutoCategorizer("test.xlsx")
        # Mock existing_df without Category column
        mock_excel_handler.existing_df = pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02'],
            'Description': ['WALMART GROCERY', 'SHELL GAS'],
            'Amount': [150.00, 45.50],
            'Account': ['Checking', 'Checking']
            # Missing 'Category' column
        })
        
        with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
            success, message = categorizer.run_auto_categorization()
            
            # Should return False with error message
            assert success is False
            assert "An error occurred:" in message
            assert "must contain a 'Category' column" in message
            
            # Should log error
            mock_logger.error.assert_called()
            error_call = mock_logger.error.call_args[0][0]
            assert "An error occurred during auto-categorization:" in error_call

    @pytest.mark.integration
    def test_file_not_found_error(self, mock_excel_handler):
        """TC055: Test FileNotFoundError - Returns False with FileNotFoundError message."""
        categorizer = AutoCategorizer("test.xlsx")
        # Mock load_workbook to raise FileNotFoundError
        mock_excel_handler.load_workbook.side_effect = FileNotFoundError("File not found")
        
        with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
            success, message = categorizer.run_auto_categorization()
            
            # Should return False with error message
            assert success is False
            assert "An error occurred:" in message
            assert "File not found" in message
            
            # Should log error
            mock_logger.error.assert_called()
            error_call = mock_logger.error.call_args[0][0]
            assert "An error occurred during auto-categorization:" in error_call

    @pytest.mark.integration
    def test_permission_error_readonly_file(self, mock_excel_handler):
        """TC056: Test PermissionError for read-only file - Returns False with PermissionError message."""
        categorizer = AutoCategorizer("test.xlsx")
        # Mock rules so the categorization process completes and reaches the save() call
        mock_excel_handler.get_autocat_rules.return_value = pd.DataFrame([
            {'Category': 'Groceries', 'Description Contains': 'WALMART', 'Tags': 'shopping'}
        ])
        # Mock save to raise PermissionError (read-only file)
        mock_excel_handler.save.side_effect = PermissionError("File is read-only")
        
        with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
            success, message = categorizer.run_auto_categorization()
            
            # Should return False with error message
            assert success is False
            assert "An error occurred:" in message
            assert "File is read-only" in message
            
            # Should log error
            mock_logger.error.assert_called()
            error_call = mock_logger.error.call_args[0][0]
            assert "An error occurred during auto-categorization:" in error_call

    @pytest.mark.integration
    def test_os_error_general(self, mock_excel_handler):
        """TC057: Test OSError - Returns False with OSError message."""
        categorizer = AutoCategorizer("test.xlsx")
        # Mock load_workbook to raise OSError
        mock_excel_handler.load_workbook.side_effect = OSError("Disk full")
        
        with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
            success, message = categorizer.run_auto_categorization()
            
            # Should return False with error message
            assert success is False
            assert "An error occurred:" in message
            assert "Disk full" in message
            
            # Should log error
            mock_logger.error.assert_called()
            error_call = mock_logger.error.call_args[0][0]
            assert "An error occurred during auto-categorization:" in error_call 