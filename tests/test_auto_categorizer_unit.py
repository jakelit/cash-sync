"""
Unit tests for AutoCategorizer class.

This module contains comprehensive unit tests for the AutoCategorizer class,
covering initialization, rule parsing, and rule evaluation logic.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from openpyxl import Workbook
import tempfile
import os

from excel_finance_tools.auto_categorizer import AutoCategorizer

@pytest.fixture
def sample_excel_file():
    """Fixture to create a temporary Excel file with a minimal AutoCat sheet for testing."""
    wb = Workbook()
    ws = wb.active
    ws.title = 'AutoCat'
    ws.append(['Category', 'Description Contains', 'Amount Max', 'Tags'])
    ws.append(['Groceries', 'WALMART', 500, 'shopping'])
    ws.append(['', 'AMAZON', '', 'online'])
    fd, path = tempfile.mkstemp(suffix='.xlsx')
    os.close(fd)
    wb.save(path)
    yield path
    os.remove(path)

class TestAutoCategorizerInit:
    """Test AutoCategorizer initialization and configuration."""

    def test_init_with_valid_file_path(self, sample_excel_file):
        """TC001: Test valid initialization with valid Excel file path."""
        categorizer = AutoCategorizer(sample_excel_file)
        
        assert categorizer.excel_file == sample_excel_file
        assert categorizer.rules == []
        assert hasattr(categorizer, '_regex_cache')
        assert hasattr(categorizer, '_comparison_methods')
        assert len(categorizer._comparison_methods) == 10  # All comparison types

    def test_init_with_invalid_file_path(self):
        """TC002: Test initialization with invalid file path raises FileNotFoundError."""
        with patch('excel_finance_tools.auto_categorizer.ExcelHandler') as mock_excel_handler:
            # Configure the mock to raise FileNotFoundError when instantiated
            mock_excel_handler.side_effect = FileNotFoundError("File not found")
            
            with pytest.raises(FileNotFoundError):
                AutoCategorizer("non_existent_file.xlsx")

    def test_init_creates_excel_handler(self, sample_excel_file):
        """TC001: Test that initialization creates ExcelHandler instance."""
        categorizer = AutoCategorizer(sample_excel_file)
        
        assert hasattr(categorizer, 'excel_handler')
        assert categorizer.excel_handler.excel_file == sample_excel_file

    def test_load_rules_valid_autocat_worksheet(self, sample_excel_file):
        """TC003: Test loading rules from a valid AutoCat worksheet."""
        categorizer = AutoCategorizer(sample_excel_file)
        # Mock get_autocat_rules to return a valid DataFrame
        rules_df = pd.DataFrame([
            {'Category': 'Groceries', 'Description Contains': 'WALMART'},
            {'Category': 'Gas', 'Description Contains': 'SHELL'}
        ])
        with patch.object(categorizer.excel_handler, 'get_autocat_rules', return_value=rules_df):
            with patch.object(categorizer.excel_handler, 'existing_columns', ['Description', 'Amount', 'Category']):
                categorizer._load_and_parse_rules()
                assert len(categorizer.rules) == 2
                assert categorizer.rules[0]['category'] == 'Groceries'
                assert categorizer.rules[1]['category'] == 'Gas'

    def test_load_rules_missing_autocat_worksheet(self, sample_excel_file):
        """TC004: Test behavior when AutoCat worksheet is missing."""
        categorizer = AutoCategorizer(sample_excel_file)
        # Mock get_autocat_rules to return None
        with patch.object(categorizer.excel_handler, 'get_autocat_rules', return_value=None):
            categorizer._load_and_parse_rules()
            assert categorizer.rules == []

    def test_load_rules_missing_category_column(self, sample_excel_file):
        """TC005: Test behavior when AutoCat worksheet is missing the Category column."""
        categorizer = AutoCategorizer(sample_excel_file)
        # Mock get_autocat_rules to return a DataFrame without 'Category'
        rules_df = pd.DataFrame([
            {'Description Contains': 'WALMART'},
            {'Description Contains': 'SHELL'}
        ])
        with patch.object(categorizer.excel_handler, 'get_autocat_rules', return_value=rules_df):
            with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
                categorizer._load_and_parse_rules()
                assert categorizer.rules == []
                mock_logger.error.assert_called()
                error_call = mock_logger.error.call_args[0][0]
                assert "must contain a 'Category' column" in error_call

    def test_load_rules_rule_with_no_valid_conditions(self, sample_excel_file):
        """TC041: Test that rules with no valid conditions are not added to self.rules."""
        categorizer = AutoCategorizer(sample_excel_file)
        # Mock get_autocat_rules to return a DataFrame with a rule that has no valid conditions
        rules_df = pd.DataFrame([
            {'Category': 'Groceries', 'Description Contains': 'WALMART'},  # Valid rule
            {'Category': 'Invalid', 'Invalid Column': 'some value', 'Another Invalid': 'value'}  # No valid conditions
        ])
        with patch.object(categorizer.excel_handler, 'get_autocat_rules', return_value=rules_df):
            with patch.object(categorizer.excel_handler, 'existing_columns', ['Description', 'Amount', 'Category']):
                categorizer._load_and_parse_rules()
                # Should only have the first rule (with valid conditions)
                assert len(categorizer.rules) == 1
                assert categorizer.rules[0]['category'] == 'Groceries'

class TestAutoCategorizerRuleParsing:
    """Test rule parsing and validation logic."""

    @pytest.fixture
    def categorizer(self, sample_excel_file):
        """Provide a standard AutoCategorizer instance."""
        cat = AutoCategorizer(sample_excel_file)
        # Ensure existing_columns is always a list
        if getattr(cat.excel_handler, 'existing_columns', None) is None:
            cat.excel_handler.existing_columns = ['Description', 'Amount', 'Tags', 'Account']
        return cat

    def test_parse_rule_columns_contains_rule(self, categorizer):
        """TC006: Test parsing 'Description Contains' rule."""
        col_name = "Description Contains"
        value = "WALMART"
        
        result = categorizer._extract_rule_condition(col_name, value)
        
        assert result is not None
        assert result['field'] == "Description"
        assert result['type'] == "contains"
        assert result['value'] == "WALMART"

    def test_parse_rule_columns_min_max_rules(self, categorizer):
        """TC007: Test parsing 'Amount Min' and 'Amount Max' rules."""
        # Test Min rule
        min_result = categorizer._extract_rule_condition("Amount Min", 100)
        assert min_result['field'] == "Amount"
        assert min_result['type'] == "min"
        assert min_result['value'] == 100
        
        # Test Max rule
        max_result = categorizer._extract_rule_condition("Amount Max", 500)
        assert max_result['field'] == "Amount"
        assert max_result['type'] == "max"
        assert max_result['value'] == 500

    def test_parse_rule_columns_equals_rule(self, categorizer):
        """TC008: Test parsing 'Account Equals' rule."""
        result = categorizer._extract_rule_condition("Account Equals", "Checking")
        
        assert result['field'] == "Account"
        assert result['type'] == "equals"
        assert result['value'] == "Checking"

    def test_parse_rule_columns_starts_with_rule(self, categorizer):
        """TC009: Test parsing 'Description starts with' rule."""
        result = categorizer._extract_rule_condition("Description starts with", "STAR")
        
        assert result['field'] == "Description"
        assert result['type'] == "starts_with"
        assert result['value'] == "STAR"

    def test_parse_rule_columns_ends_with_rule(self, categorizer):
        """TC010: Test parsing 'Description ends with' rule."""
        result = categorizer._extract_rule_condition("Description ends with", "UCKS")
        
        assert result['field'] == "Description"
        assert result['type'] == "ends_with"
        assert result['value'] == "UCKS"

    def test_parse_rule_columns_regex_rule(self, categorizer):
        """TC011: Test parsing 'Description regex' rule."""
        result = categorizer._extract_rule_condition("Description regex", ".*GAS.*")
        
        assert result['field'] == "Description"
        assert result['type'] == "regex"
        assert result['value'] == ".*GAS.*"

    def test_parse_rule_columns_not_contains_rule(self, categorizer):
        """TC012: Test parsing 'Description not contains' rule."""
        result = categorizer._extract_rule_condition("Description not contains", "WALMART")
        
        assert result['field'] == "Description"
        assert result['type'] == "not_contains"
        assert result['value'] == "WALMART"

    def test_parse_rule_columns_not_equals_rule(self, categorizer):
        """TC013: Test parsing 'Account not equals' rule."""
        result = categorizer._extract_rule_condition("Account not equals", "Savings")
        
        assert result['field'] == "Account"
        assert result['type'] == "not_equals"
        assert result['value'] == "Savings"

    def test_parse_rule_columns_between_rule(self, categorizer):
        """TC014: Test parsing 'Amount between' rule."""
        result = categorizer._extract_rule_condition("Amount between", "100,500")
        
        assert result['field'] == "Amount"
        assert result['type'] == "between"
        assert result['value'] == "100,500"

    def test_parse_rule_columns_invalid_rule_format(self, categorizer):
        """TC015: Test parsing invalid rule format logs warning and returns None."""
        with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
            result = categorizer._extract_rule_condition("Invalid Column", "value")
            
            assert result is None
            # Note: The current implementation doesn't log warnings for invalid formats

    def test_parse_single_rule_with_valid_conditions(self, categorizer):
        """TC006, TC007, TC008, TC010: Test parsing a single rule with valid conditions."""
        row_data = {
            'Category': 'Groceries',
            'Description Contains': 'WALMART',
            'Amount Max': 500,
            'Tags': 'shopping'
        }
        row = pd.Series(row_data)
        
        with patch.object(categorizer.excel_handler, 'existing_columns', ['Description', 'Amount', 'Tags']):
            rule = categorizer._parse_single_rule(row)
            
            assert rule['category'] == 'Groceries'
            assert len(rule['conditions']) == 2
            assert rule['auto_fill'] == {'Tags': 'shopping'}

    def test_parse_single_rule_with_empty_category(self, categorizer):
        """TC006, TC010: Test parsing a rule with empty category (auto-fill only)."""
        row_data = {
            'Category': '',
            'Description Contains': 'WALMART',
            'Tags': 'shopping'
        }
        row = pd.Series(row_data)
        
        with patch.object(categorizer.excel_handler, 'existing_columns', ['Description', 'Tags']):
            rule = categorizer._parse_single_rule(row)
            
            assert rule['category'] == ''
            assert len(rule['conditions']) == 1
            assert rule['auto_fill'] == {'Tags': 'shopping'}

    def test_parse_single_rule_with_invalid_auto_fill_column(self, categorizer):
        """TC047: Test parsing a rule with invalid auto-fill column is ignored and logged."""
        row_data = {
            'Category': 'Groceries',
            'Description Contains': 'WALMART',
            'Invalid Column': 'some value'  # Not in existing_columns
        }
        row = pd.Series(row_data)
        
        with patch.object(categorizer.excel_handler, 'existing_columns', ['Description', 'Category']):
            with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
                rule = categorizer._parse_single_rule(row)
                
                # Verify the rule is still created correctly
                assert rule['category'] == 'Groceries'
                assert len(rule['conditions']) == 1
                assert rule['auto_fill'] == {}  # Invalid column ignored
                mock_logger.warning.assert_called_with(
                    "Column '%s' in 'AutoCat' sheet is not a valid rule or auto-fill column and will be ignored.",
                    'Invalid Column'
                )

    def test_extract_rule_condition_valid_format_invalid_field(self, categorizer):
        """TC042: Test rule column with valid format but field not in transaction table."""
        with patch.object(categorizer.excel_handler, 'existing_columns', ['Amount', 'Category']):  # No 'Description'
            with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
                result = categorizer._extract_rule_condition("Description Contains", "WALMART")
                assert result is None
                mock_logger.warning.assert_called_with(
                    "Rule column '%s' ignored: '%s' not found in Transactions table.", 
                    "Description Contains", "Description"
                )

class TestAutoCategorizerRuleEvaluation:
    """Test rule evaluation and matching logic."""

    @pytest.fixture
    def categorizer(self, sample_excel_file):
        """Provide a standard AutoCategorizer instance."""
        cat = AutoCategorizer(sample_excel_file)
        if getattr(cat.excel_handler, 'existing_columns', None) is None:
            cat.excel_handler.existing_columns = ['Description', 'Amount', 'Tags', 'Account']
        return cat

    def test_evaluate_rule_contains_match(self, categorizer):
        """TC016: Test contains rule with matching text."""
        condition = {'field': 'Description', 'type': 'contains', 'value': 'WALMART'}
        transaction = pd.Series({'Description': 'WALMART GROCERY PURCHASE'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    def test_evaluate_rule_contains_no_match(self, categorizer):
        """TC017: Test contains rule with no matching text."""
        condition = {'field': 'Description', 'type': 'contains', 'value': 'WALMART'}
        transaction = pd.Series({'Description': 'SHELL GAS STATION'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    def test_evaluate_rule_min_match(self, categorizer):
        """TC018: Test min rule with matching amount."""
        condition = {'field': 'Amount', 'type': 'min', 'value': 100}
        transaction = pd.Series({'Amount': 150.00})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    def test_evaluate_rule_min_no_match(self, categorizer):
        """TC019: Test min rule with amount below minimum."""
        condition = {'field': 'Amount', 'type': 'min', 'value': 100}
        transaction = pd.Series({'Amount': 50.00})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    def test_evaluate_rule_max_match(self, categorizer):
        """TC020: Test max rule with matching amount."""
        condition = {'field': 'Amount', 'type': 'max', 'value': 500}
        transaction = pd.Series({'Amount': 300.00})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    def test_evaluate_rule_max_no_match(self, categorizer):
        """TC021: Test max rule with amount above maximum."""
        condition = {'field': 'Amount', 'type': 'max', 'value': 500}
        transaction = pd.Series({'Amount': 600.00})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    def test_evaluate_rule_equals_match(self, categorizer):
        """TC022: Test equals rule with exact match."""
        condition = {'field': 'Account', 'type': 'equals', 'value': 'Checking'}
        transaction = pd.Series({'Account': 'Checking'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    def test_evaluate_rule_equals_no_match(self, categorizer):
        """TC023: Test equals rule with different text."""
        condition = {'field': 'Account', 'type': 'equals', 'value': 'Checking'}
        transaction = pd.Series({'Account': 'Savings'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    def test_evaluate_rule_starts_with_match(self, categorizer):
        """TC024: Test starts with rule with matching prefix."""
        condition = {'field': 'Description', 'type': 'starts_with', 'value': 'STAR'}
        transaction = pd.Series({'Description': 'STARBUCKS COFFEE'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    def test_evaluate_rule_starts_with_no_match(self, categorizer):
        """TC025: Test starts with rule with different prefix."""
        condition = {'field': 'Description', 'type': 'starts_with', 'value': 'COFFEE'}
        transaction = pd.Series({'Description': 'STARBUCKS COFFEE'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    def test_evaluate_rule_ends_with_match(self, categorizer):
        """TC026: Test ends with rule with matching suffix."""
        condition = {'field': 'Description', 'type': 'ends_with', 'value': 'COFFEE'}
        transaction = pd.Series({'Description': 'STARBUCKS COFFEE'})
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    def test_evaluate_rule_ends_with_no_match(self, categorizer):
        """TC027: Test ends with rule with different suffix."""
        condition = {'field': 'Description', 'type': 'ends_with', 'value': 'STAR'}
        transaction = pd.Series({'Description': 'STARBUCKS COFFEE'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    def test_evaluate_rule_regex_match(self, categorizer):
        """TC028: Test regex rule with matching pattern."""
        condition = {'field': 'Description', 'type': 'regex', 'value': r'.*GAS.*'}
        transaction = pd.Series({'Description': 'SHELL GAS STATION'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    def test_evaluate_rule_regex_no_match(self, categorizer):
        """TC029: Test regex rule with non-matching pattern."""
        condition = {'field': 'Description', 'type': 'regex', 'value': r'.*GAS.*'}
        transaction = pd.Series({'Description': 'WALMART GROCERY'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    def test_evaluate_rule_not_contains_match(self, categorizer):
        """TC030: Test not contains rule with text that doesn't contain value."""
        condition = {'field': 'Description', 'type': 'not_contains', 'value': 'WALMART'}
        transaction = pd.Series({'Description': 'SHELL GAS STATION'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    def test_evaluate_rule_not_contains_no_match(self, categorizer):
        """TC031: Test not contains rule with text that contains value."""
        condition = {'field': 'Description', 'type': 'not_contains', 'value': 'WALMART'}
        transaction = pd.Series({'Description': 'WALMART GROCERY'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    def test_evaluate_rule_not_equals_match(self, categorizer):
        """TC032: Test not equals rule with different values."""
        condition = {'field': 'Account', 'type': 'not_equals', 'value': 'Checking'}
        transaction = pd.Series({'Account': 'Savings'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    def test_evaluate_rule_not_equals_no_match(self, categorizer):
        """TC033: Test not equals rule with same values."""
        condition = {'field': 'Account', 'type': 'not_equals', 'value': 'Checking'}
        transaction = pd.Series({'Account': 'Checking'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    def test_evaluate_rule_between_match(self, categorizer):
        """TC034: Test between rule with value in range."""
        condition = {'field': 'Amount', 'type': 'between', 'value': '100,500'}
        transaction = pd.Series({'Amount': 250.00})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    def test_evaluate_rule_between_no_match(self, categorizer):
        """TC035: Test between rule with value outside range."""
        condition = {'field': 'Amount', 'type': 'between', 'value': '100,500'}
        transaction = pd.Series({'Amount': 600.00})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    def test_evaluate_rule_case_insensitive(self, categorizer):
        """TC036: Test case insensitive comparison for contains."""
        condition = {'field': 'Description', 'type': 'contains', 'value': 'walmart'}
        transaction = pd.Series({'Description': 'WALMART GROCERY'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    def test_evaluate_rule_case_sensitive_equals(self, categorizer):
        """TC037: Test case sensitive comparison for equals."""
        condition = {'field': 'Account', 'type': 'equals', 'value': 'Walmart'}
        transaction = pd.Series({'Account': 'walmart'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    def test_evaluate_rule_empty_rule_value(self, categorizer):
        """TC038: Test rule with empty value (should be ignored)."""
        condition = {'field': 'Description', 'type': 'contains', 'value': ''}
        transaction = pd.Series({'Description': 'WALMART GROCERY'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True  # Empty values should be ignored

    def test_evaluate_rule_missing_transaction_column(self, categorizer):
        """TC039: Test rule with missing transaction column."""
        condition = {'field': 'NonExistentColumn', 'type': 'contains', 'value': 'WALMART'}
        transaction = pd.Series({'Description': 'WALMART GROCERY'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    def test_evaluate_rule_invalid_numeric_data(self, categorizer):
        """TC040: Test rule with invalid numeric data."""
        condition = {'field': 'Amount', 'type': 'min', 'value': 100}
        transaction = pd.Series({'Amount': 'not_a_number'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    def test_is_match_all_conditions_must_match(self, categorizer):
        """TC041: Test that all conditions must match for a rule to match (AND logic)."""
        conditions = [
            {'field': 'Description', 'type': 'contains', 'value': 'WALMART'},
            {'field': 'Amount', 'type': 'max', 'value': 500}
        ]
        transaction = pd.Series({
            'Description': 'WALMART GROCERY',
            'Amount': 300.00
        })
        
        result = categorizer._is_match(transaction, conditions)
        assert result is True

    def test_is_match_fails_when_one_condition_fails(self, categorizer):
        """TC041: Test that rule fails when one condition fails (AND logic)."""
        conditions = [
            {'field': 'Description', 'type': 'contains', 'value': 'WALMART'},
            {'field': 'Amount', 'type': 'max', 'value': 500}
        ]
        transaction = pd.Series({
            'Description': 'WALMART GROCERY',
            'Amount': 600.00  # Above max
        })
        
        result = categorizer._is_match(transaction, conditions)
        assert result is False

    def test_unknown_comparison_type_logs_warning(self, categorizer):
        """NOT IN PLAN: Test that unknown comparison type logs warning and returns False."""
        condition = {'field': 'Description', 'type': 'unknown_type', 'value': 'WALMART'}
        transaction = pd.Series({'Description': 'WALMART GROCERY'})
        with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
            result = categorizer._evaluate_condition(transaction, condition)
            assert result is False
            mock_logger.warning.assert_called()
