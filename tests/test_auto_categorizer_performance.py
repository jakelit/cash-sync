"""
Performance tests for AutoCategorizer class.

This module contains performance tests for the AutoCategorizer class,
focusing on large datasets, complex rules, and memory usage validation.
"""

import sys
import os
import time
import psutil
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from excel_finance_tools.auto_categorizer import AutoCategorizer
from excel_finance_tools.excel_handler import ExcelHandler


class TestAutoCategorizerPerformance:
    """Test performance with large datasets and complex rule sets."""
    
    @pytest.fixture
    def large_transactions_df(self):
        """Create a large dataset of transactions for performance testing."""
        # Generate 10,000 transactions with realistic data
        np.random.seed(42)  # For reproducible results
        
        descriptions = [
            "WALMART GROCERY", "SHELL GAS STATION", "STARBUCKS COFFEE",
            "AMAZON PURCHASE", "NETFLIX SUBSCRIPTION", "SPOTIFY PREMIUM",
            "UBER RIDE", "DOORDASH DELIVERY", "TARGET SHOPPING",
            "COSTCO WHOLESALE", "HOME DEPOT", "LOWES HOME IMPROVEMENT"
        ]
        
        data = {
            "Description": np.random.choice(descriptions, 10000),
            "Amount": np.random.uniform(5.0, 500.0, 10000).round(2),
            "Category": [""] * 10000,  # All uncategorized
            "Account": np.random.choice(["Checking", "Savings", "Credit"], 10000),
            "Date": pd.date_range(start="2024-01-01", periods=10000, freq="h")
        }
        
        return pd.DataFrame(data)
    
    @pytest.fixture
    def many_rules_df(self):
        """Create a dataset with many valid rules for performance testing."""
        rules = []
        # Generate 100 rules with at least one valid condition and non-empty Category
        for i in range(100):
            rule = {
                "Category": f"Category_{i % 20}",
                # Always at least one valid rule column, matching transaction columns
                "Description Contains": f"PATTERN_{i}",
                "Amount Min": str(i * 10) if i % 4 == 0 else "",
                "Amount Max": str((i + 1) * 50) if i % 5 == 0 else "",
                "Account Equals": f"Checking" if i % 6 == 0 else "",
                # Only valid comparison types and columns
                # No empty rules: at least Description Contains is always filled
            }
            rules.append(rule)
        return pd.DataFrame(rules)
    
    @pytest.fixture
    def complex_rules_df(self):
        """Create complex rules with valid columns and multiple conditions."""
        rules = [
            {
                "Category": "Groceries",
                "Description Contains": "WALMART",
                "Amount Min": "10",
                "Amount Max": "200",
                "Account Equals": "Checking"
            },
            {
                "Category": "Gas",
                "Description Contains": "SHELL",
                "Amount Min": "20",
                "Amount Max": "100",
                "Account Equals": "Checking"
            },
            {
                "Category": "Entertainment",
                "Description Contains": "NETFLIX",
                "Amount Min": "10",
                "Amount Max": "20",
                "Account Equals": "Checking"
            },
            {
                "Category": "Transportation",
                "Description Contains": "UBER",
                "Amount Min": "5",
                "Amount Max": "50",
                "Account Equals": "Checking"
            }
        ]
        return pd.DataFrame(rules)
    
    @pytest.fixture
    def mock_excel_handler(self):
        """Mock ExcelHandler for performance testing."""
        with patch('excel_finance_tools.auto_categorizer.ExcelHandler') as mock:
            handler_instance = Mock()
            handler_instance.existing_df = pd.DataFrame()
            handler_instance.existing_columns = ["Description", "Amount", "Category", "Account"]
            handler_instance.update_cell = Mock()
            mock.return_value = handler_instance
            yield mock.return_value
    
    @pytest.mark.performance
    def test_large_dataset_performance(self, large_transactions_df, mock_excel_handler):
        """TC062: Test performance with 10,000 transactions."""
        # Arrange
        mock_excel_handler.existing_df = large_transactions_df
        mock_excel_handler.existing_columns = list(large_transactions_df.columns)
        # Valid rules DataFrame
        rules_df = pd.DataFrame([
            {"Category": "Groceries", "Description Contains": "WALMART", "Amount Max": "500"},
            {"Category": "Gas", "Description Contains": "SHELL"},
            {"Category": "Coffee", "Description Contains": "STARBUCKS", "Amount Max": "20"}
        ])
        
        with patch('pandas.read_excel') as mock_read:
            mock_read.return_value = rules_df
            # Set up the mock before creating AutoCategorizer
            mock_excel_handler.get_autocat_rules.return_value = rules_df
            
            categorizer = AutoCategorizer("dummy_file.xlsx")
            categorizer.excel_handler = mock_excel_handler
            
            # Act & Assert - Should complete within 30 seconds
            start_time = time.time()
            result = categorizer.run_auto_categorization()
            execution_time = time.time() - start_time
            assert result[0] is True
            assert execution_time < 30.0, f"Performance test failed: {execution_time:.2f}s > 30s"
            update_calls = mock_excel_handler.update_cell.call_count
            assert update_calls > 0, "No transactions were categorized"
    
    @pytest.mark.performance
    def test_many_rules_performance(self, large_transactions_df, many_rules_df, mock_excel_handler):
        """TC063: Test performance with 100 rules."""
        # Arrange
        mock_excel_handler.existing_df = large_transactions_df
        mock_excel_handler.existing_columns = list(large_transactions_df.columns)
        with patch('pandas.read_excel') as mock_read:
            mock_read.return_value = many_rules_df
            # Set up the mock before creating AutoCategorizer
            mock_excel_handler.get_autocat_rules.return_value = many_rules_df
            
            categorizer = AutoCategorizer("dummy_file.xlsx")
            categorizer.excel_handler = mock_excel_handler
            # Act & Assert - Should complete within 60 seconds
            start_time = time.time()
            result = categorizer.run_auto_categorization()
            execution_time = time.time() - start_time
            assert result[0] is True
            assert execution_time < 60.0, f"Performance test failed: {execution_time:.2f}s > 60s"
            assert len(categorizer.rules) > 0, "No rules were loaded"
    
    @pytest.mark.performance
    def test_complex_rules_performance(self, large_transactions_df, complex_rules_df, mock_excel_handler):
        """TC064: Test performance with complex regex and multiple conditions."""
        # Arrange
        mock_excel_handler.existing_df = large_transactions_df
        mock_excel_handler.existing_columns = list(large_transactions_df.columns)
        with patch('pandas.read_excel') as mock_read:
            mock_read.return_value = complex_rules_df
            # Set up the mock before creating AutoCategorizer
            mock_excel_handler.get_autocat_rules.return_value = complex_rules_df
            
            categorizer = AutoCategorizer("dummy_file.xlsx")
            categorizer.excel_handler = mock_excel_handler
            # Act & Assert - Should complete within 45 seconds
            start_time = time.time()
            result = categorizer.run_auto_categorization()
            execution_time = time.time() - start_time
            assert result[0] is True
            assert execution_time < 45.0, f"Performance test failed: {execution_time:.2f}s > 45s"
            assert len(categorizer.rules) == len(complex_rules_df), "Not all complex rules were loaded"
    
    @pytest.mark.performance
    def test_memory_usage_performance(self, large_transactions_df, many_rules_df, mock_excel_handler):
        """TC065: Test memory usage stays within acceptable limits."""
        # Arrange
        mock_excel_handler.existing_df = large_transactions_df
        mock_excel_handler.existing_columns = list(large_transactions_df.columns)
        with patch('pandas.read_excel') as mock_read:
            mock_read.return_value = many_rules_df
            categorizer = AutoCategorizer("dummy_file.xlsx")
            categorizer.excel_handler = mock_excel_handler
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            result = categorizer.run_auto_categorization()
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            assert result[0] is True
            assert memory_increase < 500, f"Memory usage increased by {memory_increase:.2f}MB > 500MB"
            assert final_memory < 1024, f"Total memory usage {final_memory:.2f}MB > 1GB"
    
    @pytest.mark.performance
    def test_large_dataset_throughput(self, large_transactions_df, mock_excel_handler):
        """Test throughput with large dataset."""
        # Arrange
        mock_excel_handler.existing_df = large_transactions_df
        mock_excel_handler.existing_columns = list(large_transactions_df.columns)
        rules_df = pd.DataFrame([
            {"Category": "Groceries", "Description Contains": "WALMART"}
        ])
        with patch('pandas.read_excel') as mock_read:
            mock_read.return_value = rules_df
            categorizer = AutoCategorizer("dummy_file.xlsx")
            categorizer.excel_handler = mock_excel_handler
            # Act
            start_time = time.time()
            result = categorizer.run_auto_categorization()
            execution_time = time.time() - start_time
            # Calculate throughput
            transactions_per_second = len(large_transactions_df) / execution_time
            # Assert
            assert result[0] is True
            assert transactions_per_second > 100, f"Throughput too low: {transactions_per_second:.2f} tx/s < 100 tx/s"
    
    @pytest.mark.performance
    def test_concurrent_rule_evaluation(self, large_transactions_df, many_rules_df, mock_excel_handler):
        """Test performance with many rules against large dataset."""
        # Arrange
        mock_excel_handler.existing_df = large_transactions_df
        mock_excel_handler.existing_columns = list(large_transactions_df.columns)
        with patch('pandas.read_excel') as mock_read:
            mock_read.return_value = many_rules_df
            categorizer = AutoCategorizer("dummy_file.xlsx")
            categorizer.excel_handler = mock_excel_handler
            # Act
            start_time = time.time()
            result = categorizer.run_auto_categorization()
            execution_time = time.time() - start_time
            # Calculate rule evaluation rate
            total_evaluations = len(large_transactions_df) * len(many_rules_df)
            evaluations_per_second = total_evaluations / execution_time
            # Assert
            assert result[0] is True
            assert evaluations_per_second > 1000, f"Rule evaluation rate too low: {evaluations_per_second:.2f} eval/s < 1000 eval/s" 