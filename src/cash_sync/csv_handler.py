"""
This module provides the CSVHandler class for reading and validating CSV files.
"""
import os
from typing import List
import pandas as pd

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
                raise ValueError("Could not read CSV file with any supported encoding")
            
            # Strip whitespace from column names
            df.columns = df.columns.str.strip()
            
            # Remove any completely empty rows
            df = df.dropna(how='all')
            
            return df
            
        except (ValueError, OSError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:            
            raise ValueError(f"Error reading CSV file: {str(e)}") from e
    
 