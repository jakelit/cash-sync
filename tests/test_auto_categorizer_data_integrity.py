"""
Data integrity tests for AutoCategorizer class.

This module contains data integrity tests for the AutoCategorizer class,
focusing on ensuring only uncategorized transactions are modified and
proper audit trail functionality.
"""

import sys
import os
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from excel_finance_tools.auto_categorizer import AutoCategorizer
from excel_finance_tools.excel_handler import ExcelHandler


class TestAutoCategorizerDataIntegrity:
    """Test data integrity and audit trail functionality."""
    
    @pytest.fixture
    def mixed_transactions_df(self):
        """Create transactions with both categorized and uncategorized entries."""
        return pd.DataFrame({
            "Description": [
                "WALMART GROCERY",      # Uncategorized
                "SHELL GAS STATION",    # Uncategorized  
                "STARBUCKS COFFEE",     # Uncategorized
                "AMAZON PURCHASE",      # Already categorized
                "NETFLIX SUBSCRIPTION", # Already categorized
                "PAYROLL DEPOSIT"       # Already categorized
            ],
            "Amount": [150.00, 45.50, 5.75, 89.99, 15.99, 2500.00],
            "Category": [
                "",           # Uncategorized
                "",           # Uncategorized
                "",           # Uncategorized
                "Shopping",   # Already categorized
                "Entertainment", # Already categorized
                "Income"      # Already categorized
            ],
            "Account": ["Checking"] * 6,
            "Tags": ["", "", "", "online", "subscription", "salary"],
            "Notes": ["", "", "", "Online purchase", "Monthly subscription", "Monthly salary"]
        })
    
    @pytest.fixture
    def valid_rules_df(self):
        """Create valid rules for testing."""
        return pd.DataFrame([
            {
                "Category": "Groceries",
                "Description Contains": "WALMART",
                "Tags": "shopping",
                "Notes": "Grocery expense"
            },
            {
                "Category": "Gas",
                "Description Contains": "SHELL",
                "Tags": "fuel",
                "Notes": "Gas station purchase"
            },
            {
                "Category": "Coffee",
                "Description Contains": "STARBUCKS",
                "Tags": "beverage",
                "Notes": "Coffee purchase"
            }
        ])
    
    @pytest.fixture
    def mock_excel_handler(self):
        """Mock ExcelHandler for data integrity testing."""
        with patch('excel_finance_tools.auto_categorizer.ExcelHandler') as mock:
            handler_instance = Mock()
            handler_instance.existing_df = pd.DataFrame()
            handler_instance.existing_columns = ["Description", "Amount", "Category", "Account", "Tags", "Notes"]
            handler_instance.update_cell = Mock()
            mock.return_value = handler_instance
            yield mock.return_value
    
    @pytest.mark.data_integrity
    def test_categorized_transactions_unchanged(self, mixed_transactions_df, valid_rules_df, mock_excel_handler):
        """TC068: Test that already categorized transactions are not modified."""
        # Arrange
        mock_excel_handler.existing_df = mixed_transactions_df
        mock_excel_handler.existing_columns = list(mixed_transactions_df.columns)
        
        # Store original categorized transactions for comparison
        original_categorized = mixed_transactions_df[
            mixed_transactions_df['Category'].notna() & 
            (mixed_transactions_df['Category'] != '')
        ].copy()
        
        with patch('pandas.read_excel') as mock_read:
            mock_read.return_value = valid_rules_df
            mock_excel_handler.get_autocat_rules.return_value = valid_rules_df
            
            categorizer = AutoCategorizer("dummy_file.xlsx")
            categorizer.excel_handler = mock_excel_handler
            
            # Act
            result = categorizer.run_auto_categorization()
            
            # Assert
            assert result[0] is True, "Auto-categorization should succeed"
            
            # Verify that categorized transactions were not updated
            categorized_indices = mixed_transactions_df[
                mixed_transactions_df['Category'].notna() & 
                (mixed_transactions_df['Category'] != '')
            ].index.tolist()
            uncategorized_indices = mixed_transactions_df[
                mixed_transactions_df['Category'].isna() | 
                (mixed_transactions_df['Category'] == '')
            ].index.tolist()
            
            # Check that update_cell was NOT called for categorized transactions
            update_calls = mock_excel_handler.update_cell.call_args_list
            for call in update_calls:
                row_idx = call[0][0]  # First argument is row index
                assert row_idx in uncategorized_indices, \
                    f"Row {row_idx} should not be updated (already categorized)"
            # Optionally, check that all expected uncategorized rows were updated at least once
            updated_rows = set(call[0][0] for call in update_calls)
            for idx in uncategorized_indices:
                assert idx in updated_rows, f"Uncategorized row {idx} was not updated"
    
    @pytest.mark.data_integrity
    def test_audit_trail_functionality(self, mixed_transactions_df, valid_rules_df, mock_excel_handler):
        """TC069: Test that audit trail entries are created for categorization changes.
        
        This test validates that the AutoCategorizer properly logs all categorization actions
        for audit and debugging purposes. It ensures:
        
        1. **Process Logging**: Start, rule loading, and completion messages are logged
        2. **Transaction Logging**: Each individual categorization is logged with transaction details
        3. **No False Logging**: Already categorized transactions are not logged
        4. **Log Levels**: Summary info at INFO level, detailed transactions at DEBUG level
        
        The audit trail is crucial for:
        - Tracking what changes were made during auto-categorization
        - Debugging categorization issues by seeing which rules matched which transactions
        - Compliance requirements for financial data modifications
        - Understanding system behavior during categorization runs
        """
        # Arrange
        mock_excel_handler.existing_df = mixed_transactions_df
        mock_excel_handler.existing_columns = list(mixed_transactions_df.columns)
        
        # Mock the logger to capture log entries
        with patch('excel_finance_tools.auto_categorizer.logger') as mock_logger:
            with patch('pandas.read_excel') as mock_read:
                mock_read.return_value = valid_rules_df
                mock_excel_handler.get_autocat_rules.return_value = valid_rules_df
                
                categorizer = AutoCategorizer("dummy_file.xlsx")
                categorizer.excel_handler = mock_excel_handler
                
                # Act
                result = categorizer.run_auto_categorization()
                
                # Assert
                assert result[0] is True, "Auto-categorization should succeed"
                
                # Verify that log entries were created for the categorization process
                info_calls = mock_logger.info.call_args_list
                debug_calls = mock_logger.debug.call_args_list
                all_log_calls = info_calls + debug_calls
                
                # Print all log messages for debugging
                print("\n--- Captured INFO log messages ---")
                for call in info_calls:
                    print(str(call))
                print("--- Captured DEBUG log messages ---")
                for call in debug_calls:
                    print(str(call))
                print("--- End log messages ---\n")
                
                # Should have log entries for:
                # 1. Starting auto-categorization
                # 2. Loading rules
                # 3. Processing each uncategorized transaction (DEBUG level)
                # 4. Completion summary
                
                # Check for start of auto-categorization
                start_log_found = any(
                    "Starting auto-categorization" in str(call) or
                    "Auto-categorization started" in str(call)
                    for call in info_calls
                )
                assert start_log_found, "No log entry found for starting auto-categorization"
                
                # Check for rule loading (match actual log message)
                rules_log_found = any(
                    "loaded and parsed" in str(call).lower() or
                    "rules loaded" in str(call).lower() or
                    "loading rules" in str(call).lower()
                    for call in info_calls
                )
                assert rules_log_found, "No log entry found for rule loading"
                
                # Check for transaction processing logs (DEBUG level)
                transaction_logs = [
                    call for call in debug_calls
                    if any(keyword in str(call).lower() 
                          for keyword in ["transaction", "categorized", "matched", "rule", "updating"])
                ]
                assert len(transaction_logs) >= 3, f"Expected at least 3 transaction logs, got {len(transaction_logs)}"
                
                # Check for completion summary
                completion_log_found = any(
                    "successfully categorized" in str(call).lower() or
                    "completed" in str(call).lower() or
                    "finished" in str(call).lower() or
                    "summary" in str(call).lower()
                    for call in info_calls
                )
                assert completion_log_found, "No log entry found for completion summary"
                
                # Verify specific categorization logs for each transaction (DEBUG level)
                # Check for WALMART GROCERY categorization
                walmart_log_found = any(
                    "walmart grocery" in str(call).lower() and "groceries" in str(call).lower()
                    for call in debug_calls
                )
                assert walmart_log_found, "No log entry found for WALMART GROCERY -> Groceries categorization"
                
                # Check for SHELL GAS STATION categorization
                shell_log_found = any(
                    "shell gas station" in str(call).lower() and "gas" in str(call).lower()
                    for call in debug_calls
                )
                assert shell_log_found, "No log entry found for SHELL GAS STATION -> Gas categorization"
                
                # Check for STARBUCKS COFFEE categorization
                starbucks_log_found = any(
                    "starbucks coffee" in str(call).lower() and "coffee" in str(call).lower()
                    for call in debug_calls
                )
                assert starbucks_log_found, "No log entry found for STARBUCKS COFFEE -> Coffee categorization"
                
                # Verify that no log entries were created for already categorized transactions
                categorized_logs = [
                    call for call in all_log_calls
                    if any(keyword in str(call).lower() 
                          for keyword in ["amazon", "netflix", "payroll"])
                ]
                assert len(categorized_logs) == 0, \
                    f"Found {len(categorized_logs)} log entries for already categorized transactions" 