import pytest
from excel_finance_tools.duplicate_checker import DuplicateChecker
import pandas as pd

class TestDuplicateCheckerUnit:
    """Unit tests for DuplicateChecker class."""

    @pytest.mark.unit
    def test_create_comparison_key_valid(self):
        """UT021: Valid transaction key - Should filter out duplicate if all fields match (normalized)."""        
        existing_df = pd.DataFrame([
            {'Date': '2024-01-01', 'Amount': '-10.50', 'Full Description': 'Starbucks Coffee #1234'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': '-10.50', 'Full Description': 'Starbucks Coffee #1234'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []

    @pytest.mark.unit
    def test_create_comparison_key_missing_fields(self):
        """UT022: Missing fields key - Should treat missing fields as empty and not match existing."""
        existing_df = pd.DataFrame([
            {'Date': '', 'Amount': '5.00', 'Full Description': ''}
        ])
        new_txns = [
            {'Amount': '5.00'}  # Missing Date and Description
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        # Should be filtered as duplicate
        assert filtered == []

    @pytest.mark.unit
    def test_create_comparison_key_date_normalization(self):
        """UT023: Date normalization - Should match even if date formats differ but represent same date."""
        existing_df = pd.DataFrame([
            {'Date': '2024-01-02', 'Amount': '1.00', 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': '01/02/2024', 'Amount': '1.00', 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []

    @pytest.mark.unit
    def test_create_comparison_key_amount_normalization(self):
        """UT024: Amount normalization - Should match even if amount formats differ but represent same value."""
        existing_df = pd.DataFrame([
            {'Date': '2024-01-01', 'Amount': '5.00', 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': 5, 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []

    @pytest.mark.unit
    def test_create_comparison_key_description_fallback(self):
        """UT025: Description fallback - Should match if Description matches and Full Description is missing."""
        existing_df = pd.DataFrame([
            {'Date': '2024-01-01', 'Amount': '1.00', 'Description': 'Test Desc'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': '1.00', 'Description': 'Test Desc'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []

    @pytest.mark.unit
    def test_check_for_duplicates_empty_existing(self):
        """UT026: Empty existing data - All new transactions should be returned if existing is empty."""
        existing_df = pd.DataFrame([])
        new_txns = [{'Date': '2024-01-01', 'Amount': '1.00', 'Full Description': 'A'}]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == new_txns

    @pytest.mark.unit
    def test_check_for_duplicates_empty_new(self):
        """UT027: Empty new data - Should return empty list if no new transactions."""
        existing_df = pd.DataFrame([{'Date': '2024-01-01', 'Amount': '1.00', 'Full Description': 'A'}])
        filtered = DuplicateChecker.check_for_duplicates(existing_df, [])
        assert filtered == []

    @pytest.mark.unit
    def test_check_for_duplicates_exact_duplicate(self):
        """UT028: Exact duplicate detection - Should filter out identical transaction data."""
        existing_df = pd.DataFrame([{'Date': '2024-01-01', 'Amount': '1.00', 'Full Description': 'A'}])
        new_txns = [{'Date': '2024-01-01', 'Amount': '1.00', 'Full Description': 'A'}]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []

    @pytest.mark.unit
    def test_check_for_duplicates_partial_duplicate(self):
        """UT029: Partial duplicate detection - Should include transaction if description differs."""
        existing_df = pd.DataFrame([{'Date': '2024-01-01', 'Amount': '1.00', 'Full Description': 'A'}])
        new_txns = [{'Date': '2024-01-01', 'Amount': '1.00', 'Full Description': 'B'}]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == new_txns

    @pytest.mark.unit
    def test_check_for_duplicates_multiple_duplicates(self):
        """UT030: Multiple duplicates - Should filter out all duplicates and return only unique transactions."""
        existing_df = pd.DataFrame([
            {'Date': '2024-01-01', 'Amount': '1.00', 'Full Description': 'A'},
            {'Date': '2024-01-02', 'Amount': '2.00', 'Full Description': 'B'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': '1.00', 'Full Description': 'A'},  # duplicate
            {'Date': '2024-01-02', 'Amount': '2.00', 'Full Description': 'B'},  # duplicate
            {'Date': '2024-01-03', 'Amount': '3.00', 'Full Description': 'C'}   # unique
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == [{'Date': '2024-01-03', 'Amount': '3.00', 'Full Description': 'C'}]