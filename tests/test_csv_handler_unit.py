import pytest
from excel_finance_tools.csv_handler import CSVHandler

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