"""
Defines the AllyImporter class for processing Ally Bank transaction data.

This module provides the implementation of the AllyImporter, which is a subclass
of BaseImporter. It is specifically designed to handle the unique CSV format
exported from Ally Bank's online portal. This includes mapping Ally-specific
column names (e.g., 'Transaction Type') to the standardized transaction
format and correctly interpreting transaction amounts.
"""
from .base_importer import BaseImporter
from .logger import logger

class AllyImporter(BaseImporter):
    """
    Handles the import of transaction data from Ally Bank CSV files.

    This class sets up the specific column mappings and default values
    required to correctly parse and import transaction files from Ally Bank.
    """
    def __init__(self):
        super().__init__()
        
        # Set column mappings for Ally's CSV format
        self.set_column_mapping('Date', 'Date')
        self.set_column_mapping('Amount', 'Amount')
        self.set_column_mapping('Type', 'Transaction Type')
        self.set_column_mapping('Description', 'Description')
        
        # Set default values for required fields
        self.set_default_value('Account Number', 'Ally Bank')
        self.set_default_value('Balance', 0.0)
    
    def get_expected_columns(self):
        """Return the expected columns for Ally CSV file."""
        return [
            'Date', 'Time', 'Amount', 'Type', 'Description'
        ]
    
    def get_institution_name(self):
        """Return the institution name for Ally."""
        return 'Ally Bank'
    
    def get_account_name(self):
        """Return the default account name for Ally."""
        return 'Ally'
    
    def parse_transaction_amount(self, amount_str, transaction_type=None):
        """Parse transaction amount and determine if it's a debit or credit."""
        try:
            # Remove any currency symbols and whitespace
            amount_str = amount_str.replace('$', '').strip()
            
            # Convert to float
            amount = float(amount_str)
            
            # For Ally, negative amounts are debits, positive are credits
            return amount
            
        except (ValueError, TypeError) as e:
            logger.error("Error parsing amount '%s': %s", amount_str, e)
            return 0.0
