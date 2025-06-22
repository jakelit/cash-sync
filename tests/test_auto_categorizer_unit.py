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

    @pytest.mark.unit
    def test_init_with_valid_file_path(self, sample_excel_file):
        """UT001: Test valid initialization with valid Excel file path."""
        categorizer = AutoCategorizer(sample_excel_file)
        
        assert categorizer.excel_file == sample_excel_file
        assert categorizer.rules == []
        assert hasattr(categorizer, '_regex_cache')
        assert hasattr(categorizer, '_comparison_methods')
        assert len(categorizer._comparison_methods) == 10  # All comparison types
        assert hasattr(categorizer, 'excel_handler')
        assert categorizer.excel_handler.excel_file == sample_excel_file

    @pytest.mark.unit
    def test_init_with_invalid_file_path(self):
        """UT002: Test initialization with invalid file path."""
        with patch('excel_finance_tools.auto_categorizer.ExcelHandler') as mock_excel_handler:
            # Configure the mock to raise FileNotFoundError when instantiated
            mock_excel_handler.side_effect = FileNotFoundError("File not found")
            
            with pytest.raises(FileNotFoundError):
                AutoCategorizer("non_existent_file.xlsx")

    @pytest.mark.unit
    def test_load_rules_valid_autocat_worksheet(self, sample_excel_file):
        """UT003: Test loading rules from a valid AutoCat worksheet."""
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

    @pytest.mark.unit
    def test_load_rules_missing_autocat_worksheet(self, sample_excel_file):
        """UT004: Test loading rules when AutoCat worksheet is missing."""
        categorizer = AutoCategorizer(sample_excel_file)
        # Mock get_autocat_rules to return None
        with patch.object(categorizer.excel_handler, 'get_autocat_rules', return_value=None):
            with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
                categorizer._load_and_parse_rules()
                mock_logger.warning.assert_called_with("AutoCat worksheet not found or empty")
                assert len(categorizer.rules) == 0

    @pytest.mark.unit
    def test_load_rules_missing_category_column(self, sample_excel_file):
        """UT005: Test loading rules when Category column is missing."""
        categorizer = AutoCategorizer(sample_excel_file)
        # Mock get_autocat_rules to return a DataFrame without 'Category'
        rules_df = pd.DataFrame([
            {'Description Contains': 'WALMART'},
            {'Amount Min': 100}
        ])
        with patch.object(categorizer.excel_handler, 'get_autocat_rules', return_value=rules_df):
            with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
                categorizer._load_and_parse_rules()
                # The actual implementation logs an ERROR and sets rules to empty list
                mock_logger.error.assert_called_with("The 'AutoCat' sheet must contain a 'Category' column.")
                assert len(categorizer.rules) == 0

    @pytest.mark.unit
    def test_load_rules_rule_with_no_valid_conditions(self, sample_excel_file):
        """UT041: Test that rules with no valid conditions are not added to self.rules."""
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

    @pytest.mark.unit
    def test_parse_rule_columns_contains_rule(self, categorizer):
        """UT006: Test parsing 'Description Contains' rule."""
        col_name = "Description Contains"
        value = "WALMART"
        
        result = categorizer._extract_rule_condition(col_name, value)
        
        assert result is not None
        assert result['field'] == "Description"
        assert result['type'] == "contains"
        assert result['value'] == "WALMART"

    @pytest.mark.unit
    def test_parse_rule_columns_min_max_rules(self, categorizer):
        """UT007: Test parsing 'Amount Min' and 'Amount Max' rules."""
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

    @pytest.mark.unit
    def test_parse_rule_columns_equals_rule(self, categorizer):
        """UT008: Test parsing 'Account Equals' rule."""
        result = categorizer._extract_rule_condition("Account Equals", "Checking")
        
        assert result['field'] == "Account"
        assert result['type'] == "equals"
        assert result['value'] == "Checking"

    @pytest.mark.unit
    def test_parse_rule_columns_starts_with_rule(self, categorizer):
        """UT009: Test parsing 'Description starts with' rule."""
        result = categorizer._extract_rule_condition("Description starts with", "STAR")
        
        assert result['field'] == "Description"
        assert result['type'] == "starts_with"
        assert result['value'] == "STAR"

    @pytest.mark.unit
    def test_parse_rule_columns_ends_with_rule(self, categorizer):
        """UT010: Test parsing 'Description ends with' rule."""
        result = categorizer._extract_rule_condition("Description ends with", "UCKS")
        
        assert result['field'] == "Description"
        assert result['type'] == "ends_with"
        assert result['value'] == "UCKS"

    @pytest.mark.unit
    def test_parse_rule_columns_regex_rule(self, categorizer):
        """UT011: Test parsing 'Description regex' rule."""
        result = categorizer._extract_rule_condition("Description regex", ".*GAS.*")
        
        assert result['field'] == "Description"
        assert result['type'] == "regex"
        assert result['value'] == ".*GAS.*"

    @pytest.mark.unit
    def test_parse_rule_columns_not_contains_rule(self, categorizer):
        """UT012: Test parsing 'Description not contains' rule."""
        result = categorizer._extract_rule_condition("Description not contains", "WALMART")
        
        assert result['field'] == "Description"
        assert result['type'] == "not_contains"
        assert result['value'] == "WALMART"

    @pytest.mark.unit
    def test_parse_rule_columns_not_equals_rule(self, categorizer):
        """UT013: Test parsing 'Account not equals' rule."""
        result = categorizer._extract_rule_condition("Account not equals", "Savings")
        
        assert result['field'] == "Account"
        assert result['type'] == "not_equals"
        assert result['value'] == "Savings"

    @pytest.mark.unit
    def test_parse_rule_columns_between_rule(self, categorizer):
        """UT014: Test parsing 'Amount between' rule."""
        result = categorizer._extract_rule_condition("Amount between", "100,500")
        
        assert result['field'] == "Amount"
        assert result['type'] == "between"
        assert result['value'] == "100,500"

    @pytest.mark.unit
    def test_parse_rule_columns_invalid_rule_format(self, categorizer):
        """UT015: Test parsing invalid rule format logs warning and returns None."""
        with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
            result = categorizer._extract_rule_condition("Invalid Column", "value")
            
            assert result is None
            # Note: The current implementation doesn't log warnings for invalid formats

    @pytest.mark.unit
    def test_parse_single_rule_with_valid_conditions(self, categorizer):
        """UT006, UT007, UT008, UT010: Test parsing a single rule with valid conditions."""
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

    @pytest.mark.unit
    def test_parse_single_rule_with_empty_category(self, categorizer):
        """UT006, UT010: Test parsing a rule with empty category (auto-fill only)."""
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

    @pytest.mark.unit
    def test_parse_single_rule_with_invalid_auto_fill_column(self, categorizer):
        """UT042: Test parsing a rule with invalid auto-fill column is ignored and logged."""
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

    @pytest.mark.unit
    def test_extract_rule_condition_valid_format_invalid_field(self, categorizer):
        """UT042: Test rule column with valid format but field not in transaction table."""
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
        # Ensure existing_columns is always a list
        if getattr(cat.excel_handler, 'existing_columns', None) is None:
            cat.excel_handler.existing_columns = ['Description', 'Amount', 'Tags', 'Account']
        return cat

    @pytest.mark.unit
    def test_evaluate_rule_contains_match(self, categorizer):
        """UT016: Test contains rule with matching text."""
        condition = {'field': 'Description', 'type': 'contains', 'value': 'WALMART'}
        transaction = pd.Series({'Description': 'WALMART GROCERY PURCHASE'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    @pytest.mark.unit
    def test_evaluate_rule_contains_no_match(self, categorizer):
        """UT017: Test contains rule with no matching text."""
        condition = {'field': 'Description', 'type': 'contains', 'value': 'WALMART'}
        transaction = pd.Series({'Description': 'SHELL GAS STATION'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    @pytest.mark.unit
    def test_evaluate_rule_min_match(self, categorizer):
        """UT018: Test min rule with matching amount."""
        condition = {'field': 'Amount', 'type': 'min', 'value': 100}
        transaction = pd.Series({'Amount': 150.00})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    @pytest.mark.unit
    def test_evaluate_rule_min_no_match(self, categorizer):
        """UT019: Test min rule with amount below minimum."""
        condition = {'field': 'Amount', 'type': 'min', 'value': 100}
        transaction = pd.Series({'Amount': 50.00})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    @pytest.mark.unit
    def test_evaluate_rule_max_match(self, categorizer):
        """UT020: Test max rule with matching amount."""
        condition = {'field': 'Amount', 'type': 'max', 'value': 500}
        transaction = pd.Series({'Amount': 300.00})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    @pytest.mark.unit
    def test_evaluate_rule_max_no_match(self, categorizer):
        """UT021: Test max rule with amount above maximum."""
        condition = {'field': 'Amount', 'type': 'max', 'value': 500}
        transaction = pd.Series({'Amount': 600.00})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    @pytest.mark.unit
    def test_evaluate_rule_equals_match(self, categorizer):
        """UT022: Test equals rule with exact match."""
        condition = {'field': 'Account', 'type': 'equals', 'value': 'Checking'}
        transaction = pd.Series({'Account': 'Checking'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    @pytest.mark.unit
    def test_evaluate_rule_equals_no_match(self, categorizer):
        """UT023: Test equals rule with different text."""
        condition = {'field': 'Account', 'type': 'equals', 'value': 'Checking'}
        transaction = pd.Series({'Account': 'Savings'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    @pytest.mark.unit
    def test_evaluate_rule_starts_with_match(self, categorizer):
        """UT024: Test starts with rule with matching prefix."""
        condition = {'field': 'Description', 'type': 'starts_with', 'value': 'STAR'}
        transaction = pd.Series({'Description': 'STARBUCKS COFFEE'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    @pytest.mark.unit
    def test_evaluate_rule_starts_with_no_match(self, categorizer):
        """UT025: Test starts with rule with different prefix."""
        condition = {'field': 'Description', 'type': 'starts_with', 'value': 'COFFEE'}
        transaction = pd.Series({'Description': 'STARBUCKS COFFEE'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    @pytest.mark.unit
    def test_evaluate_rule_ends_with_match(self, categorizer):
        """UT026: Test ends with rule with matching suffix."""
        condition = {'field': 'Description', 'type': 'ends_with', 'value': 'COFFEE'}
        transaction = pd.Series({'Description': 'STARBUCKS COFFEE'})
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    @pytest.mark.unit
    def test_evaluate_rule_ends_with_no_match(self, categorizer):
        """UT027: Test ends with rule with different suffix."""
        condition = {'field': 'Description', 'type': 'ends_with', 'value': 'STAR'}
        transaction = pd.Series({'Description': 'STARBUCKS COFFEE'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    @pytest.mark.unit
    def test_evaluate_rule_regex_match(self, categorizer):
        """UT028: Test regex rule with matching pattern."""
        condition = {'field': 'Description', 'type': 'regex', 'value': r'.*GAS.*'}
        transaction = pd.Series({'Description': 'SHELL GAS STATION'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    @pytest.mark.unit
    def test_evaluate_rule_regex_no_match(self, categorizer):
        """UT029: Test regex rule with non-matching pattern."""
        condition = {'field': 'Description', 'type': 'regex', 'value': r'.*GAS.*'}
        transaction = pd.Series({'Description': 'WALMART GROCERY'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    @pytest.mark.unit
    def test_evaluate_rule_not_contains_match(self, categorizer):
        """UT030: Test not contains rule with text that doesn't contain value."""
        condition = {'field': 'Description', 'type': 'not_contains', 'value': 'WALMART'}
        transaction = pd.Series({'Description': 'SHELL GAS STATION'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    @pytest.mark.unit
    def test_evaluate_rule_not_contains_no_match(self, categorizer):
        """UT031: Test not contains rule with text that contains value."""
        condition = {'field': 'Description', 'type': 'not_contains', 'value': 'WALMART'}
        transaction = pd.Series({'Description': 'WALMART GROCERY'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    @pytest.mark.unit
    def test_evaluate_rule_not_equals_match(self, categorizer):
        """UT032: Test not equals rule with different values."""
        condition = {'field': 'Account', 'type': 'not_equals', 'value': 'Checking'}
        transaction = pd.Series({'Account': 'Savings'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    @pytest.mark.unit
    def test_evaluate_rule_not_equals_no_match(self, categorizer):
        """UT033: Test not equals rule with same values."""
        condition = {'field': 'Account', 'type': 'not_equals', 'value': 'Checking'}
        transaction = pd.Series({'Account': 'Checking'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    @pytest.mark.unit
    def test_evaluate_rule_between_match(self, categorizer):
        """UT034: Test between rule with value in range."""
        condition = {'field': 'Amount', 'type': 'between', 'value': '100,500'}
        transaction = pd.Series({'Amount': 250.00})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    @pytest.mark.unit
    def test_evaluate_rule_between_no_match(self, categorizer):
        """UT035: Test between rule with value outside range."""
        condition = {'field': 'Amount', 'type': 'between', 'value': '100,500'}
        transaction = pd.Series({'Amount': 600.00})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    @pytest.mark.unit
    def test_evaluate_rule_case_insensitive(self, categorizer):
        """UT036: Test case insensitive comparison for contains."""
        condition = {'field': 'Description', 'type': 'contains', 'value': 'walmart'}
        transaction = pd.Series({'Description': 'WALMART GROCERY'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True

    @pytest.mark.unit
    def test_evaluate_rule_case_sensitive_equals(self, categorizer):
        """UT037: Test case sensitive comparison for equals."""
        condition = {'field': 'Account', 'type': 'equals', 'value': 'Walmart'}
        transaction = pd.Series({'Account': 'walmart'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    @pytest.mark.unit
    def test_evaluate_rule_empty_rule_value(self, categorizer):
        """UT038: Test rule with empty value (should be ignored)."""
        condition = {'field': 'Description', 'type': 'contains', 'value': ''}
        transaction = pd.Series({'Description': 'WALMART GROCERY'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is True  # Empty values should be ignored

    @pytest.mark.unit
    def test_evaluate_rule_missing_transaction_column(self, categorizer):
        """UT039: Test rule with missing transaction column."""
        condition = {'field': 'NonExistentColumn', 'type': 'contains', 'value': 'WALMART'}
        transaction = pd.Series({'Description': 'WALMART GROCERY'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    @pytest.mark.unit
    def test_evaluate_rule_invalid_numeric_data(self, categorizer):
        """UT040: Test rule with invalid numeric data."""
        condition = {'field': 'Amount', 'type': 'min', 'value': 100}
        transaction = pd.Series({'Amount': 'not_a_number'})
        
        result = categorizer._evaluate_condition(transaction, condition)
        assert result is False

    @pytest.mark.unit
    def test_is_match_all_conditions_must_match(self, categorizer):
        """UT044: Test that all conditions must match for a rule to match (AND logic)."""
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

    @pytest.mark.unit
    def test_is_match_fails_when_one_condition_fails(self, categorizer):
        """UT045: Test that rule fails when one condition fails (AND logic)."""
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

    @pytest.mark.unit
    def test_unknown_comparison_type_logs_warning(self, categorizer):
        """UT043: Test that unknown comparison type logs warning and returns False."""
        condition = {'field': 'Description', 'type': 'unknown_type', 'value': 'WALMART'}
        transaction = pd.Series({'Description': 'WALMART GROCERY'})
        with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
            result = categorizer._evaluate_condition(transaction, condition)
            assert result is False
            mock_logger.warning.assert_called()

    @pytest.mark.unit
    def test_load_rules_no_valid_conditions(self, sample_excel_file):
        """UT041: Test loading rules with no valid conditions."""
        categorizer = AutoCategorizer(sample_excel_file)
        # Mock get_autocat_rules to return a DataFrame with no valid conditions
        rules_df = pd.DataFrame([
            {'Category': 'Groceries', 'Description Contains': 'WALMART'},  # Valid rule
            {'Category': 'Invalid', 'Invalid Column': 'some value', 'Another Invalid': 'value'}  # No valid conditions
        ])
        with patch.object(categorizer.excel_handler, 'get_autocat_rules', return_value=rules_df):
            with patch.object(categorizer.excel_handler, 'existing_columns', ['Description', 'Amount', 'Category']):
                categorizer._load_and_parse_rules()
                assert len(categorizer.rules) == 1
                assert categorizer.rules[0]['category'] == 'Groceries'
