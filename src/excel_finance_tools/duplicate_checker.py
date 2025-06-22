"""
This module provides the DuplicateChecker class to identify and filter
duplicate transactions.
"""
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime


class DuplicateChecker:
    """
    A utility class to check for and filter duplicate transactions between
    a new set of data and an existing dataset.
    """
    
    @staticmethod
    def check_for_duplicates(existing_df: pd.DataFrame, new_transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for potential duplicate transactions and return filtered list."""
        if existing_df.empty or not new_transactions:
            return new_transactions
        
        # Create a comparison key using date, amount, and first 20 chars of Full Description
        # Note: Using Full Description instead of Description because Description is often changed by users. 
        # The Full Description is the original description from the bank and provides more reliable duplicate detection.
        def create_comparison_key(row: Dict[str, Any]) -> str:
            # Normalize date to YYYY-MM-DD format
            date_value = row.get('Date', '')
            if pd.isna(date_value) or date_value == '':
                date_str = ''
            elif isinstance(date_value, (pd.Timestamp, datetime)):
                date_str = date_value.strftime('%Y-%m-%d')
            else:
                # Try to parse string date
                try:
                    parsed_date = pd.to_datetime(str(date_value))
                    date_str = parsed_date.strftime('%Y-%m-%d')
                except:
                    date_str = str(date_value)
            
            # Normalize amount to string with 2 decimal places
            amount_value = row.get('Amount', '')
            if pd.isna(amount_value) or amount_value == '':
                amount_str = ''
            else:
                try:
                    amount_float = float(amount_value)
                    amount_str = f"{amount_float:.2f}"
                except:
                    amount_str = str(amount_value)
            
            # Get description (try Full Description first, then Description)
            desc_value = row.get('Full Description', row.get('Description', ''))
            desc_str = str(desc_value)[:20].strip() if desc_value else ''
            
            return f"{date_str}|{amount_str}|{desc_str}"
        
        # Create comparison keys for existing transactions
        existing_keys = set()
        for _, row in existing_df.iterrows():
            key = create_comparison_key(row)
            existing_keys.add(key)
        
        # Filter out potential duplicates
        filtered_transactions = []
        duplicate_count = 0
        
        for transaction in new_transactions:
            key = create_comparison_key(transaction)
            if key not in existing_keys:
                filtered_transactions.append(transaction)
                existing_keys.add(key)  # Add to existing keys to prevent duplicates within new transactions
            else:
                duplicate_count += 1
        
        if duplicate_count > 0:
            print(f"Filtered out {duplicate_count} potential duplicate transactions")
        
        return filtered_transactions 