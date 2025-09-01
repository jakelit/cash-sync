"""
Defines the VenmoImporter class for processing Venmo transaction data.

This module provides the implementation of the VenmoImporter, which is a subclass
of BaseImporter. It is specifically designed to handle Venmo's unique CSV format
with multi-line headers, ISO datetime formats, and signed currency amounts.
"""

import re

import pandas as pd

from .base_importer import BaseImporter


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
        self._set_column_mapping('Datetime', 'Date')
        self._set_column_mapping('Amount (total)', 'Amount')
        self._set_column_mapping('Type', 'Transaction Type')
        # Store extracted username from CSV header
        self.extracted_username = None
        # Minimal implementation to make first test pass

    def _read_csv_data(self, csv_file: str) -> pd.DataFrame:
        """
        Read and parse Venmo CSV file with multi-line header structure.
        
        Overrides the base method to handle Venmo's unique CSV format:
        - Line 1: "Account Statement - (@username)" - extract username
        - Line 2: "Account Activity" - skip
        - Line 3: Column headers (actual transaction data starts from line 4)
        - Skip footer disclaimer text
        - Handle blank first column and filter out balance rows
        
        Args:
            csv_file (str): Path to the CSV file to read
            
        Returns:
            pd.DataFrame: The parsed CSV data as a pandas DataFrame
        """
        
        # Read the first line to extract username
        with open(csv_file, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            # Extract username from "Account Statement - (@username)" format
            self._extract_username_from_header(first_line)
        
        # Read CSV starting from line 4 (data rows), no header
        df = pd.read_csv(csv_file, skiprows=3, header=None, encoding='utf-8')
        
        # Get column headers from line 3 and clean them
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            headers = lines[2].strip().split(',')[1:]  # Skip blank first column
        
        # Remove first column from data and set headers
        df = df.iloc[:, 1:]
        
        # Ensure DataFrame has the same number of columns as headers
        if len(df.columns) > len(headers):
            df = df.iloc[:, :len(headers)]
        
        df.columns = headers
        
        # Remove any completely empty rows
        df = df.dropna(how='all')
        
        # Filter out balance rows - keep only rows with valid transaction IDs
        df = df[df['ID'].notna() & (df['ID'] != '')]
        
        return df
    
    def _get_expected_columns(self):
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
    
    def _get_institution_name(self):
        """Return the human-readable name of the financial institution."""
        # Minimal implementation - will be properly implemented later
        return "Venmo"
    
    def _get_account_name(self):
        """Return the account name or identifier for this specific account."""
        # Return extracted username if available, otherwise default to "Venmo"
        if self.extracted_username:
            return self.extracted_username
        return "Venmo"

    def _extract_username_from_header(self, header_line):
        """Extract username from Venmo CSV header line."""
        # Extract username from "Account Statement - (@username)" format
        match = re.search(r'@\w+', header_line)
        if match:
            self.extracted_username = match.group(0)
        else:
            self.extracted_username = "Venmo"

    def _get_description(self, row: dict) -> str:
        """
        Return the description for a Venmo transaction based on From/To fields.
        
        For Venmo transactions:
        - Negative amount = money sent (use 'To' field)
        - Positive amount = money received (use 'From' field)
        
        Args:
            row (dict): A dictionary representing a single row from the CSV file
            
        Returns:
            str: The description for this transaction
        """
        from_field = str(row.get('From', '')).strip()
        to_field = str(row.get('To', '')).strip()
        amount_str = str(row.get('Amount (total)', '')).strip()
        
        # Parse amount to determine transaction direction
        amount = self._parse_transaction_amount(amount_str)
        
        # For Venmo: negative amount = money sent (use 'To' field), positive = money received (use 'From' field)
        if amount < 0:
            return to_field  # Money sent to someone
        else:
            return from_field  # Money received from someone
