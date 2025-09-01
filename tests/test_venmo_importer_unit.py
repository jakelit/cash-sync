"""
Test module for VenmoImporter class.

This module contains comprehensive tests for the VenmoImporter class,
covering all public methods, error conditions, and edge cases specific to
Venmo's unique CSV format with multi-line headers and ISO datetime formats.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

from src.cash_sync.venmo_importer import VenmoImporter


class TestVenmoImporterInit:
    """Unit tests for VenmoImporter initialization and configuration."""
    
    def test_venmo_importer_initialization(self):
        """Test UT001: Valid initialization creates object successfully."""
        importer = VenmoImporter()
        assert importer is not None
        assert isinstance(importer, VenmoImporter)

    def test_venmo_importer_column_mappings(self):
        """Test UT002: Column mappings are set correctly for Venmo format."""
        importer = VenmoImporter()
        
        # Check that Venmo-specific column mappings are set
        assert importer.column_mappings['Date'] == 'Datetime'
        # Description will be mapped from 'From' or 'To' depending on transaction type
        assert importer.column_mappings['Amount'] == 'Amount (total)'
        assert importer.column_mappings['Transaction Type'] == 'Type'
        
        # Check default values
        assert importer.default_values['Account Number'] == ''
        assert importer.default_values['Balance'] == 0.0

    def test_get_expected_columns(self):
        """Test UT003: Required columns method returns 6 required Venmo columns."""
        importer = VenmoImporter()
        
        expected_columns = importer.get_expected_columns()
        
        # Should return exactly 6 columns as specified in venmo_importer.md
        assert len(expected_columns) == 6
        
        # Check for required Venmo columns
        required_columns = [
            'Datetime',
            'Type', 
            'Note',
            'From',
            'To',
            'Amount (total)'
        ]
        
        for column in required_columns:
            assert column in expected_columns, f"Required column '{column}' not found in expected columns"

    def test_get_institution_name(self):
        """Test UT004: Institution name method returns 'Venmo'."""
        importer = VenmoImporter()
        
        institution_name = importer.get_institution_name()
        
        assert institution_name == "Venmo"

    def test_get_account_name_username_extraction(self):
        """Test UT005: Username extraction from header 'Account Statement - (@testuser)'."""
        importer = VenmoImporter()
        
        # Create a temporary CSV file with Venmo format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("Account Statement - (@testuser) ,,,,,,,,,,,,,,,,,,,,,\n")
            f.write("Account Activity,,,,,,,,,,,,,,,,,,,,,\n")
            f.write(",ID,Datetime,Type,Status,Note,From,To,Amount (total),Amount (tip),Amount (tax),Amount (fee),Tax Rate,Tax Exempt,Funding Source,Destination,Beginning Balance,Ending Balance,Statement Period Venmo Fees,Terminal Location,Year to Date Venmo Fees,Disclaimer\n")
            f.write(",,,,,,,,,,,,,,,,,,,,\"$1,250.00\",,,,,\n")
            temp_csv_file = f.name
        
        try:
            # Read the CSV data which should extract the username
            importer.read_csv_data(temp_csv_file)
            
            # Get the account name which should now return the extracted username
            account_name = importer.get_account_name()
            
            # Should extract "@testuser" from header "Account Statement - (@testuser)"
            assert account_name == "@testuser"
        finally:
            # Clean up temporary file
            os.unlink(temp_csv_file)

    def test_get_account_name_complex_username(self):
        """Test UT006: Complex username with special characters."""
        importer = VenmoImporter()
        
        # Create a temporary CSV file with complex username
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("Account Statement - (@user123_456) ,,,,,,,,,,,,,,,,,,,,,\n")
            f.write("Account Activity,,,,,,,,,,,,,,,,,,,,,\n")
            f.write(",ID,Datetime,Type,Status,Note,From,To,Amount (total),Amount (tip),Amount (tax),Amount (fee),Tax Rate,Tax Exempt,Funding Source,Destination,Beginning Balance,Ending Balance,Statement Period Venmo Fees,Terminal Location,Year to Date Venmo Fees,Disclaimer\n")
            f.write(",,,,,,,,,,,,,,,,,,,,\"$1,250.00\",,,,,\n")
            temp_csv_file = f.name
        
        try:
            # Read the CSV data which should extract the complex username
            importer.read_csv_data(temp_csv_file)
            
            # Get the account name which should now return the extracted username
            account_name = importer.get_account_name()
            
            # Should handle complex usernames with underscores, numbers, etc.
            assert account_name == "@user123_456"
        finally:
            # Clean up temporary file
            os.unlink(temp_csv_file)

    def test_get_account_name_malformed_header(self):
        """Test UT007: Malformed header format returns appropriate error."""
        importer = VenmoImporter()
        
        # Create a temporary CSV file with malformed header (no username)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("Account Statement - No Username Here ,,,,,,,,,,,,,,,,,,,,,\n")
            f.write("Account Activity,,,,,,,,,,,,,,,,,,,,,\n")
            f.write(",ID,Datetime,Type,Status,Note,From,To,Amount (total),Amount (tip),Amount (tax),Amount (fee),Tax Rate,Tax Exempt,Funding Source,Destination,Beginning Balance,Ending Balance,Statement Period Venmo Fees,Terminal Location,Year to Date Venmo Fees,Disclaimer\n")
            f.write(",,,,,,,,,,,,,,,,,,,,\"$1,250.00\",,,,,\n")
            temp_csv_file = f.name
        
        try:
            # Read the CSV data which should handle malformed header gracefully
            importer.read_csv_data(temp_csv_file)
            
            # Get the account name which should return default "Venmo" for malformed header
            account_name = importer.get_account_name()
            
            # Should return default "Venmo" when no username is found in header
            assert account_name == "Venmo"
        finally:
            # Clean up temporary file
            os.unlink(temp_csv_file)

    def test_parse_transaction_date_iso_datetime(self):
        """Test UT008: ISO datetime parsing '2025-06-01T01:39:54'."""
        from datetime import date
        
        importer = VenmoImporter()
        
        # Test ISO datetime format
        iso_datetime = "2025-06-01T01:39:54"
        parsed_date = importer.parse_transaction_date(iso_datetime)
        
        # Should parse to a date object
        assert parsed_date is not None
        assert isinstance(parsed_date, date)
        assert parsed_date.year == 2025
        assert parsed_date.month == 6
        assert parsed_date.day == 1

    def test_parse_transaction_date_timezone_formats(self):
        """Test UT009: Timezone formats - Various ISO formats."""
        from datetime import date
        
        importer = VenmoImporter()
        
        # Test various ISO datetime formats with timezone info
        test_cases = [
            ("2025-06-01T01:39:54Z", date(2025, 6, 1)),  # UTC timezone
            ("2025-06-01T01:39:54-05:00", date(2025, 6, 1)),  # EST timezone
            ("2025-06-01T01:39:54+00:00", date(2025, 6, 1)),  # UTC with offset
            ("2025-06-01T01:39:54-08:00", date(2025, 6, 1)),  # PST timezone
        ]
        
        for iso_datetime, expected_date in test_cases:
            parsed_date = importer.parse_transaction_date(iso_datetime)
            
            # Should parse to a date object
            assert parsed_date is not None, f"Failed to parse: {iso_datetime}"
            assert isinstance(parsed_date, date), f"Not a date object: {iso_datetime}"
            assert parsed_date == expected_date, f"Date mismatch for {iso_datetime}: expected {expected_date}, got {parsed_date}"

    def test_parse_transaction_date_invalid_iso_format(self):
        """Test UT010: Invalid ISO format - Malformed datetime."""
        import logging
        
        importer = VenmoImporter()
        
        # Test various malformed datetime strings that pandas cannot parse
        invalid_datetime_strings = [
            "not-a-datetime",
            "2025-13-01T01:39:54",  # Invalid month (13)
            "2025-06-32T01:39:54",  # Invalid day (32)
            "2025-06-01T25:39:54",  # Invalid hour (25)
            "2025-06-01T01:60:54",  # Invalid minute (60)
            "2025-06-01T01:39:60",  # Invalid second (60)
            "2025-06-01T01:39:54+99:00",  # Invalid timezone offset
            "completely-invalid-date",  # Non-date string
            "2025-XX-01T01:39:54",  # Invalid characters
            "",  # Empty string
            None,  # None value
        ]
        
        for invalid_datetime in invalid_datetime_strings:
            parsed_date = importer.parse_transaction_date(invalid_datetime)
            
            # Should return None for invalid datetime strings
            assert parsed_date is None, f"Expected None for invalid datetime '{invalid_datetime}', but got {parsed_date}"

    def test_parse_transaction_amount_positive_amount(self):
        """Test UT011: Positive amount - '+ $25.00'."""
        importer = VenmoImporter()
        
        # Test positive amount with Venmo format
        positive_amount = "+ $25.00"
        parsed_amount = importer.parse_transaction_amount(positive_amount)
        
        # Should parse to positive float value
        assert parsed_amount is not None
        assert isinstance(parsed_amount, float)
        assert parsed_amount == 25.00
        assert parsed_amount > 0  # Should be positive

    def test_parse_transaction_amount_negative_amount(self):
        """Test UT012: Negative amount - '- $150.00'."""
        importer = VenmoImporter()
        
        # Test negative amount with Venmo format
        negative_amount = "- $150.00"
        parsed_amount = importer.parse_transaction_amount(negative_amount)
        
        # Should parse to negative float value
        assert parsed_amount is not None
        assert isinstance(parsed_amount, float)
        assert parsed_amount == -150.00
        assert parsed_amount < 0  # Should be negative

    def test_parse_transaction_amount_zero_amount(self):
        """Test UT013: Zero amount - '$0.00'."""
        importer = VenmoImporter()
        
        # Test zero amount with Venmo format
        zero_amount = "$0.00"
        parsed_amount = importer.parse_transaction_amount(zero_amount)
        
        # Should parse to zero float value
        assert parsed_amount is not None
        assert isinstance(parsed_amount, float)
        assert parsed_amount == 0.00
        assert parsed_amount == 0  # Should be exactly zero

    def test_parse_transaction_amount_comma_separated_numbers(self):
        """Test UT014: Comma-separated numbers - '+ $1,000.00'."""
        importer = VenmoImporter()
        
        # Test comma-separated positive amount with Venmo format
        comma_amount = "+ $1,000.00"
        parsed_amount = importer.parse_transaction_amount(comma_amount)
        
        # Should parse to positive float value with commas removed
        assert parsed_amount is not None
        assert isinstance(parsed_amount, float)
        assert parsed_amount == 1000.00
        assert parsed_amount > 0  # Should be positive
        
        # Test comma-separated negative amount
        comma_negative_amount = "- $1,500.00"
        parsed_negative_amount = importer.parse_transaction_amount(comma_negative_amount)
        
        # Should parse to negative float value with commas removed
        assert parsed_negative_amount is not None
        assert isinstance(parsed_negative_amount, float)
        assert parsed_negative_amount == -1500.00
        assert parsed_negative_amount < 0  # Should be negative

    def test_parse_transaction_amount_additional_formats(self):
        """Test UT015: Additional currency formats - More robust parsing."""
        importer = VenmoImporter()
        
        # Test various additional valid currency formats
        test_cases = [
            ("25.00", 25.00),  # Plain numeric format
            ("+25.00", 25.00),  # Positive without dollar sign
            ("-25.00", -25.00),  # Negative without dollar sign
            ("$25", 25.00),  # Dollar sign without cents
            ("$25.00", 25.00),  # Dollar sign with cents
            ("+$25.00", 25.00),  # Positive with dollar sign (no space)
            ("-$25.00", -25.00),  # Negative with dollar sign (no space)
            ("1,000.00", 1000.00),  # Plain numeric with commas
            ("+1,000.00", 1000.00),  # Positive with commas
            ("-1,000.00", -1000.00),  # Negative with commas
            ("$1,000.00", 1000.00),  # Dollar sign with commas
            ("+$1,000.00", 1000.00),  # Positive dollar sign with commas
            ("-$1,000.00", -1000.00),  # Negative dollar sign with commas
        ]
        
        for amount_str, expected_amount in test_cases:
            parsed_amount = importer.parse_transaction_amount(amount_str)
            assert parsed_amount == expected_amount, f"Expected {expected_amount} for '{amount_str}', but got {parsed_amount}"

    def test_parse_transaction_amount_invalid_format(self):
        """Test UT016: Invalid format - Non-currency string."""
        importer = VenmoImporter()
        
        # Test various truly invalid currency formats
        invalid_amounts = [
            "not-a-currency",
            "25 dollars",  # Text instead of currency
            "25.00 USD",  # Currency code instead of dollar sign
            "25.00€",  # Wrong currency symbol
            "25.00£",  # Wrong currency symbol
            "25.00¥",  # Wrong currency symbol
            "25.00%",  # Percentage instead of currency
            "25.00x",  # Invalid suffix
            "x25.00",  # Invalid prefix
            "25.00.00",  # Multiple decimal points
            "25..00",  # Multiple decimal points
            "25.00.00.00",  # Multiple decimal points
            "25.00.00.00.00",  # Multiple decimal points
        ]
        
        for invalid_amount in invalid_amounts:
            parsed_amount = importer.parse_transaction_amount(invalid_amount)
            
            # Should return 0.0 for invalid currency formats
            assert parsed_amount == 0.0, f"Expected 0.0 for invalid amount '{invalid_amount}', but got {parsed_amount}"
