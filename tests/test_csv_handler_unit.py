import pytest
from excel_finance_tools.csv_handler import CSVHandler
import os
import pandas as pd
from unittest.mock import patch

class TestCSVHandlerUnit:
    """Unit tests for CSVHandler class."""

    @pytest.mark.unit
    def test_read_csv_valid(self, tmp_path):
        """UT031: Valid CSV file - Should return DataFrame with transactions."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Date,Amount,Description\n2024-01-01,10.00,Test")
        handler = CSVHandler(str(csv_file))
        df = handler.read_csv()
        assert not df.empty
        assert list(df.columns) == ["Date", "Amount", "Description"]

    @pytest.mark.unit
    def test_read_csv_empty(self, tmp_path):
        """UT032: Empty CSV file - Should raise ValueError for empty file."""
        
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")
        handler = CSVHandler(str(csv_file))
        with pytest.raises(ValueError) as excinfo:
            handler.read_csv()
        assert "No columns to parse from file" in str(excinfo.value)

    @pytest.mark.unit
    def test_read_csv_malformed(self, tmp_path):
        """UT033: Malformed CSV file - Should raise ValueError for malformed file."""
        # Use an unclosed quote to trigger a parser error
        csv_file = tmp_path / "bad.csv"
        csv_file.write_text('Date,Amount,Description\n"2024-01-01,10.00,Test')
        handler = CSVHandler(str(csv_file))
        with pytest.raises(ValueError) as excinfo:
            handler.read_csv()
        assert "Error reading CSV file" in str(excinfo.value)

    @pytest.mark.unit
    def test_validate_columns_valid(self, tmp_path):
        """UT034: Valid column set - Should not raise exception for expected columns."""
        csv_file = tmp_path / "valid.csv"
        csv_file.write_text("Date,Amount,Description\n2024-01-01,10.00,Test")
        handler = CSVHandler(str(csv_file))
        handler.read_csv()  # Load the DataFrame
        handler.validate_columns(["Date", "Amount", "Description"])

    @pytest.mark.unit
    def test_validate_columns_missing_required(self):
        """UT035: Missing required columns - Should raise ValueError if required columns are missing."""
        handler = CSVHandler("dummy.csv")
        handler.df = None
        handler.columns = ["Date", "Description"]
        with pytest.raises(ValueError):
            handler.validate_columns(["Date", "Amount", "Description"])

    @pytest.mark.unit
    def test_validate_file_valid(self, tmp_path):
        """UT061: Valid CSV file - Should not raise exception."""
        csv_file = tmp_path / "file.csv"
        csv_file.write_text("test")
        handler = CSVHandler(str(csv_file))
        handler.validate_file()  # Should not raise

    @pytest.mark.unit
    def test_validate_file_not_found(self, tmp_path):
        """UT062: File not found - Should raise FileNotFoundError."""
        handler = CSVHandler(str(tmp_path / "no_such.csv"))
        with pytest.raises(FileNotFoundError):
            handler.validate_file()

    @pytest.mark.unit
    def test_validate_file_wrong_extension(self, tmp_path):
        """UT063: Wrong file extension - Should raise ValueError."""
        txt_file = tmp_path / "file.txt"
        txt_file.write_text("test")
        handler = CSVHandler(str(txt_file))
        with pytest.raises(ValueError):
            handler.validate_file()

    @pytest.mark.unit
    def test_read_csv_encoding_fallback(self, tmp_path):
        """UT064: Multiple encoding attempts - Should succeed with a later encoding."""
        # Write a Latin-1 encoded CSV file with a special character
        csv_file = tmp_path / "latin1.csv"
        content = 'Date,Amount,Description\n2024-01-01,10.00,CAFÉ\n'
        csv_file.write_bytes(content.encode('latin-1'))
        handler = CSVHandler(str(csv_file))
        df = handler.read_csv()
        assert isinstance(df, pd.DataFrame)
        assert df.loc[0, 'Description'] == 'CAFÉ'

    @pytest.mark.unit
    def test_read_csv_all_encodings_fail(self, tmp_path):
        """UT065: All encodings fail - Should raise ValueError."""
        csv_file = tmp_path / "bad.csv"
        csv_file.write_text("irrelevant")  # Content doesn't matter
        handler = CSVHandler(str(csv_file))
        # Patch pandas.read_csv to always raise UnicodeDecodeError
        with patch("pandas.read_csv", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "fail")):
            with pytest.raises(ValueError):
                handler.read_csv()

    @pytest.mark.unit
    def test_validate_columns_error_message_content(self, tmp_path):
        """UT066: Error message includes available columns and suggestions when required columns are missing."""
        csv_file = tmp_path / "missing_amount.csv"
        csv_file.write_text("Date,Description\n2024-01-01,Test")
        handler = CSVHandler(str(csv_file))
        handler.read_csv()  # Load the DataFrame
        with pytest.raises(ValueError) as excinfo:
            handler.validate_columns(["Date", "Amount", "Description"])
        msg = str(excinfo.value)
        assert "Available columns in your CSV" in msg
        assert "missing some required columns" in msg
        assert "Please check that you selected the correct bank" in msg