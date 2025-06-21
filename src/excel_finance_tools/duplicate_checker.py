"""
This module provides the DuplicateChecker class to identify and filter
duplicate transactions.
"""
from typing import List, Dict, Any
import pandas as pd


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
            date_str = str(row.get('Date', ''))
            amount_str = str(row.get('Amount', ''))
            desc_str = str(row.get('Full Description', ''))[:20].strip()
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