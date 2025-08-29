"""
Defines the base class and interface for all transaction importers.

This module provides the `BaseImporter` class, an abstract base class that
establishes a common interface for all bank-specific importers. It handles
the shared logic for reading CSVs, finding and validating columns, checking
for duplicates, and writing new transactions to Excel.
"""
import os
import re
import traceback
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import pandas as pd
from .csv_handler import CSVHandler
from .excel_handler import ExcelHandler
from .logger import logger


class BaseImporter(ABC):
    """
    Abstract base class for all bank-specific transaction importers.

    This class provides the core framework for importing transactions, including
    CSV reading, duplicate checking, and writing to an Excel file. Subclasses

    must implement the abstract methods to handle institution-specific details
    like column mappings and transaction parsing logic.
    """
    
    def __init__(self):
        """Initializes the BaseImporter."""
        self.csv_file = None
        self.excel_file = None
        
        # Default column mappings for common fields
        self.column_mappings = {
            'Date': 'Date',
            'Description': 'Description',
            'Amount': 'Amount',
            'Balance': 'Balance',
            'Account Number': 'Account Number',
            'Transaction Type': 'Transaction Type'
        }
        
        # Default values for required fields
        self.default_values = {
            'Account Number': '',
            'Transaction Type': '',
            'Balance': 0.0
        }
    
    @abstractmethod
    def get_expected_columns(self):
        """
        Return the list of required column names that must be present in the CSV file.
        
        This method is used for CSV validation before processing begins. If any of these
        columns are missing from the CSV file, the import will fail with a clear error
        message showing which columns are missing.
        
        Returns:
            List[str]: A list of column names that must be present in the CSV file.
                       These should match the exact column headers in the CSV.
        
        Example:
            >>> return ['Date', 'Description', 'Amount', 'Account Number']
        """
        raise NotImplementedError  # pragma: no cover
    
    @abstractmethod
    def get_institution_name(self):
        """
        Return the human-readable name of the financial institution.

        The value returned by this method will be used to populate the "Institution"
        column in the transaction table (Excel output), clearly identifying the source of each transaction.
        It should be the official name of the bank or financial service
        (e.g., "Capital One", "Ally Bank", "Venmo").

        Returns:
            str: The institution name that will appear in the "Institution" column
                 of the Excel file.

        Example:
            >>> return "Capital One"
        """
        raise NotImplementedError  # pragma: no cover
    
    @abstractmethod
    def get_account_name(self):
        """
        Return the account name or identifier for this specific account.

        The value returned by this method will be used to populate the "Account" column
        in the transaction table (Excel output), clearly indicating which account each
        transaction belongs to.

        This should be a unique identifier for the account being imported. It could be:
        - A default account name (e.g., "Capital One", "Ally")
        - An account number or identifier
        - A username extracted from the CSV (e.g., "@username" for Venmo)
        - Any other identifier that distinguishes this account from others

        Returns:
            str: The account name or identifier for this account, to be shown in the "Account" column.

        Example:
            >>> return "Capital One"  # Default account name
            >>> return "@sophib"      # Username extracted from CSV
            >>> return "1234567890"   # Account number
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def parse_transaction_amount(self, amount_str, transaction_type=None):
        """
        Parse a transaction amount string and determine if it's a debit or credit.
        
        This method handles the bank-specific logic for interpreting transaction amounts.
        Different banks may represent debits and credits differently:
        - Some use positive/negative signs
        - Some use separate debit/credit columns
        - Some rely on transaction type to determine direction
        
        Args:
            amount_str (str): The raw amount string from the CSV (e.g., "$50.00", "-$25.00")
            transaction_type (str, optional): The transaction type from the CSV, which may
                                            be needed to determine if the amount is a debit
                                            or credit. Defaults to None.
        
        Returns:
            float: The parsed amount as a float where:
                  - Negative values = Money leaving the account (debit)
                  - Positive values = Money entering the account (credit)
        
        Example:
            >>> parse_transaction_amount("$50.00")  # Returns 50.0 (credit)
            >>> parse_transaction_amount("-$25.00") # Returns -25.0 (debit)
            >>> parse_transaction_amount("100.00", "debit")  # Returns -100.0
        """
        raise NotImplementedError  # pragma: no cover

    def set_column_mapping(self, source_column: str, target_column: str):
        """
        Set a custom column mapping for this bank's CSV format.
        
        This method maps a bank-specific column name to the standardized column name
        used internally by the importer. For example, if a bank uses "Transaction Date"
        but the importer expects "Date", you would map "Transaction Date" to "Date".
        
        Args:
            source_column (str): The column name as it appears in the bank's CSV file
            target_column (str): The standardized column name used internally by the importer
        
        Example:
            >>> set_column_mapping("Transaction Date", "Date")
            >>> set_column_mapping("Transaction Description", "Description")
        """
        self.column_mappings[target_column] = source_column
    
    def set_default_value(self, column: str, value: Any):
        """
        Set a default value for a column if it's missing in the CSV file.
        
        This method provides fallback values for columns that might not be present
        in the CSV file. The default value will be used when get_column_value() cannot
        find the column in the CSV data.
        
        Precedence Order (in get_column_value):
        1. First, check if there's a column mapping for the requested column
        2. If mapped column exists in the CSV row, return its value
        3. If no mapping or column doesn't exist, check for a default value (set by this method)
        4. If no default value, return an empty string
        
        Note: Some default values are already set in __init__() for common fields:
        - 'Account Number': ''
        - 'Transaction Type': ''
        - 'Balance': 0.0
        
        Args:
            column (str): The standardized column name (e.g., "Account Number", "Transaction Type")
            value (Any): The default value to use if the column is missing from the CSV
        
        Example:
            >>> set_default_value("Account Number", "1234567890")
            >>> set_default_value("Transaction Type", "Transfer")
            >>> set_default_value("Category", "Uncategorized")
        """
        self.default_values[column] = value
    
    def get_column_value(self, row: Dict[str, Any], column_name: str) -> str:
        """
        Get a column value from a CSV row, using mapping and default values if needed.
        
        This method retrieves a value from a CSV row using the following logic:
        1. First, check if there's a column mapping for the requested column
        2. If mapped column exists in the row, return its value
        3. If no mapping or column doesn't exist, check for a default value
        4. If no default value, return an empty string
        
        Args:
            row (Dict[str, Any]): A dictionary representing a single row from the CSV file,
                                where keys are column names and values are cell contents
            column_name (str): The standardized column name to retrieve (e.g., "Date", "Amount")
        
        Returns:
            str: The value from the CSV row, or the default value, or an empty string
                 if neither exists
        
        Example:
            >>> row = {"Transaction Date": "2023-01-15", "Amount": "$50.00"}
            >>> get_column_value(row, "Date")  # Returns "2023-01-15" (using mapping)
            >>> get_column_value(row, "Account Number")  # Returns default value or ""
        """
        # Get the mapped column name
        mapped_column = self.column_mappings.get(column_name)
        
        # If we have a mapping and the column exists in the row, use it
        if mapped_column and mapped_column in row:
            return row[mapped_column]
        
        # If we have a default value, use it
        if column_name in self.default_values:
            return self.default_values[column_name]
        
        # If no mapping or default, return empty string
        return ''
    
    def parse_transaction_date(self, date_str):
        """
        Parse a transaction date string into a datetime.date object.
        
        This method attempts to parse date strings in multiple common formats.
        If parsing fails, it logs a warning and returns None, allowing the
        transaction to be processed with an empty date field for manual correction.
        
        Args:
            date_str (str): The date string to parse (e.g., "01/15/2023", "2023-01-15")
        
        Returns:
            datetime.date or None: The parsed date object, or None if parsing fails.
                                  Returns None for invalid or unparseable date strings.
        
        Supported Formats:
            - MM/DD/YYYY (e.g., "01/15/2023")
            - YYYY-MM-DD (e.g., "2023-01-15")
            - MM-DD-YYYY (e.g., "01-15-2023")
            - DD/MM/YYYY (e.g., "15/01/2023")
        
        Example:
            >>> parse_transaction_date("01/15/2023")  # Returns datetime.date(2023, 1, 15)
            >>> parse_transaction_date("invalid")     # Returns None, logs warning
        """
        try:
            # Try multiple date formats
            date_formats = ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d/%m/%Y']
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            # Last resort - try pandas
            date = pd.to_datetime(date_str, errors='coerce').date()
            if pd.isna(date):
                logger.warning("Could not parse date: '%s'. Date field will be left empty for manual correction.", date_str)
                return None
            return date
                
        except (ValueError, TypeError, OSError) as date_error:
            logger.warning("Date parsing error for '%s': %s. Date field will be left empty for manual correction.", date_str, date_error)
            return None

    def validate_files(self, csv_file, excel_file):
        """
        Validate that input files exist and are accessible.
        
        This method performs basic file validation before attempting to process
        the CSV and Excel files. It checks file existence and validates file extensions.
        
        Args:
            csv_file (str): Path to the CSV file to be imported
            excel_file (str): Path to the Excel file where transactions will be added
        
        Raises:
            FileNotFoundError: If either the CSV or Excel file does not exist
            ValueError: If the CSV file does not have a .csv extension
            ValueError: If the Excel file does not have a .xlsx or .xls extension
        
        Example:
            >>> validate_files("transactions.csv", "budget.xlsx")  # Valid
            >>> validate_files("transactions.txt", "budget.xlsx")  # Raises ValueError
            >>> validate_files("nonexistent.csv", "budget.xlsx")  # Raises FileNotFoundError
        """
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file not found: {csv_file}")
        
        if not os.path.exists(excel_file):
            raise FileNotFoundError(f"Excel file not found: {excel_file}")
        
        if not csv_file.lower().endswith('.csv'):
            raise ValueError("First file must be a CSV file")
        
        if not excel_file.lower().endswith(('.xlsx', '.xls')):
            raise ValueError("Second file must be an Excel file")
    
    def get_week_start(self, date):
        """
        Get the first day of the week (Sunday) for a given date.
        
        This method calculates the Sunday that starts the week containing the given date.
        It's used to populate the "Week" column in the Excel output for weekly grouping.
        
        Args:
            date (datetime.date): The date for which to find the week start
        
        Returns:
            datetime.date: The Sunday that starts the week containing the input date
        
        Example:
            >>> get_week_start(datetime.date(2023, 1, 15))  # Returns datetime.date(2023, 1, 15) (Sunday)
            >>> get_week_start(datetime.date(2023, 1, 18))  # Returns datetime.date(2023, 1, 15) (Sunday)
            >>> get_week_start(datetime.date(2023, 1, 20))  # Returns datetime.date(2023, 1, 15) (Sunday)
        """
        # Get the weekday (0=Monday, 6=Sunday in Python)
        days_since_sunday = (date.weekday() + 1) % 7
        week_start = date - timedelta(days=days_since_sunday)
        return week_start
    
    def format_date_mdy(self, date_obj):
        """
        Format a date object as M/D/YYYY string (without leading zeros).
        
        This method formats dates in a cross-platform compatible way without using
        strftime, which can have platform-specific issues. It's used to format dates
        for the Excel output in a consistent format.
        
        Args:
            date_obj (datetime.date or str or None): The date to format. Can be a date object,
                                                    a string (returned as-is), or None (returns empty string)
        
        Returns:
            str: The formatted date string in M/D/YYYY format, or the original string if input is a string,
                 or an empty string if input is None
        
        Example:
            >>> format_date_mdy(datetime.date(2023, 1, 5))  # Returns "1/5/2023"
            >>> format_date_mdy(datetime.date(2023, 12, 25))  # Returns "12/25/2023"
            >>> format_date_mdy("2023-01-05")  # Returns "2023-01-05" (string passed through)
            >>> format_date_mdy(None)  # Returns ""
        """
        if date_obj is None:
            return ''
        
        if isinstance(date_obj, str):
            return date_obj
        
        # Use manual formatting to avoid platform-specific strftime issues
        month = date_obj.month
        day = date_obj.day
        year = date_obj.year
        return f"{month}/{day}/{year}"
    
    def clean_description(self, description):
        """
        Clean and format transaction description to be more human readable.
        
        This method applies various cleaning operations to transaction descriptions:
        - Removes common bank prefixes (e.g., "Digital Card Purchase - ")
        - Removes payment processor prefixes (e.g., "TST* ", "SQ* ", "PP* ")
        - Removes store numbers and ID patterns
        - Normalizes spacing and formatting
        - Converts to title case
        
        Args:
            description (str or pandas.NA): The raw transaction description from the CSV
        
        Returns:
            str: The cleaned and formatted description, or an empty string if input is empty/None
        
        Example:
            >>> clean_description("Digital Card Purchase - TST* COFFEE SHOP #123")
            # Returns "Coffee Shop"
            >>> clean_description("SQ* BURGER JOINT")
            # Returns "Burger Joint"
            >>> clean_description("")  # Returns ""
        """
        if not description or pd.isna(description):
            return ''
        
        description = str(description).strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "Digital Card Purchase - ",
            "Debit Card Purchase - ",
            "Credit Card Purchase - ",
            "Card Purchase - ",
            "Purchase - "
        ]
        
        cleaned = description
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
                break
        
        # Remove common payment processor prefixes (more comprehensive)
        processor_prefixes = [
            "TST* ",    # Toast (with asterisk)
            "TST ",     # Toast (without asterisk)
            "SQ* ",     # Square (with asterisk)
            "SQ ",      # Square (without asterisk)
            "SP* ",     # Stripe (with asterisk)
            "SP ",      # Stripe (without asterisk)
            "PP* ",     # PayPal (with asterisk)
            "PP ",      # PayPal (without asterisk)
            "PAYPAL* ", # PayPal variant (with asterisk)
            "PAYPAL ",  # PayPal variant (without asterisk)
            "AMZN* ",   # Amazon (with asterisk)
            "AMZN ",    # Amazon (without asterisk)
            "UBER* ",   # Uber (with asterisk)
            "UBER ",    # Uber (without asterisk)
            "LYFT* ",   # Lyft (with asterisk)
            "LYFT ",    # Lyft (without asterisk)
        ]
        
        for prefix in processor_prefixes:
            if cleaned.upper().startswith(prefix.upper()):
                cleaned = cleaned[len(prefix):]
                break
        
        # Remove store numbers and common patterns
        # Remove patterns like #243, #1760, etc. (store numbers with #)
        cleaned = re.sub(r'\s*#\d+\s*', ' ', cleaned)
        # Remove standalone numbers that look like store IDs (4-6 digits)
        cleaned = re.sub(r'\s+\d{4,6}\s+', ' ', cleaned)
        
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Handle some final cleanup
        cleaned = cleaned.replace(',  ', ', ')  # Fix spacing after commas
        
        # Convert to title case (first letter of each word capitalized, rest lowercase)
        cleaned = ' '.join(word.capitalize() for word in cleaned.split())
        
        return cleaned

    def transform_transactions(self, df: pd.DataFrame, existing_columns: List[str]) -> List[Dict[str, Any]]:
        """
        Transform bank transactions from CSV format to standardized Excel format.
        
        This method processes each row in the CSV DataFrame and converts it to a
        standardized transaction format that matches the Excel file's column structure.
        It handles date parsing, amount parsing, description cleaning, and applies
        bank-specific logic through the abstract methods.
        
        Args:
            df (pd.DataFrame): The CSV data as a pandas DataFrame, where each row
                             represents a transaction and columns are CSV headers
            existing_columns (List[str]): List of column names that exist in the target Excel file.
                                        Only these columns will be included in the output.
        
        Returns:
            List[Dict[str, Any]]: A list of transaction dictionaries, where each dictionary
                                 represents one transaction with keys matching the Excel column names.
                                 Only includes columns that exist in the target Excel file.
        
        Note:
            - Rows with parsing errors are logged and skipped, allowing the import to continue
            - The method uses bank-specific logic from abstract methods (get_account_name, etc.)
            - Date fields (Year, Month, Week) are calculated from the transaction date
            - Empty or invalid dates result in empty string values for date-related fields
        """
        transformed_transactions = []
        
        for index, row in df.iterrows():
            try:
                # Parse transaction date
                trans_date = self.parse_transaction_date(str(self.get_column_value(row, 'Date')).strip())
                
                # Parse transaction amount
                amount = self.parse_transaction_amount(
                    str(self.get_column_value(row, 'Amount')),
                    str(self.get_column_value(row, 'Transaction Type')).lower().strip()
                )
                
                if trans_date is None:
                    year_start = ''
                    month_start = ''
                    week_start = ''
                else:
                    # Calculate date-related fields
                    year_start = datetime(trans_date.year, 1, 1)
                    month_start = datetime(trans_date.year, trans_date.month, 1)
                    week_start = self.get_week_start(trans_date)
                
                # Create transaction mapping
                transaction = {
                    'Date': self.format_date_mdy(trans_date),
                    'Description': self.clean_description(self.get_column_value(row, 'Description')),
                    'Category': '',  # Will be empty for user to categorize
                    'Amount': amount,
                    'Account': self.get_account_name(),
                    'Account #': str(self.get_column_value(row, 'Account Number')),
                    'Institution': self.get_institution_name(),
                    'Year': self.format_date_mdy(year_start),
                    'Month': self.format_date_mdy(month_start),
                    'Week': self.format_date_mdy(week_start),
                    'Check Number': '',  # Not applicable for most transactions
                    'Full Description': str(self.get_column_value(row, 'Description')),
                    'Date Added': self.format_date_mdy(datetime.now())
                }
                
                # Filter to only include columns that exist in the Excel file
                filtered_transaction = {
                    col: transaction.get(col, '')
                    for col in existing_columns
                }
                
                transformed_transactions.append(filtered_transaction)
                
            except (ValueError, TypeError, AttributeError, KeyError) as row_error:
                logger.error("Error processing row %d: %s", index, row_error)
                logger.debug("Row data: %s", dict(row))
                logger.info("Skipping this transaction and continuing...")
                continue
        
        return transformed_transactions

    def import_transactions(self, csv_file: str, excel_file: str) -> Tuple[bool, str]:
        """
        Main import function that processes a CSV file and adds transactions to an Excel file.
        
        This method orchestrates the entire import process:
        1. Validates input files exist and have correct extensions
        2. Reads and validates the CSV file structure
        3. Loads the target Excel file
        4. Transforms CSV transactions to standardized format
        5. Adds new transactions to Excel (avoiding duplicates)
        6. Saves the updated Excel file
        
        Args:
            csv_file (str): Path to the CSV file containing transaction data to import
            excel_file (str): Path to the Excel file where transactions will be added
        
        Returns:
            Tuple[bool, str]: A tuple containing:
                - bool: True if the operation completed successfully (with or without new transactions),
                       False if an error occurred
                - str: A descriptive message about the operation result:
                      - Success message with count of new transactions imported
                      - Message indicating no new transactions were found
                      - Error message describing what went wrong
        
        Raises:
            FileNotFoundError: If CSV or Excel file doesn't exist
            ValueError: If file extensions are incorrect or CSV format is invalid
            Various other exceptions: For CSV parsing errors, Excel access issues, etc.
        
        Example:
            >>> success, message = import_transactions("transactions.csv", "budget.xlsx")
            >>> if success:
            ...     print(f"Import completed: {message}")
            ... else:
            ...     print(f"Import failed: {message}")
        """
        try:
            # Initialize handlers
            csv_handler = CSVHandler(csv_file)
            excel_handler = ExcelHandler(excel_file)
            
            # Validate files
            csv_handler.validate_file()
            
            # Read and validate CSV
            logger.info("Reading CSV file: %s", csv_file)
            df = csv_handler.read_csv()
            csv_handler.validate_columns(self.get_expected_columns())
            logger.info("Found %d transactions in CSV", len(df))
            
            # Load Excel file
            excel_handler.load_workbook()
            existing_columns = excel_handler.existing_columns
            logger.debug("Excel file has %d columns: %s", len(existing_columns), existing_columns)
            
            # Transform transactions
            logger.info("Transforming transactions...")
            transactions = self.transform_transactions(df, existing_columns)
            
            # Update Excel file
            logger.info("Updating Excel file: %s", excel_file)            
            count = excel_handler.update_transactions(transactions)
            excel_handler.save()            
            
            if count > 0:
                logger.info("Successfully imported %d new transactions!", count)
                return True, f"Successfully imported {count} new transactions!"
            
            logger.warning("No new transactions to import (all appear to be duplicates)")
            return True, "No new transactions to import (all appear to be duplicates)"
            
        except (ValueError, FileNotFoundError, OSError, pd.errors.EmptyDataError, 
                pd.errors.ParserError, AttributeError, KeyError) as e:
            logger.error("Error during import: %s", e)
            logger.debug("Traceback:\n%s", traceback.format_exc())
            return False, str(e) 