"""
Defines the CapitalOneImporter class for processing Capital One transaction data.

This module provides the implementation of the CapitalOneImporter, which is
specifically designed to handle the CSV format exported from Capital One's
online portal.
"""
from .base_importer import BaseImporter
from .logger import logger

class CapitalOneImporter(BaseImporter):
    """
    Handles the import of transaction data from Capital One CSV files.

    This class sets up the specific column mappings and default values
    required to correctly parse and import transaction files from Capital One,
    and it implements the logic for parsing transaction amounts, where debits
    are positive and credits are negative.
    """
    def __init__(self):
        super().__init__()
        
        # Set column mappings for CapitalOne's CSV format
        self.set_column_mapping('Transaction Date', 'Date')
        self.set_column_mapping('Transaction Description', 'Description')
        self.set_column_mapping('Transaction Amount', 'Amount')
        self.set_column_mapping('Balance', 'Balance')
        self.set_column_mapping('Account Number', 'Account Number')
        self.set_column_mapping('Transaction Type', 'Transaction Type')
        
    def get_expected_columns(self):
        """Return the expected columns for Capital One's CSV file."""
        return [
            'Account Number',
            'Transaction Description',
            'Transaction Date',
            'Transaction Type',
            'Transaction Amount',
            'Balance'
        ]
    
    def get_institution_name(self):
        """Return the institution name for Capital  One."""
        return 'Capital One'
    
    def get_account_name(self):
        """Return the default account name for Capital One."""
        return 'Capital One'
    
    def parse_transaction_amount(self, amount_str, transaction_type=None):
        """Parse transaction amount and determine if it's a debit or credit."""
        try:
            # Remove any currency symbols and whitespace
            amount_str = amount_str.replace('$', '').strip()
            
            # Convert to float
            amount = float(amount_str)
            
            # For CapitalOne, we need to check the transaction type
            if transaction_type:
                transaction_type = transaction_type.lower()
                if 'debit' in transaction_type:
                    amount = -abs(amount)  # Ensure negative for debits
                elif 'credit' in transaction_type:
                    amount = abs(amount)   # Ensure positive for credits
            
            return amount
            
        except (ValueError, TypeError) as e:
            logger.error("Error parsing amount '%s': %s", amount_str, e)
            return 0.0 
    