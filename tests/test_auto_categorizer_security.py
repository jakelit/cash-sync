"""
Security tests for AutoCategorizer class.

Covers:
- TC072: File access validation (invalid paths, permissions)
- TC073: Input sanitization (malicious Excel content)
"""

import sys
import os
import pytest
from unittest.mock import patch, Mock
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from excel_finance_tools.auto_categorizer import AutoCategorizer

@pytest.mark.security
class TestAutoCategorizerSecurity:
    """Security tests for AutoCategorizer (TC072, TC073)."""

    def test_init_invalid_file_path(self):
        """TC072: __init__() should raise FileNotFoundError for invalid file path."""
        with patch('excel_finance_tools.auto_categorizer.ExcelHandler') as mock_handler:
            mock_handler.side_effect = FileNotFoundError("File not found")
            with pytest.raises(FileNotFoundError, match="File not found"):
                AutoCategorizer("/invalid/path/to/file.xlsx")

    def test_init_permission_error(self):
        """TC072: __init__() should raise PermissionError for inaccessible file."""
        with patch('excel_finance_tools.auto_categorizer.ExcelHandler') as mock_handler:
            mock_handler.side_effect = PermissionError("Permission denied")
            with pytest.raises(PermissionError, match="Permission denied"):
                AutoCategorizer("/protected/file.xlsx")

    def test_load_rules_malformed_excel(self):
        """TC073: load_rules() should handle malformed Excel content safely."""
        # Patch ExcelHandler to return a DataFrame with malicious/invalid columns
        with patch('excel_finance_tools.auto_categorizer.ExcelHandler') as mock_handler_class:
            mock_handler = Mock()
            # Simulate a DataFrame with a malicious column name and missing 'Category'
            malicious_df = pd.DataFrame({
                'DROP TABLE Transactions;': ['malicious'],
                'Description Contains': ['WALMART']
            })
            mock_handler.get_autocat_rules.return_value = malicious_df
            mock_handler.existing_columns = ['Description', 'Amount', 'Category', 'Account']
            mock_handler_class.return_value = mock_handler
            categorizer = AutoCategorizer("dummy.xlsx")
            # Should not raise, but should log error and set rules to []
            categorizer._load_and_parse_rules()
            assert categorizer.rules == [], "Malformed rules should not be loaded."

    def test_load_rules_missing_category_column(self, caplog):
        """TC073: load_rules() should log error and not crash if 'Category' column is missing."""
        with patch('excel_finance_tools.auto_categorizer.ExcelHandler') as mock_handler_class:
            mock_handler = Mock()
            # DataFrame missing 'Category' column
            df = pd.DataFrame({
                'Description Contains': ['WALMART'],
                'Amount Min': [100]
            })
            mock_handler.get_autocat_rules.return_value = df
            mock_handler.existing_columns = ['Description', 'Amount', 'Category', 'Account']
            mock_handler_class.return_value = mock_handler
            categorizer = AutoCategorizer("dummy.xlsx")
            with caplog.at_level('ERROR'):
                categorizer._load_and_parse_rules()
                assert any('must contain a' in m for m in caplog.messages), "Should log error for missing Category column."
                assert categorizer.rules == [], "Rules should be empty if Category column is missing." 