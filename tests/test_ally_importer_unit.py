import pytest
from cash_sync.ally_importer import AllyImporter

class TestAllyImporterUnit:
    """Unit tests for AllyImporter class."""

    @pytest.mark.unit
    def test_parse_transaction_amount_positive(self):
        """UT003: Positive amount parsing - Credit transaction amount should return positive float value."""        
        ally = AllyImporter()
        assert ally.parse_transaction_amount("123.45") == 123.45

    @pytest.mark.unit
    def test_parse_transaction_amount_negative(self):
        """UT004: Negative amount parsing - Debit transaction amount should return negative float value."""
        from cash_sync.ally_importer import AllyImporter
        ally = AllyImporter()
        assert ally.parse_transaction_amount("-67.89") == -67.89

    @pytest.mark.unit
    def test_parse_transaction_amount_invalid(self):
        """UT005: Invalid amount format - Non-numeric amount string should raise ValueError or return 0.0."""
        from cash_sync.ally_importer import AllyImporter
        ally = AllyImporter()
        assert ally.parse_transaction_amount("notanumber") == 0.0   

    @pytest.mark.unit
    def test_get_expected_columns(self):
        """UT017: Ally Bank columns - Should return Ally-specific columns."""
        from cash_sync.ally_importer import AllyImporter
        ally = AllyImporter()
        expected = ["Date", "Time", "Amount", "Type", "Description"]
        assert ally.get_expected_columns() == expected

    @pytest.mark.unit
    def test_get_institution_name(self):
        """UT019: Institution name - Should return institution name for AllyImporter."""
        from cash_sync.ally_importer import AllyImporter
        ally = AllyImporter()
        assert ally.get_institution_name() == "Ally Bank"

    @pytest.mark.unit
    def test_get_account_name(self):
        """UT020: Account name - Should return account name for AllyImporter."""
        from cash_sync.ally_importer import AllyImporter
        ally = AllyImporter()
        assert ally.get_account_name() == "Ally"
