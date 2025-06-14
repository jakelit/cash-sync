from abc import ABC, abstractmethod
from typing import List

class TransactionImporter(ABC):
    """Core interface for importing transactions from a bank's CSV file."""
    
    @abstractmethod
    def get_expected_columns(self) -> List[str]:
        """Return the expected columns for this bank's CSV file."""
        pass
    
    @abstractmethod
    def get_institution_name(self) -> str:
        """Return the institution name for this bank."""
        pass
    
    @abstractmethod
    def get_account_name(self) -> str:
        """Return the default account name for this bank."""
        pass
    
    @abstractmethod
    def parse_transaction_amount(self, amount_str: str, transaction_type: str = None) -> float:
        """Parse transaction amount and determine if it's a debit or credit."""
        pass
    
    @abstractmethod
    def parse_transaction_date(self, date_str: str) -> str:
        """Parse transaction date from string."""
        pass
    
    @abstractmethod
    def clean_description(self, description: str) -> str:
        """Clean and format transaction description to be more human readable."""
        pass 