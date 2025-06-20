import os
import pandas as pd
from datetime import datetime, timedelta
import re
from abc import abstractmethod
import re
from typing import List, Dict, Any, Tuple
import traceback
from .csv_handler import CSVHandler
from .excel_handler import ExcelHandler
from .importer_interface import TransactionImporter
from .logger import logger


class BaseImporter(TransactionImporter):
    """Base class for importing transactions from bank CSV files to Excel."""
    
    def __init__(self):
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
        """Return the expected columns for this bank's CSV file."""
        pass
    
    @abstractmethod
    def get_institution_name(self):
        """Return the institution name for this bank."""
        pass
    
    @abstractmethod
    def get_account_name(self):
        """Return the default account name for this bank."""
        pass
    
    @abstractmethod
    def parse_transaction_amount(self, amount_str, transaction_type=None):
        """Parse transaction amount and determine if it's a debit or credit."""
        pass

    def set_column_mapping(self, source_column: str, target_column: str):
        """Set a custom column mapping for this bank."""
        self.column_mappings[target_column] = source_column
    
    def set_default_value(self, column: str, value: Any):
        """Set a default value for a column if it's missing in the CSV."""
        self.default_values[column] = value
    
    def get_column_value(self, row: Dict[str, Any], column_name: str) -> str:
        """Get a column value from the row, using mapping and default values if needed."""
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
        """Parse transaction date from string."""
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
                return datetime.now().date()
            return date
                
        except Exception as date_error:
            logger.error(f"Date parsing error: {date_error}")
            logger.debug(f"Raw date value: '{date_str}'")
            return datetime.now().date()

    def validate_files(self, csv_file, excel_file):
        """Validate that input files exist and are accessible."""
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file not found: {csv_file}")
        
        if not os.path.exists(excel_file):
            raise FileNotFoundError(f"Excel file not found: {excel_file}")
        
        if not csv_file.lower().endswith('.csv'):
            raise ValueError("First file must be a CSV file")
        
        if not excel_file.lower().endswith(('.xlsx', '.xls')):
            raise ValueError("Second file must be an Excel file")
    
    def read_csv(self, csv_file):
        """Read and parse CSV file with multiple encoding attempts."""
        try:
            # Try different encodings in case of special characters
            encodings = ['utf-8', 'latin-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_file, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise Exception("Could not read CSV file with any supported encoding")
            
            # Strip whitespace from column names
            df.columns = df.columns.str.strip()
            
            # Remove any completely empty rows
            df = df.dropna(how='all')
            
            return df
            
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}") from e
    
    def get_week_start(self, date):
        """Get the first day of the week (Sunday) for a given date."""
        # Get the weekday (0=Monday, 6=Sunday in Python)
        days_since_sunday = (date.weekday() + 1) % 7
        week_start = date - timedelta(days=days_since_sunday)
        return week_start
    
    def format_date_mdy(self, date_obj):
        """Format date as M/D/YYYY (without leading zeros) - cross-platform compatible."""
        if isinstance(date_obj, str):
            return date_obj
        
        # Use manual formatting to avoid platform-specific strftime issues
        month = date_obj.month
        day = date_obj.day
        year = date_obj.year
        return f"{month}/{day}/{year}"
    
    def clean_description(self, description):
        """Clean and format transaction description to be more human readable."""
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
        """Transform bank transactions to Tiller format based on existing columns."""
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
                
            except Exception as row_error:
                logger.error(f"Error processing row {index}: {row_error}")
                logger.debug(f"Row data: {dict(row)}")
                logger.info("Skipping this transaction and continuing...")
                continue
        
        return transformed_transactions

    def import_transactions(self, csv_file: str, excel_file: str) -> Tuple[bool, str]:
        """Main import function."""
        try:
            # Initialize handlers
            csv_handler = CSVHandler(csv_file)
            excel_handler = ExcelHandler(excel_file)
            
            # Validate files
            csv_handler.validate_file()
            
            # Read and validate CSV
            logger.info(f"Reading CSV file: {csv_file}")
            df = csv_handler.read_csv()
            csv_handler.validate_columns(self.get_expected_columns())
            logger.info(f"Found {len(df)} transactions in CSV")
            
            # Load Excel file
            excel_handler.load_workbook()
            existing_columns = excel_handler.existing_columns
            logger.debug(f"Excel file has {len(existing_columns)} columns: {existing_columns}")
            
            # Transform transactions
            logger.info("Transforming transactions...")
            transactions = self.transform_transactions(df, existing_columns)
            
            # Update Excel file
            logger.info(f"Updating Excel file: {excel_file}")            
            count = excel_handler.update_transactions(transactions)
            excel_handler.save()            
            
            if count > 0:
                logger.info(f"Successfully imported {count} new transactions!")
                return True, f"Successfully imported {count} new transactions!"
            else:
                logger.warning("No new transactions to import (all appear to be duplicates)")
                return True, "No new transactions to import (all appear to be duplicates)"
            
        except Exception as e:
            logger.error(f"Error during import: {e}")
            logger.debug(f"Traceback:\n{traceback.format_exc()}")
            return False, str(e) 