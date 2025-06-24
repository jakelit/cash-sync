import pytest
from excel_finance_tools.capital_one_importer import CapitalOneImporter

class TestCapitalOneImporterUnit:
    """Unit tests for CapitalOneImporter class."""

    @pytest.mark.unit
    def test_parse_transaction_amount_positive(self):
        """UT003: Positive amount parsing - Credit transaction amount should return positive float value."""        
        cap1 = CapitalOneImporter()
        assert cap1.parse_transaction_amount("123.45", "credit") == 123.45

    @pytest.mark.unit
    def test_parse_transaction_amount_negative(self):
        """UT004: Negative amount parsing - Debit transaction amount should return negative float value."""
        cap1 = CapitalOneImporter()
        assert cap1.parse_transaction_amount("67.89", "debit") == -67.89

    @pytest.mark.unit
    def test_parse_transaction_amount_invalid(self):
        """UT005: Invalid amount format - Non-numeric amount string should raise ValueError or return 0.0."""
        cap1 = CapitalOneImporter()
        assert cap1.parse_transaction_amount("notanumber") == 0.0
   
    @pytest.mark.unit
    def test_get_expected_columns(self):
        """UT018: Capital One columns - Should return Capital One columns."""
        from excel_finance_tools.capital_one_importer import CapitalOneImporter
        cap1 = CapitalOneImporter()
        expected = [
            'Account Number',
            'Transaction Description',
            'Transaction Date',
            'Transaction Type',
            'Transaction Amount',
            'Balance'
        ]
        assert cap1.get_expected_columns() == expected

    @pytest.mark.unit
    def test_get_institution_name(self):
        """UT019: Institution name - Should return institution name for CapitalOneImporter."""
        from excel_finance_tools.capital_one_importer import CapitalOneImporter
        cap1 = CapitalOneImporter()
        assert cap1.get_institution_name() == "Capital One"

    @pytest.mark.unit
    def test_get_account_name(self):
        """UT020: Account name - Should return account name for CapitalOneImporter."""
        from excel_finance_tools.capital_one_importer import CapitalOneImporter
        cap1 = CapitalOneImporter()
        assert cap1.get_account_name() == "Capital One"