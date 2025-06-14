from .base_importer import BaseImporter

class CapitalOneImporter(BaseImporter):
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
        """Return the expected columns for CapitalOne's CSV file."""
        return [
            'Account Number',
            'Transaction Description',
            'Transaction Date',
            'Transaction Type',
            'Transaction Amount',
            'Balance'
        ]
    
    def get_institution_name(self):
        """Return the institution name for CapitalOne."""
        return 'Capital One'
    
    def get_account_name(self):
        """Return the default account name for CapitalOne."""
        return 'CapitalOne'
    
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
            
        except Exception as e:
            print(f"Error parsing amount '{amount_str}': {e}")
            return 0.0 
    