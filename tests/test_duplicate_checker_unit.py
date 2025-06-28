import pytest
from excel_finance_tools.duplicate_checker import DuplicateChecker
import pandas as pd
import numpy as np

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

    @pytest.mark.unit
    def test_create_comparison_key_date_as_pd_timestamp(self):
        """UT067: Date as pd.Timestamp - Should match string date and filter as duplicate."""
        existing_df = pd.DataFrame([
            {'Date': pd.Timestamp('2024-01-01'), 'Amount': '10.00', 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': '10.00', 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []

    @pytest.mark.unit
    def test_create_comparison_key_date_as_datetime(self):
        """UT068: Date as datetime object - Should match string date and filter as duplicate."""
        from datetime import datetime
        import pandas as pd
        existing_df = pd.DataFrame([
            {'Date': datetime(2024, 1, 1), 'Amount': '10.00', 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': '10.00', 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []

    @pytest.mark.unit
    def test_create_comparison_key_date_unparseable_type(self):
        """UT069: Date as unparseable type - Should fallback to str(date_value) and use that in the comparison key."""
        import pandas as pd
        # Case 1: Existing has list, new has string (should NOT match)
        existing_df = pd.DataFrame([
            {'Date': [2024, 1, 1], 'Amount': '10.00', 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': '10.00', 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == new_txns  # Not a duplicate

        # Case 2: Both have the same unparseable type/value (should match)
        existing_df = pd.DataFrame([
            {'Date': [2024, 1, 1], 'Amount': '10.00', 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': [2024, 1, 1], 'Amount': '10.00', 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []  # Is a duplicate

        # Case 3: Dict as date
        existing_df = pd.DataFrame([
            {'Date': {'y':2024,'m':1,'d':1}, 'Amount': '10.00', 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': {'y':2024,'m':1,'d':1}, 'Amount': '10.00', 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []  # Is a duplicate

        # Case 4: Dict vs string (should NOT match)
        existing_df = pd.DataFrame([
            {'Date': {'y':2024,'m':1,'d':1}, 'Amount': '10.00', 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': '10.00', 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == new_txns  # Not a duplicate

    @pytest.mark.unit
    def test_create_comparison_key_date_invalid_string(self):
        """UT070: Date as invalid string - Should fallback to str(date_value) in the comparison key."""
        existing_df = pd.DataFrame([
            {'Date': 'not-a-date', 'Amount': '10.00', 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': 'not-a-date', 'Amount': '10.00', 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []  # Is a duplicate

        # Also test that a different invalid string does not match
        new_txns = [
            {'Date': 'foo', 'Amount': '10.00', 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == new_txns  # Not a duplicate

    @pytest.mark.unit
    def test_create_comparison_key_amount_isna(self):
        """UT071: Amount as None, pd.NA, or numpy.nan - Should treat as empty and set amount_str to ''."""
        # Case 1: Amount is None
        existing_df = pd.DataFrame([
            {'Date': '2024-01-01', 'Amount': None, 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': None, 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []  # Is a duplicate

        # Case 2: Amount is pd.NA
        existing_df = pd.DataFrame([
            {'Date': '2024-01-01', 'Amount': pd.NA, 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': pd.NA, 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []  # Is a duplicate

        # Case 3: Amount is numpy.nan
        existing_df = pd.DataFrame([
            {'Date': '2024-01-01', 'Amount': np.nan, 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': np.nan, 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []  # Is a duplicate

        # Case 4: Amount is empty string
        existing_df = pd.DataFrame([
            {'Date': '2024-01-01', 'Amount': '', 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': '', 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []  # Is a duplicate

    @pytest.mark.unit
    def test_create_comparison_key_amount_invalid_type(self):
        """UT072: Amount as invalid string or unparseable type - Should fallback to str(amount_value) in the comparison key."""
        import pandas as pd
        # Case 1: Amount is a non-numeric string
        existing_df = pd.DataFrame([
            {'Date': '2024-01-01', 'Amount': 'foo', 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': 'foo', 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []  # Is a duplicate

        # Case 2: Amount is a list
        existing_df = pd.DataFrame([
            {'Date': '2024-01-01', 'Amount': [1,2,3], 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': [1,2,3], 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []  # Is a duplicate

        # Case 3: Amount is a dict
        existing_df = pd.DataFrame([
            {'Date': '2024-01-01', 'Amount': {'a':1}, 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': {'a':1}, 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == []  # Is a duplicate

        # Case 4: Amount is a different invalid string (should not match)
        existing_df = pd.DataFrame([
            {'Date': '2024-01-01', 'Amount': 'foo', 'Full Description': 'Test'}
        ])
        new_txns = [
            {'Date': '2024-01-01', 'Amount': 'bar', 'Full Description': 'Test'}
        ]
        filtered = DuplicateChecker.check_for_duplicates(existing_df, new_txns)
        assert filtered == new_txns  # Not a duplicate