"""
Test module for VenmoImporter class.

This module contains comprehensive tests for the VenmoImporter class,
covering all public methods, error conditions, and edge cases specific to
Venmo's unique CSV format with multi-line headers and ISO datetime formats.
"""

import pytest
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
