"""
Test module for VenmoImporter class.

This module contains comprehensive unit tests for the VenmoImporter class,
covering all public methods, error conditions, and edge cases specific to
Venmo's unique CSV format.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

from cash_sync import VenmoImporter


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
        assert importer._column_mappings['Date'] == 'Datetime'
        # Description will be mapped from 'From' or 'To' depending on transaction type
        assert importer._column_mappings['Amount'] == 'Amount (total)'
        assert importer._column_mappings['Transaction Type'] == 'Type'
        
        # Check default values
        assert importer._default_values['Account Number'] == ''
        assert importer._default_values['Balance'] == 0.0

    def test_get_expected_columns(self):
        """Test UT003: Required columns method returns 6 required Venmo columns."""
        importer = VenmoImporter()
        
        expected_columns = importer._get_expected_columns()
        
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
        
        institution_name = importer._get_institution_name()
        
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
            importer._read_csv_data(temp_csv_file)
            
            # Get the account name which should now return the extracted username
            account_name = importer._get_account_name()
            
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
            importer._read_csv_data(temp_csv_file)
            
            # Get the account name which should now return the extracted username
            account_name = importer._get_account_name()
            
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
            importer._read_csv_data(temp_csv_file)
            
            # Get the account name which should return default "Venmo" for malformed header
            account_name = importer._get_account_name()
            
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
        parsed_date = importer._parse_transaction_date(iso_datetime)
        
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
            parsed_date = importer._parse_transaction_date(iso_datetime)
            
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
            parsed_date = importer._parse_transaction_date(invalid_datetime)
            
            # Should return None for invalid datetime strings
            assert parsed_date is None, f"Expected None for invalid datetime '{invalid_datetime}', but got {parsed_date}"

    def test_parse_transaction_amount_positive_amount(self):
        """Test UT011: Positive amount - '+ $25.00'."""
        importer = VenmoImporter()
        
        # Test positive amount with Venmo format
        positive_amount = "+ $25.00"
        parsed_amount = importer._parse_transaction_amount(positive_amount)
        
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
        parsed_amount = importer._parse_transaction_amount(negative_amount)
        
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
        parsed_amount = importer._parse_transaction_amount(zero_amount)
        
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
        parsed_amount = importer._parse_transaction_amount(comma_amount)
        
        # Should parse to positive float value with commas removed
        assert parsed_amount is not None
        assert isinstance(parsed_amount, float)
        assert parsed_amount == 1000.00
        assert parsed_amount > 0  # Should be positive
        
        # Test comma-separated negative amount
        comma_negative_amount = "- $1,500.00"
        parsed_negative_amount = importer._parse_transaction_amount(comma_negative_amount)
        
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
            parsed_amount = importer._parse_transaction_amount(amount_str)
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
            parsed_amount = importer._parse_transaction_amount(invalid_amount)
            
            # Should return 0.0 for invalid currency formats
            assert parsed_amount == 0.0, f"Expected 0.0 for invalid amount '{invalid_amount}', but got {parsed_amount}"

    def test_transform_transactions_venmo_csv_row(self):
        """Test UT017: Venmo CSV row - Single valid row."""
        importer = VenmoImporter()
        
        # Create a sample Venmo CSV row (as a pandas DataFrame)
        import pandas as pd
        
        venmo_data = {
            'ID': ['1234567890123456789'],
            'Datetime': ['2024-01-15T14:30:22'],
            'Type': ['Payment'],
            'Status': ['Complete'],
            'Note': ['Dinner payment'],
            'From': ['Alex Johnson'],
            'To': ['Sarah Wilson'],
            'Amount (total)': ['- $75.00'],
            'Amount (tip)': [''],
            'Amount (tax)': ['0'],
            'Amount (fee)': ['0'],
            'Tax Rate': ['0'],
            'Tax Exempt': [''],
            'Funding Source': ['Venmo balance'],
            'Destination': ['Venmo'],
            'Beginning Balance': [''],
            'Ending Balance': [''],
            'Statement Period Venmo Fees': [''],
            'Terminal Location': [''],
            'Year to Date Venmo Fees': [''],
            'Disclaimer': ['']
        }
        
        venmo_df = pd.DataFrame(venmo_data)
        
        # Define existing columns that should be in the Excel file
        existing_columns = [
            'Date', 'Description', 'Category', 'Amount', 'Account', 
            'Account #', 'Institution', 'Year', 'Month', 'Week', 
            'Check Number', 'Full Description', 'Date Added'
        ]
        
        # Transform the transaction
        transformed = importer._transform_transactions(venmo_df, existing_columns)
        
        # Should return a list with one transformed transaction
        assert len(transformed) == 1
        
        transaction = transformed[0]
        
        # Check that the transaction has the expected structure
        assert 'Date' in transaction
        assert 'Description' in transaction
        assert 'Amount' in transaction
        assert 'Account' in transaction
        assert 'Institution' in transaction
        
        # Check specific values
        assert transaction['Date'] == '1/15/2024'  # Date only from ISO datetime
        assert transaction['Description'] == 'Sarah Wilson'  # 'To' field for debit
        assert transaction['Amount'] == -75.00  # Negative amount for debit
        assert transaction['Account'] == 'Venmo'  # Default account name
        assert transaction['Institution'] == 'Venmo'

    def test_transform_transactions_multi_line_header(self):
        """Test UT018: Multi-line header - CSV with 3-line header."""
        importer = VenmoImporter()
        
        # Create a temporary CSV file with multi-line header
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("Account Statement - (@testuser) ,,,,,,,,,,,,,,,,,,,,,\n")
            f.write("Account Activity,,,,,,,,,,,,,,,,,,,,,\n")
            f.write(",ID,Datetime,Type,Status,Note,From,To,Amount (total),Amount (tip),Amount (tax),Amount (fee),Tax Rate,Tax Exempt,Funding Source,Destination,Beginning Balance,Ending Balance,Statement Period Venmo Fees,Terminal Location,Year to Date Venmo Fees,Disclaimer\n")
            f.write(",,,,,,,,,,,,,,,,,,,,\"$1,250.00\",,,,,\n")
            f.write(",1234567890123456789,2024-01-15T14:30:22,Payment,Complete,Dinner payment,Alex Johnson,Sarah Wilson,- $75.00,,0,,0,,Venmo balance,,,,,Venmo,,,\n")
            temp_csv_file = f.name
        
        try:
            # Read the CSV data which should handle multi-line header correctly
            df = importer._read_csv_data(temp_csv_file)
            
            # Should have processed the transaction data correctly
            assert len(df) > 0
            assert 'Datetime' in df.columns
            assert 'From' in df.columns
            assert 'To' in df.columns
            assert 'Amount (total)' in df.columns
            
            # Check that the transaction data was read correctly
            assert df.iloc[0]['Datetime'] == '2024-01-15T14:30:22'
            assert df.iloc[0]['From'] == 'Alex Johnson'
            assert df.iloc[0]['To'] == 'Sarah Wilson'
            assert df.iloc[0]['Amount (total)'] == '- $75.00'
            
        finally:
            # Clean up temporary file
            os.unlink(temp_csv_file)

    def test_transform_transactions_from_to_mapping(self):
        """Test UT019: From/To mapping - Transaction with From/To should use correct description logic."""
        importer = VenmoImporter()
        
        # Create test data for both debit and credit transactions
        import pandas as pd
        
        # Test data: one debit (money sent) and one credit (money received)
        venmo_data = {
            'ID': ['1234567890123456789', '9876543210987654321'],
            'Datetime': ['2024-01-15T14:30:22', '2024-01-16T15:45:33'],
            'Type': ['Payment', 'Payment'],
            'Status': ['Complete', 'Complete'],
            'Note': ['Dinner payment', 'Rent split'],
            'From': ['Alex Johnson', 'Sarah Wilson'],  # Who sent the money
            'To': ['Emily Davis', 'Alex Johnson'],     # Who received the money
            'Amount (total)': ['- $75.00', '+ $200.00'],  # Negative = sent, Positive = received
            'Amount (tip)': ['', ''],
            'Amount (tax)': ['0', '0'],
            'Amount (fee)': ['0', '0'],
            'Tax Rate': ['0', '0'],
            'Tax Exempt': ['', ''],
            'Funding Source': ['Venmo balance', ''],
            'Destination': ['Venmo', 'Venmo balance'],
            'Beginning Balance': ['', ''],
            'Ending Balance': ['', ''],
            'Statement Period Venmo Fees': ['', ''],
            'Terminal Location': ['', ''],
            'Year to Date Venmo Fees': ['', ''],
            'Disclaimer': ['', '']
        }
        
        venmo_df = pd.DataFrame(venmo_data)
        
        # Define existing columns that should be in the Excel file
        existing_columns = [
            'Date', 'Description', 'Category', 'Amount', 'Account', 
            'Account #', 'Institution', 'Year', 'Month', 'Week', 
            'Check Number', 'Full Description', 'Date Added'
        ]
        
        # Transform the transactions
        transformed = importer._transform_transactions(venmo_df, existing_columns)
        
        # Should return a list with two transformed transactions
        assert len(transformed) == 2
        
        # Find the debit and credit transactions
        debit_transaction = next(t for t in transformed if t['Amount'] == -75.00)
        credit_transaction = next(t for t in transformed if t['Amount'] == 200.00)
        
        # For debit transactions (money sent), description should use 'To' field
        assert debit_transaction['Description'] == 'Emily Davis', f"Expected 'Emily Davis' for debit, got '{debit_transaction['Description']}'"
        
        # For credit transactions (money received), description should use 'From' field
        assert credit_transaction['Description'] == 'Sarah Wilson', f"Expected 'Sarah Wilson' for credit, got '{credit_transaction['Description']}'"

    def test_transform_transactions_special_characters(self):
        """Test UT020: Special characters - Emojis in notes should be handled correctly."""
        importer = VenmoImporter()
        
        # Create test data with various special characters and emojis
        import pandas as pd
        
        venmo_data = {
            'ID': ['1234567890123456789', '9876543210987654321', '5555555555555555555'],
            'Datetime': ['2024-01-15T14:30:22', '2024-01-16T15:45:33', '2024-01-17T16:00:00'],
            'Type': ['Payment', 'Payment', 'Payment'],
            'Status': ['Complete', 'Complete', 'Complete'],
            'Note': [
                'Dinner 🍕 🍷 with friends',  # Food emojis
                'Coffee ☕ and pastries 🥐',  # Drink and food emojis
                'Concert tickets 🎵 🎫 for tonight!'  # Music emojis with punctuation
            ],
            'From': ['Alex Johnson', 'Sarah Wilson', 'Mike Chen'],
            'To': ['Emily Davis', 'Alex Johnson', 'Alex Johnson'],
            'Amount (total)': ['- $45.50', '+ $12.75', '+ $120.00'],
            'Amount (tip)': ['', '', ''],
            'Amount (tax)': ['0', '0', '0'],
            'Amount (fee)': ['0', '0', '0'],
            'Tax Rate': ['0', '0', '0'],
            'Tax Exempt': ['', '', ''],
            'Funding Source': ['Venmo balance', '', ''],
            'Destination': ['Venmo', 'Venmo balance', 'Venmo balance'],
            'Beginning Balance': ['', '', ''],
            'Ending Balance': ['', '', ''],
            'Statement Period Venmo Fees': ['', '', ''],
            'Terminal Location': ['', '', ''],
            'Year to Date Venmo Fees': ['', '', ''],
            'Disclaimer': ['', '', '']
        }
        
        venmo_df = pd.DataFrame(venmo_data)
        
        # Define existing columns that should be in the Excel file
        existing_columns = [
            'Date', 'Description', 'Category', 'Amount', 'Account', 
            'Account #', 'Institution', 'Year', 'Month', 'Week', 
            'Check Number', 'Full Description', 'Date Added', 'Note'
        ]
        
        # Transform the transactions
        transformed = importer._transform_transactions(venmo_df, existing_columns)
        
        # Should return a list with three transformed transactions
        assert len(transformed) == 3
        
        # Find each transaction by amount and verify emojis are preserved
        dinner_transaction = next(t for t in transformed if t['Amount'] == -45.50)
        coffee_transaction = next(t for t in transformed if t['Amount'] == 12.75)
        concert_transaction = next(t for t in transformed if t['Amount'] == 120.00)
        
        # Check that Note field exists (according to spec: Note -> Note)
        assert 'Note' in dinner_transaction
        assert 'Note' in coffee_transaction  
        assert 'Note' in concert_transaction
        
        # Verify that emojis are preserved in the Note field (per specification)
        # According to venmo_importer.md: Note field maps to Note field
        assert '🍕' in dinner_transaction['Note'] and '🍷' in dinner_transaction['Note'], f"Expected emojis in dinner note: {dinner_transaction['Note']}"
        assert '☕' in coffee_transaction['Note'] and '🥐' in coffee_transaction['Note'], f"Expected emojis in coffee note: {coffee_transaction['Note']}"
        assert '🎵' in concert_transaction['Note'] and '🎫' in concert_transaction['Note'], f"Expected emojis in concert note: {concert_transaction['Note']}"

    def test_transform_transactions_empty_fields(self):
        """Test UT021: Empty fields - Missing From/To fields should be handled gracefully."""
        importer = VenmoImporter()
        
        # Create test data with empty/missing From and To fields
        import pandas as pd
        
        venmo_data = {
            'ID': ['1111111111111111111', '2222222222222222222', '3333333333333333333'],
            'Datetime': ['2024-01-15T14:30:22', '2024-01-16T15:45:33', '2024-01-17T16:00:00'],
            'Type': ['Payment', 'Payment', 'Payment'],
            'Status': ['Complete', 'Complete', 'Complete'],
            'Note': ['Empty from field', 'Empty to field', 'Both fields empty'],
            'From': ['', 'Alex Johnson', ''],  # First and third have empty From
            'To': ['Sarah Wilson', '', ''],    # Second and third have empty To
            'Amount (total)': ['- $25.00', '+ $50.00', '- $75.00'],
            'Amount (tip)': ['', '', ''],
            'Amount (tax)': ['0', '0', '0'],
            'Amount (fee)': ['0', '0', '0'],
            'Tax Rate': ['0', '0', '0'],
            'Tax Exempt': ['', '', ''],
            'Funding Source': ['Venmo balance', '', ''],
            'Destination': ['Venmo', 'Venmo balance', 'Venmo'],
            'Beginning Balance': ['', '', ''],
            'Ending Balance': ['', '', ''],
            'Statement Period Venmo Fees': ['', '', ''],
            'Terminal Location': ['', '', ''],
            'Year to Date Venmo Fees': ['', '', ''],
            'Disclaimer': ['', '', '']
        }
        
        venmo_df = pd.DataFrame(venmo_data)
        
        # Define existing columns that should be in the Excel file
        existing_columns = [
            'Date', 'Description', 'Category', 'Amount', 'Account', 
            'Account #', 'Institution', 'Year', 'Month', 'Week', 
            'Check Number', 'Full Description', 'Date Added'
        ]
        
        # Transform the transactions
        transformed = importer._transform_transactions(venmo_df, existing_columns)
        
        # Should return a list with three transformed transactions
        assert len(transformed) == 3
        
        # Find transactions by amount
        first_transaction = next(t for t in transformed if t['Amount'] == -25.00)  # Empty From, has To
        second_transaction = next(t for t in transformed if t['Amount'] == 50.00)  # Has From, empty To
        third_transaction = next(t for t in transformed if t['Amount'] == -75.00)  # Both empty
        
        # Test case 1: Empty From field, has To field, negative amount (should use To field)
        assert first_transaction['Description'] == 'Sarah Wilson', f"Expected 'Sarah Wilson' for first transaction, got '{first_transaction['Description']}'"
        
        # Test case 2: Has From field, empty To field, positive amount (should use From field)
        assert second_transaction['Description'] == 'Alex Johnson', f"Expected 'Alex Johnson' for second transaction, got '{second_transaction['Description']}'"
        
        # Test case 3: Both From and To fields empty (should use fallback description)
        # When both fields are empty, should use a default description like "Venmo Transaction" or "Unknown"
        expected_fallback = 'Venmo Transaction'  # Define expected fallback behavior
        assert third_transaction['Description'] == expected_fallback, f"Expected '{expected_fallback}' for third transaction, got '{third_transaction['Description']}'"

    def test_transform_transactions_multi_line_disclaimer(self):
        """Test UT022: Multi-line disclaimer - CSV with multi-line disclaimer in last row should be handled correctly."""
        importer = VenmoImporter()
        
        # Create a temporary CSV file with multi-line disclaimer at the end
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("Account Statement - (@testuser) ,,,,,,,,,,,,,,,,,,,,,\n")
            f.write("Account Activity,,,,,,,,,,,,,,,,,,,,,\n")
            f.write(",ID,Datetime,Type,Status,Note,From,To,Amount (total),Amount (tip),Amount (tax),Amount (fee),Tax Rate,Tax Exempt,Funding Source,Destination,Beginning Balance,Ending Balance,Statement Period Venmo Fees,Terminal Location,Year to Date Venmo Fees,Disclaimer\n")
            f.write(",,,,,,,,,,,,,,,,,,,,\"$1,250.00\",,,,,\n")
            # Add some valid transaction data
            f.write(",1234567890123456789,2024-01-15T14:30:22,Payment,Complete,Dinner payment,Alex Johnson,Sarah Wilson,- $75.00,,0,,0,,Venmo balance,,,,,Venmo,,,\n")
            f.write(",9876543210987654321,2024-01-16T15:45:33,Payment,Complete,Coffee money,Mike Chen,Alex Johnson,+ $12.50,,0,,0,,Venmo balance,,,,,Venmo,,,\n")
            # Add multi-line disclaimer at the end (this should be filtered out)
            f.write(",,,,,,,,,,,,,,,,,,,,,,\"This is a multi-line disclaimer\n")
            f.write("that spans multiple lines and contains\n")
            f.write("important legal information about\n")
            f.write("your Venmo account and transactions.\"\n")
            temp_csv_file = f.name
        
        try:
            # Read the CSV data which should handle multi-line disclaimer correctly
            df = importer._read_csv_data(temp_csv_file)
            
            # Should have processed only the valid transaction data, filtering out disclaimer
            assert len(df) == 2, f"Expected 2 transactions, but got {len(df)}"
            
            # Check that we have the expected transaction data
            assert 'Datetime' in df.columns
            assert 'From' in df.columns
            assert 'To' in df.columns
            assert 'Amount (total)' in df.columns
            
            # Verify the transaction data is correct (not corrupted by disclaimer)
            first_row = df.iloc[0]
            second_row = df.iloc[1]
            
            assert first_row['Datetime'] == '2024-01-15T14:30:22'
            assert first_row['From'] == 'Alex Johnson'
            assert first_row['To'] == 'Sarah Wilson'
            assert first_row['Amount (total)'] == '- $75.00'
            
            assert second_row['Datetime'] == '2024-01-16T15:45:33'
            assert second_row['From'] == 'Mike Chen'
            assert second_row['To'] == 'Alex Johnson'
            assert second_row['Amount (total)'] == '+ $12.50'
            
            # Transform the transactions to ensure they process correctly
            existing_columns = [
                'Date', 'Description', 'Category', 'Amount', 'Account', 
                'Account #', 'Institution', 'Year', 'Month', 'Week', 
                'Check Number', 'Full Description', 'Date Added'
            ]
            
            transformed = importer._transform_transactions(df, existing_columns)
            
            # Should successfully transform both transactions
            assert len(transformed) == 2
            
            # Verify transformed data is correct
            first_transaction = next(t for t in transformed if t['Amount'] == -75.00)
            second_transaction = next(t for t in transformed if t['Amount'] == 12.50)
            
            assert first_transaction['Description'] == 'Sarah Wilson'  # Debit: use To field
            assert second_transaction['Description'] == 'Mike Chen'    # Credit: use From field
            
        finally:
            # Clean up temporary file
            os.unlink(temp_csv_file)

    def test_read_csv_data_balance_row_filtering(self):
        """Test UT023: Balance row filtering - CSV with beginning/ending balance rows should be filtered out correctly."""
        importer = VenmoImporter()
        
        # Create a temporary CSV file with balance rows that should be filtered out
        # Use a simple format that matches existing working tests
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("Account Statement - (@testuser) ,,,,,,,,,,,,,,,,,,,,,\n")
            f.write("Account Activity,,,,,,,,,,,,,,,,,,,,,\n")
            f.write(",ID,Datetime,Type,Status,Note,From,To,Amount (total),Amount (tip),Amount (tax),Amount (fee),Tax Rate,Tax Exempt,Funding Source,Destination,Beginning Balance,Ending Balance,Statement Period Venmo Fees,Terminal Location,Year to Date Venmo Fees,Disclaimer\n")
            
            # Beginning balance row (should be filtered out - no transaction ID) - match working test format
            f.write(",,,,,,,,,,,,,,,,,,,,\"$1,250.00\",,,,,\n")
            
            # Valid transaction (should be kept) - exact same format as working test
            f.write(",1234567890123456789,2024-01-15T14:30:22,Payment,Complete,Dinner payment,Alex Johnson,Sarah Wilson,- $75.00,,0,,0,,Venmo balance,,,,,Venmo,,,\n")
            
            # Ending balance row (should be filtered out - no transaction ID) - match working test format
            f.write(",,,,,,,,,,,,,,,,,,,,\"$1,175.00\",,,,,\n")
            
            temp_csv_file = f.name
        
        try:
            # Call the actual _read_csv_data method to test the real functionality
            df = importer._read_csv_data(temp_csv_file)
            
            # The method should filter out balance rows and keep only valid transactions
            # We expect 1 transaction (the valid one with ID), balance rows should be filtered out
            assert len(df) == 1, f"Expected 1 transaction after filtering, but got {len(df)}. DataFrame:\n{df}"
            
            # Verify we have the expected columns
            assert 'ID' in df.columns
            assert 'Datetime' in df.columns
            assert 'From' in df.columns
            assert 'To' in df.columns
            assert 'Amount (total)' in df.columns
            
            # Verify the remaining transaction has a valid ID
            transaction_row = df.iloc[0]
            # ID might be parsed as float, so convert to string for comparison
            assert transaction_row['ID'] == '1234567890123456789'
            assert transaction_row['Datetime'] == '2024-01-15T14:30:22'
            assert transaction_row['From'] == 'Alex Johnson'
            assert transaction_row['To'] == 'Sarah Wilson'
            assert transaction_row['Amount (total)'] == '- $75.00'
            
            # Verify all rows have valid transaction IDs (no empty or NaN IDs)
            for idx, row in df.iterrows():
                transaction_id = row['ID'].strip()
                assert transaction_id != '', f"Row {idx} should have been filtered out due to empty transaction ID"
                assert transaction_id != 'nan', f"Row {idx} should have been filtered out due to NaN transaction ID"
                assert len(transaction_id) > 0, f"Row {idx} has zero-length transaction ID"
                
        finally:
            # Clean up temporary file
            os.unlink(temp_csv_file)