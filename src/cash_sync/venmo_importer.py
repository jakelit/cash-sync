"""
Defines the VenmoImporter class for processing Venmo transaction data.

This module provides the implementation of the VenmoImporter, which is a subclass
of BaseImporter. It is specifically designed to handle Venmo's unique CSV format
with multi-line headers, ISO datetime formats, and signed currency amounts.
"""

from .base_importer import BaseImporter
import re
import pandas as pd


class VenmoImporter(BaseImporter):
    """
    Handles the import of transaction data from Venmo CSV files.

    This class sets up the specific column mappings and default values
    required to correctly parse and import transaction files from Venmo.
    """
    
    def __init__(self):
        """Initialize VenmoImporter instance."""
        super().__init__()
        # Set Venmo-specific column mappings
        self.set_column_mapping('Datetime', 'Date')
        self.set_column_mapping('Amount (total)', 'Amount')
        self.set_column_mapping('Type', 'Transaction Type')
        # Store extracted username from CSV header
        self.extracted_username = None
        # Minimal implementation to make first test pass

    def read_csv_data(self, csv_file: str) -> pd.DataFrame:
        """
        Read and parse Venmo CSV file with multi-line header structure.
        
        Overrides the base method to handle Venmo's unique CSV format:
        - Line 1: "Account Statement - (@username)" - extract username
        - Line 2: "Account Activity" - skip
        - Line 3: Column headers (actual transaction data starts from line 4)
        - Skip footer disclaimer text
        
        Args:
            csv_file (str): Path to the CSV file to read
            
        Returns:
            pd.DataFrame: The parsed CSV data as a pandas DataFrame
        """
        
        # Read the first line to extract username
        with open(csv_file, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            # Extract username from "Account Statement - (@username)" format
            self.extract_username_from_header(first_line)
        
        # Read CSV starting from line 3 (skip lines 1-2)
        df = pd.read_csv(csv_file, skiprows=2, encoding='utf-8')
        
        # Remove any completely empty rows
        df = df.dropna(how='all')
        
        return df
    
    def get_expected_columns(self):
        """Return the list of required column names for Venmo CSV files."""
        # Return the 6 required Venmo columns as specified in venmo_importer.md
        return [
            'Datetime',
            'Type', 
            'Note',
            'From',
            'To',
            'Amount (total)'
        ]
    
    def get_institution_name(self):
        """Return the human-readable name of the financial institution."""
        # Minimal implementation - will be properly implemented later
        return "Venmo"
    
    def get_account_name(self):
        """Return the account name or identifier for this specific account."""
        # Return extracted username if available, otherwise default to "Venmo"
        if self.extracted_username:
            return self.extracted_username
        return "Venmo"

    def extract_username_from_header(self, header_line):
        """Extract username from Venmo CSV header line."""
        # Extract username from "Account Statement - (@username)" format
        match = re.search(r'@\w+', header_line)
        if match:
            self.extracted_username = match.group(0)
        else:
            self.extracted_username = "Venmo"
    
    def parse_transaction_amount(self, amount_str, transaction_type=None):
        """Parse a transaction amount string and determine if it's a debit or credit."""
        # Minimal implementation - will be properly implemented later
        return 0.0
