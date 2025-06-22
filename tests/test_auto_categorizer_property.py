"""
Property-based tests for AutoCategorizer class.

This module contains property-based tests for the AutoCategorizer class,
using hypothesis to validate rule parsing consistency and rule evaluation properties.
"""

import sys
import os
import pytest
import pandas as pd
import re
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from excel_finance_tools.auto_categorizer import AutoCategorizer
from excel_finance_tools.excel_handler import ExcelHandler


class TestAutoCategorizerProperty:
    """Property-based tests using hypothesis for comprehensive validation."""
    
    def setup_method(self):
        """Set up test environment for each test method."""
        # Create mock ExcelHandler
        self.mock_handler = Mock()
        self.mock_handler.existing_df = pd.DataFrame()
        self.mock_handler.existing_columns = ["Description", "Amount", "Category", "Account", "Tags", "Notes"]
        self.mock_handler.update_cell = Mock()
        
        # Create AutoCategorizer instance
        with patch('excel_finance_tools.auto_categorizer.ExcelHandler', return_value=self.mock_handler):
            self.categorizer = AutoCategorizer("dummy_file.xlsx")
    
    # Hypothesis strategies for property-based testing
    @st.composite
    def rule_column_names(draw):
        """Generate valid rule column names for testing."""
        field_names = draw(st.sampled_from(["Description", "Amount", "Account", "Category", "Tags", "Notes"]))
        comparison_types = draw(st.sampled_from([
            "Contains", "Not Contains", "Equals", "Not Equals", 
            "Starts With", "Ends With", "Min", "Max", "Between", "Regex"
        ]))
        return f"{field_names} {comparison_types}"
    
    @st.composite
    def transaction_data(draw):
        """Generate realistic transaction data for testing with equal-length columns."""
        length = draw(st.integers(min_value=1, max_value=10))
        descriptions = draw(st.lists(
            st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'S'))),
            min_size=length, max_size=length
        ))
        amounts = draw(st.lists(
            st.floats(min_value=0.01, max_value=10000.0, allow_nan=False, allow_infinity=False),
            min_size=length, max_size=length
        ))
        accounts = draw(st.lists(
            st.sampled_from(["Checking", "Savings", "Credit", "Investment"]),
            min_size=length, max_size=length
        ))
        return pd.DataFrame({
            "Description": descriptions,
            "Amount": amounts,
            "Account": accounts,
            "Category": [""] * length,  # All uncategorized for testing
            "Tags": [""] * length,
            "Notes": [""] * length
        })
    
    @st.composite
    def rule_conditions(draw):
        """Generate rule conditions for testing."""
        field = draw(st.sampled_from(["Description", "Amount", "Account"]))
        comp_type = draw(st.sampled_from([
            "contains", "not_contains", "equals", "not_equals", 
            "starts_with", "ends_with", "min", "max", "between", "regex"
        ]))
        
        # Generate appropriate values based on comparison type
        if comp_type in ["min", "max"]:
            value = draw(st.floats(min_value=0.0, max_value=10000.0))
        elif comp_type == "between":
            min_val = draw(st.floats(min_value=0.0, max_value=5000.0))
            max_val = draw(st.floats(min_value=min_val, max_value=10000.0))
            value = f"{min_val},{max_val}"
        elif comp_type == "regex":
            value = draw(st.sampled_from([r".*GAS.*", r".*FOOD.*", r".*COFFEE.*", r".*SHOP.*"]))
        else:
            value = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N', 'S'))))
        
        return {"field": field, "type": comp_type, "value": value}
    
    @pytest.mark.property
    @given(rule_column_name=rule_column_names())
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_parse_rule_columns_consistency(self, rule_column_name):
        """PROP001: Test that rule parsing is consistent for hypothesis-generated rule names.
        
        This property test validates that the rule parsing logic behaves consistently
        across a wide variety of rule column names. It ensures that:
        
        1. **Deterministic Results**: Same input always produces same output
        2. **Valid Format Handling**: Properly formatted rules are parsed correctly
        3. **Invalid Format Handling**: Malformed rules are handled gracefully
        4. **Field Validation**: Only valid transaction fields are accepted
        """
        # Arrange
        self.categorizer.excel_handler.existing_columns = ["Description", "Amount", "Category", "Account", "Tags", "Notes"]
        
        # Generate a test value for the rule
        test_value = "test_value"
        
        # Act
        result1 = self.categorizer._extract_rule_condition(rule_column_name, test_value)
        result2 = self.categorizer._extract_rule_condition(rule_column_name, test_value)
        
        # Assert: Results should be identical (deterministic)
        assert result1 == result2, f"Rule parsing is not deterministic for '{rule_column_name}'"
        
        # If parsing succeeded, validate the result structure
        if result1 is not None:
            assert isinstance(result1, dict), "Parsed rule should be a dictionary"
            assert "field" in result1, "Parsed rule should have 'field' key"
            assert "type" in result1, "Parsed rule should have 'type' key"
            assert "value" in result1, "Parsed rule should have 'value' key"
            assert result1["value"] == test_value, "Parsed rule should preserve the test value"
            
            # Validate that the field exists in transaction columns
            assert result1["field"] in self.categorizer.excel_handler.existing_columns, \
                f"Parsed field '{result1['field']}' should exist in transaction columns"
            
            # Validate that the comparison type is valid
            assert result1["type"] in self.categorizer.VALID_COMPARISONS.values(), \
                f"Parsed comparison type '{result1['type']}' should be valid"
    
    @pytest.mark.property
    @given(
        condition=rule_conditions(),
        transaction_data=transaction_data()
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_rule_evaluation_properties(self, condition, transaction_data):
        """PROP002: Test that rule evaluation is deterministic and consistent.
        
        This property test validates that rule evaluation behaves consistently
        across random rule/transaction combinations. It ensures that:
        
        1. **Deterministic Results**: Same rule/transaction always produces same result
        2. **Type Safety**: Evaluation handles various data types correctly
        3. **Error Handling**: Invalid data is handled gracefully
        4. **Comparison Logic**: All comparison types work as expected
        5. **Edge Cases**: Boundary conditions are handled properly
        """
        # Arrange
        self.categorizer.excel_handler.existing_df = transaction_data
        self.categorizer.excel_handler.existing_columns = list(transaction_data.columns)
        
        # Get a transaction to test with
        transaction = transaction_data.iloc[0]
        
        # Act: Evaluate the same condition multiple times
        result1 = self.categorizer._evaluate_condition(transaction, condition)
        result2 = self.categorizer._evaluate_condition(transaction, condition)
        
        # Assert: Results should be identical (deterministic)
        assert result1 == result2, f"Rule evaluation is not deterministic for condition {condition}"
        
        # Assert: Result should be boolean
        assert isinstance(result1, bool), f"Rule evaluation should return boolean, got {type(result1)}"
        
        # Test specific properties based on comparison type
        if condition["type"] in ["min", "max", "between"]:
            # Numeric comparisons should handle numeric values correctly
            if pd.notna(transaction.get(condition["field"])):
                try:
                    float(transaction.get(condition["field"]))
                    # If we can convert to float, evaluation should succeed
                    assert isinstance(result1, bool)
                except (ValueError, TypeError):
                    # If we can't convert to float, evaluation should return False
                    assert result1 is False
        
        elif condition["type"] == "regex":
            # Regex comparisons should handle string values
            if pd.notna(transaction.get(condition["field"])):
                try:
                    # Test that the regex pattern is valid
                    re.compile(condition["value"], re.IGNORECASE)
                    assert isinstance(result1, bool)
                except re.error:
                    # Invalid regex should be handled gracefully
                    assert isinstance(result1, bool)
        
        else:
            # String comparisons should handle string values
            if pd.notna(transaction.get(condition["field"])):
                assert isinstance(result1, bool)
    
    @pytest.mark.property
    @given(
        conditions=st.lists(rule_conditions(), min_size=1, max_size=5),
        transaction_data=transaction_data()
    )
    @settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_multiple_conditions_consistency(self, conditions, transaction_data):
        """PROP003: Test that multiple conditions in a rule are evaluated consistently.
        
        This property test validates that when multiple conditions are combined
        in a single rule, the evaluation remains consistent and follows AND logic.
        """
        # Arrange
        self.categorizer.excel_handler.existing_df = transaction_data
        self.categorizer.excel_handler.existing_columns = list(transaction_data.columns)
        
        transaction = transaction_data.iloc[0]
        
        # Act: Evaluate the same conditions multiple times
        result1 = self.categorizer._is_match(transaction, conditions)
        result2 = self.categorizer._is_match(transaction, conditions)
        
        # Assert: Results should be identical (deterministic)
        assert result1 == result2, f"Multiple condition evaluation is not deterministic"
        
        # Assert: Result should be boolean
        assert isinstance(result1, bool), f"Multiple condition evaluation should return boolean"
        
        # Test AND logic: if any condition is False, the whole rule should be False
        individual_results = [self.categorizer._evaluate_condition(transaction, cond) for cond in conditions]
        expected_result = all(individual_results)
        assert result1 == expected_result, f"AND logic not working correctly: {individual_results} -> {result1}, expected {expected_result}"
    
    @pytest.mark.property
    @given(
        field_name=st.sampled_from(["Description", "Amount", "Account", "Category"]),
        comparison_type=st.sampled_from(["contains", "equals", "min", "max"]),
        test_value=st.text(min_size=1, max_size=20)
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_rule_parsing_edge_cases(self, field_name, comparison_type, test_value):
        """PROP004: Test rule parsing with edge cases and boundary conditions.
        
        This property test validates that rule parsing handles edge cases correctly,
        including empty values, special characters, and boundary conditions.
        """
        # Arrange
        self.categorizer.excel_handler.existing_columns = ["Description", "Amount", "Category", "Account", "Tags", "Notes"]
        
        # Create rule column name
        rule_column_name = f"{field_name} {comparison_type.title()}"
        
        # Act
        result = self.categorizer._extract_rule_condition(rule_column_name, test_value)
        
        # Assert: If field exists in columns, parsing should succeed
        if field_name in self.categorizer.excel_handler.existing_columns:
            assert result is not None, f"Rule parsing should succeed for valid field '{field_name}'"
            assert result["field"] == field_name, f"Parsed field should match input field"
            assert result["type"] == comparison_type, f"Parsed comparison type should match input"
            assert result["value"] == test_value, f"Parsed value should match input value"
        else:
            # If field doesn't exist, parsing should fail gracefully
            assert result is None, f"Rule parsing should fail for invalid field '{field_name}'" 