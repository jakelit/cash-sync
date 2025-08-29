"""
This module defines the abstract interface for transaction importers.
"""
from abc import ABC, abstractmethod
from typing import List

class TransactionImporter(ABC):
    """
    An abstract base class that defines the interface for all bank-specific
    transaction importers. It ensures that all importers implement a consistent
    method for importing transactions.
    """
    
    @abstractmethod
    def get_expected_columns(self) -> List[str]:
        """Return the expected columns for this bank's CSV file."""
        raise NotImplementedError  # pragma: no cover
    
    @abstractmethod
    def get_institution_name(self) -> str:
        """Return the institution name for this bank."""
        raise NotImplementedError  # pragma: no cover
    
    @abstractmethod
    def get_account_name(self) -> str:
        """Return the default account name for this bank."""
        raise NotImplementedError  # pragma: no cover
    
    @abstractmethod
    def parse_transaction_amount(self, amount_str: str, transaction_type: str = None) -> float:
        """Parse transaction amount and determine if it's a debit or credit."""
        raise NotImplementedError  # pragma: no cover
    
    @abstractmethod
    def parse_transaction_date(self, date_str: str) -> str:
        """Parse transaction date from string."""
        raise NotImplementedError  # pragma: no cover
    
    @abstractmethod
    def clean_description(self, description: str) -> str:
        """Clean and format transaction description to be more human readable."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def import_transactions(self, csv_file: str, excel_file: str):
        """
        Import transactions from a CSV file and save them to an Excel file.

        Args:
            csv_file (str): The path to the CSV file containing transaction data.
            excel_file (str): The path to the Excel file where transactions will be saved.
        """
        raise NotImplementedError  # pragma: no cover