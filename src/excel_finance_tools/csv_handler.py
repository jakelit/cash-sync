"""
This module provides the CSVHandler class for reading and validating CSV files.
"""
import os
import pandas as pd
from typing import List

class CSVHandler:
    """A utility class to handle reading and validating CSV files."""
    
    def __init__(self, csv_file: str):
        self.csv_file = csv_file
    
    def validate_file(self):
        """Validate that the CSV file exists and is accessible."""
        if not os.path.exists(self.csv_file):
            raise FileNotFoundError(f"CSV file not found: {self.csv_file}")
        
        if not self.csv_file.lower().endswith('.csv'):
            raise ValueError("File must be a CSV file")
    
    def read_csv(self) -> pd.DataFrame:
        """Read and parse CSV file with multiple encoding attempts."""
        try:
            # Try different encodings in case of special characters
            encodings = ['utf-8', 'latin-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(self.csv_file, encoding=encoding)
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
    
    def validate_columns(self, expected_columns: List[str]) -> None:
        """Validate that all expected columns are present in the CSV."""
        df = self.read_csv()
        missing_columns = set(expected_columns) - set(df.columns)
        
        if missing_columns:
            available_cols = list(df.columns)
            suggestion_msg = f"\nAvailable columns in your CSV: {available_cols}"
            error_msg = f"Your CSV file is missing some required columns: {missing_columns}.{suggestion_msg}\n\n"
            error_msg += "This usually means either:\n"
            error_msg += "1. The CSV file is from a different bank than selected\n"
            error_msg += "2. The CSV file format has changed\n"
            error_msg += "3. The CSV file was exported incorrectly\n\n"
            error_msg += "Please check that you selected the correct bank and that the CSV file is properly exported."
            raise ValueError(error_msg) 