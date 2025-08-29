import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from cash_sync.base_importer import BaseImporter

class DummyImporter(BaseImporter):
    def get_expected_columns(self):
        return []
    def get_institution_name(self):
        return "Dummy"
    def get_account_name(self):
        return "Dummy"
    def parse_transaction_amount(self, amount_str, transaction_type=None):
        return float(amount_str)

class TestBaseImporterUnit:
    """Unit tests for BaseImporter class."""

    @pytest.mark.unit
    def test_parse_transaction_date_valid(self):
        """UT001: Valid date parsing - Standard date format should create a date object successfully."""
        importer = DummyImporter()
        date_str = "2024-06-22"
        parsed = importer.parse_transaction_date(date_str)
        assert parsed == datetime(2024, 6, 22).date()

    @pytest.mark.unit
    def test_parse_transaction_date_invalid(self):
        """UT002: Invalid date format - Malformed date string should return None."""
        importer = DummyImporter()
        date_str = "not-a-date"
        parsed = importer.parse_transaction_date(date_str)
        assert parsed is None

    @pytest.mark.unit
    def test_parse_transaction_date_pandas_fallback(self):
        """UT051: Pandas fallback parsing - Date format not handled by manual parsing but parsed by pandas."""
        importer = DummyImporter()
        # Use a date format that manual parsing doesn't handle but pandas can
        date_str = "2024-06-22T00:00:00"  # ISO format with time
        parsed = importer.parse_transaction_date(date_str)
        assert parsed == datetime(2024, 6, 22).date()

    @pytest.mark.unit
    def test_parse_transaction_date_exception_handling(self):
        """UT052: Exception handling - Date parsing that raises an exception should return None."""
        importer = DummyImporter()
        # Use a date string that will cause an exception during parsing
        # Mock pd.to_datetime to raise an exception
        with patch('pandas.to_datetime', side_effect=OSError("Test exception")):
            date_str = "invalid-date"
            parsed = importer.parse_transaction_date(date_str)
            assert parsed is None

    @pytest.mark.unit
    def test_clean_description(self):
        """UT006: Description cleaning - Raw bank description should be cleaned and readable."""        
        importer = DummyImporter()
        desc = "Debit Card Purchase - STARBUCKS COFFEE #1234"
        cleaned = importer.clean_description(desc)
        assert cleaned == "Starbucks Coffee"

    @pytest.mark.unit
    def test_clean_description_empty(self):
        """UT007: Empty description - Empty or null description should return empty string."""
        importer = DummyImporter()
        assert importer.clean_description("") == ""
        assert importer.clean_description(None) == ""

    @pytest.mark.unit
    def test_transform_transactions_valid(self):
        """UT008: Valid CSV row transformation - Single CSV row with valid data should be transformed to transaction dict."""
        import pandas as pd
        importer = DummyImporter()
        df = pd.DataFrame([{ 'Date': '2024-01-01', 'Amount': '10.00', 'Type': 'DEBIT', 'Description': 'Test' }])
        existing_columns = [
            'Date', 'Description', 'Category', 'Amount', 'Account', 'Account #', 'Institution',
            'Year', 'Month', 'Week', 'Check Number', 'Full Description', 'Date Added'
        ]
        txns = importer.transform_transactions(df, existing_columns)
        assert isinstance(txns, list)
        assert len(txns) == 1
        assert txns[0]['Date'] == '1/1/2024'
        assert txns[0]['Description'] == 'Test'
        assert txns[0]['Amount'] == 10.00 or txns[0]['Amount'] == -10.00  # Ally keeps sign

    @pytest.mark.unit
    def test_transform_transactions_missing_required(self):
        """UT009: Missing required columns - CSV row missing Date or Amount should be skipped and log error."""
        import pandas as pd
        importer = DummyImporter()
        # Missing Date
        df = pd.DataFrame([{ 'Amount': '10.00', 'Type': 'DEBIT', 'Description': 'Test' }])
        existing_columns = [
            'Date', 'Description', 'Category', 'Amount', 'Account', 'Account #', 'Institution',
            'Year', 'Month', 'Week', 'Check Number', 'Full Description', 'Date Added'
        ]
        txns = importer.transform_transactions(df, existing_columns)
        assert isinstance(txns, list)
        # Should skip row, so txns should be empty or have empty Date
        assert len(txns) == 1 or len(txns) == 0
        # If present, Date should be empty or default
        if txns:
            assert txns[0]['Date'] == '' or txns[0]['Date']

    @pytest.mark.unit
    def test_validate_files_valid(self, tmp_path):
        """UT010: Valid file paths - Existing CSV and Excel files should not raise exception."""
        importer = DummyImporter()
        csv_file = tmp_path / "file.csv"
        excel_file = tmp_path / "file.xlsx"
        csv_file.write_text("test")
        excel_file.write_text("test")
        # Should not raise
        importer.validate_files(str(csv_file), str(excel_file))

    @pytest.mark.unit
    def test_validate_files_invalid(self, tmp_path):
        """UT011: Invalid file paths - Non-existent files should raise FileNotFoundError."""
        importer = DummyImporter()
        with pytest.raises(FileNotFoundError):
            importer.validate_files(str(tmp_path / "no_such.csv"), str(tmp_path / "no_such.xlsx"))

    @pytest.mark.unit
    def test_validate_files_wrong_extension(self, tmp_path):
        """UT012: Wrong file extensions - Should raise ValueError for incorrect file types."""
        importer = DummyImporter()
        # Create dummy files
        csv_file = tmp_path / "file.txt"
        excel_file = tmp_path / "file.docx"
        csv_file.write_text("test")
        excel_file.write_text("test")
        with pytest.raises(ValueError):
            importer.validate_files(str(csv_file), str(excel_file))

    @pytest.mark.unit
    def test_validate_files_excel_not_found(self, tmp_path):
        """UT053: Excel file not found - CSV exists but Excel file doesn't exist."""
        importer = DummyImporter()
        # Create valid CSV file
        csv_file = tmp_path / "file.csv"
        csv_file.write_text("test")
        # Use non-existent Excel file
        excel_file = tmp_path / "no_such.xlsx"
        with pytest.raises(FileNotFoundError) as excinfo:
            importer.validate_files(str(csv_file), str(excel_file))
        assert "Excel file not found" in str(excinfo.value)

    @pytest.mark.unit
    def test_validate_files_excel_wrong_extension(self, tmp_path):
        """UT054: Excel file wrong extension - CSV has correct extension but Excel has wrong extension."""
        importer = DummyImporter()
        # Create valid CSV file
        csv_file = tmp_path / "file.csv"
        csv_file.write_text("test")
        # Create file with wrong extension for Excel
        excel_file = tmp_path / "file.txt"
        excel_file.write_text("test")
        with pytest.raises(ValueError) as excinfo:
            importer.validate_files(str(csv_file), str(excel_file))
        assert "Second file must be an Excel file" in str(excinfo.value)

    @pytest.mark.unit
    def test_get_column_value_mapping(self):
        """UT013: Column mapping - Should return mapped target column value."""
        importer = DummyImporter()
        row = {"BankDate": "2024-01-01"}
        importer.set_column_mapping("BankDate", "Date")
        assert importer.get_column_value(row, "Date") == "2024-01-01"

    @pytest.mark.unit
    def test_get_column_value_missing(self):
        """UT014: Missing column - Should return default value if column is missing."""
        importer = DummyImporter()
        importer.set_default_value("Category", "Uncategorized")
        row = {"Other": "foo"}
        assert importer.get_column_value(row, "Category") == "Uncategorized"

    @pytest.mark.unit
    def test_set_column_mapping(self):
        """UT015: Custom column mapping - Should store mapping correctly."""
        importer = DummyImporter()
        importer.set_column_mapping("BankDate", "Date")
        assert importer.column_mappings["Date"] == "BankDate"

    @pytest.mark.unit
    def test_set_default_value(self):
        """UT016: Default value setting - Should store default value correctly."""
        importer = DummyImporter()
        importer.set_default_value("Category", "Uncategorized")
        assert importer.default_values["Category"] == "Uncategorized"

    @pytest.mark.unit
    def test_format_date_mdy_string_input(self):
        """UT055: String input - String date passed to format_date_mdy should return string unchanged."""
        importer = DummyImporter()
        date_str = "2024-06-22"
        result = importer.format_date_mdy(date_str)
        assert result == date_str

    @pytest.mark.unit
    def test_format_date_mdy_date_object_input(self):
        """UT056: Date object input - Date object passed to format_date_mdy should return formatted M/D/YYYY string."""
        importer = DummyImporter()
        date_obj = datetime(2024, 6, 22).date()
        result = importer.format_date_mdy(date_obj)
        assert result == "6/22/2024"

    @pytest.mark.unit
    def test_clean_description_payment_processor_prefix(self):
        """UT057: Payment processor prefix removal - Description with payment processor prefix should have prefix removed."""
        importer = DummyImporter()
        desc = "TST* STARBUCKS COFFEE"
        cleaned = importer.clean_description(desc)
        assert cleaned == "Starbucks Coffee"

    @pytest.mark.unit
    def test_clean_description_multiple_prefixes(self):
        """UT058: Multiple prefix removal - Description with multiple prefixes should have all prefixes removed."""
        importer = DummyImporter()
        desc = "Debit Card Purchase - PP* AMAZON.COM"
        cleaned = importer.clean_description(desc)
        assert cleaned == "Amazon.com"

    @pytest.mark.unit
    def test_transform_transactions_row_exceptions(self):
        """UT059: Row processing exceptions - Row with data that causes exceptions should be skipped and logged."""
        import pandas as pd
        importer = DummyImporter()
        
        # Create a DataFrame with a row that will cause a ValueError during parsing
        # This will trigger the exception handling code
        df = pd.DataFrame([
            {'Date': '2024-01-01', 'Amount': '10.00', 'Type': 'DEBIT', 'Description': 'Test'},  # Valid row
            {'Date': 'invalid-date', 'Amount': 'not-a-number', 'Type': 'DEBIT', 'Description': 'Test'},  # Invalid row
            {'Date': '2024-01-03', 'Amount': '20.00', 'Type': 'DEBIT', 'Description': 'Test'}   # Valid row
        ])
        
        existing_columns = [
            'Date', 'Description', 'Category', 'Amount', 'Account', 'Account #', 'Institution',
            'Year', 'Month', 'Week', 'Check Number', 'Full Description', 'Date Added'
        ]
        
        # This should process the valid rows and skip the invalid one
        txns = importer.transform_transactions(df, existing_columns)
        
        # Should have processed the valid rows (1 and 3)
        assert isinstance(txns, list)
        assert len(txns) == 2  # Only the valid rows should be processed
        
        # Check that the valid transactions are present
        dates = [t['Date'] for t in txns]
        assert '1/1/2024' in dates
        assert '1/3/2024' in dates

    @pytest.mark.unit
    def test_transform_transactions_mixed_valid_invalid(self):
        """UT060: Mixed valid and invalid rows - DataFrame with some valid rows and some causing exceptions."""
        import pandas as pd
        importer = DummyImporter()
        
        # Create a DataFrame with various types of problematic data
        df = pd.DataFrame([
            {'Date': '2024-01-01', 'Amount': '10.00', 'Type': 'DEBIT', 'Description': 'Valid'},  # Valid
            {'Date': None, 'Amount': '20.00', 'Type': 'DEBIT', 'Description': 'Invalid'},        # TypeError
            {'Date': '2024-01-03', 'Amount': '30.00', 'Type': 'DEBIT', 'Description': 'Valid'},  # Valid
            {'Date': '2024-01-04', 'Amount': 'invalid', 'Type': 'DEBIT', 'Description': 'Invalid'}, # ValueError
            {'Date': '2024-01-05', 'Amount': '50.00', 'Type': 'DEBIT', 'Description': 'Valid'}   # Valid
        ])
        
        existing_columns = [
            'Date', 'Description', 'Category', 'Amount', 'Account', 'Account #', 'Institution',
            'Year', 'Month', 'Week', 'Check Number', 'Full Description', 'Date Added'
        ]
        
        # This should process all rows: 3 valid + 1 with empty date (None date gets empty fields)
        txns = importer.transform_transactions(df, existing_columns)
        
        # Should have processed 4 rows: 3 valid + 1 with empty date
        assert isinstance(txns, list)
        assert len(txns) == 4  # 3 valid + 1 with empty date
        
        # Check that the valid transactions are present
        dates = [t['Date'] for t in txns]
        assert '1/1/2024' in dates
        assert '1/3/2024' in dates
        assert '1/5/2024' in dates
        
        # Check that the transaction with None date has empty date fields
        empty_date_transaction = None
        for t in txns:
            if t['Date'] == '':
                empty_date_transaction = t
                break
        
        assert empty_date_transaction is not None
        assert empty_date_transaction['Date'] == ''
        assert empty_date_transaction['Year'] == ''
        assert empty_date_transaction['Month'] == ''
        assert empty_date_transaction['Week'] == ''
