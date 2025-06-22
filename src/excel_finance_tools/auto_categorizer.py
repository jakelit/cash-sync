"""
This module contains the AutoCategorizer class for automatically categorizing transactions.
"""
import re
import traceback
from typing import Dict, List

import pandas as pd

from .excel_handler import ExcelHandler
from .logger import logger


class AutoCategorizer:
    """
    Automatically categorizes uncategorized transactions in an Excel file by
    applying pattern matching rules defined in the AutoCat worksheet.
    """

    # A mapping of user-friendly names to internal types
    VALID_COMPARISONS = {
        'contains': 'contains',
        'not contains': 'not_contains',
        'equals': 'equals',
        'not equals': 'not_equals',
        'starts with': 'starts_with',
        'ends with': 'ends_with',
        'min': 'min',
        'max': 'max',
        'between': 'between',
        'regex': 'regex'
    }

    def __init__(self, excel_file: str):
        """
        Initialize the AutoCategorizer with the path to the Excel file.
        Args:
            excel_file (str): Path to the Excel file containing transactions.
        """
        self.excel_file = excel_file
        self.excel_handler = ExcelHandler(excel_file)
        self.rules = []
        self._regex_cache = {}
        self._comparison_methods = {
            'contains': self._compare_contains,
            'not_contains': self._compare_not_contains,
            'equals': self._compare_equals,
            'not_equals': self._compare_not_equals,
            'starts_with': self._compare_starts_with,
            'ends_with': self._compare_ends_with,
            'min': self._compare_min,
            'max': self._compare_max,
            'between': self._compare_between,
            'regex': self._compare_regex,
        }

    def run_auto_categorization(self) -> tuple[bool, str]:
        """
        Main method to run the auto-categorization process.
        Returns:
            A tuple of (bool, str) indicating success and a message.
        """
        logger.info("Starting auto-categorization for '%s'...", self.excel_file)
        try:
            # 1. Load the workbook and data using ExcelHandler.
            self.excel_handler.load_workbook()

            # 2. Get transactions that need categorization
            uncategorized_df = self._get_uncategorized_transactions()
            if uncategorized_df.empty:
                logger.warning("No uncategorized transactions found to process.")
                return True, "No uncategorized transactions to process."

            logger.info("Found %d uncategorized transactions.", len(uncategorized_df))

            # 3. Load categorization rules
            self._load_and_parse_rules()
            if not self.rules:
                logger.warning("No valid categorization rules found in 'AutoCat' sheet.")
                return True, "No valid categorization rules found in 'AutoCat' sheet."
            logger.info("Successfully loaded and parsed %d rules.", len(self.rules))

            # 4. Apply rules to transactions
            categorized_count = self._apply_rules_to_transactions(uncategorized_df)
            if categorized_count == 0:
                logger.warning("No new transactions were categorized based on the existing rules.")
                return True, "Completed. No updates were applied based on the rules."

            logger.info("Successfully categorized %d transactions.", categorized_count)

            # 5. Save the workbook
            self.excel_handler.save()

            return True, f"Successfully categorized {categorized_count} transactions!"

        except (ValueError, FileNotFoundError, PermissionError, OSError) as e:
            logger.error("An error occurred during auto-categorization: %s", e)
            logger.debug(traceback.format_exc())
            return False, f"An error occurred: {e}"

    def _get_uncategorized_transactions(self) -> pd.DataFrame:
        """
        Filters the DataFrame from ExcelHandler to find rows where 'Category' is empty.
        """
        logger.debug("Filtering for uncategorized transactions...")
        df = self.excel_handler.existing_df

        if 'Category' not in df.columns:
            raise ValueError("The 'Transactions' table must contain a 'Category' column.")
            
        # Ensure the index is a standard range index for reliable lookups
        df = df.reset_index(drop=True)

        uncategorized_mask = df['Category'].isnull() | (df['Category'] == '')
        return df[uncategorized_mask]

    def _load_and_parse_rules(self):
        """Load and parse categorization rules from the AutoCat sheet."""
        rules_df = self.excel_handler.get_autocat_rules()
        if rules_df is None or rules_df.empty:
            logger.warning("AutoCat worksheet not found or empty")
            self.rules = []
            return

        if 'Category' not in rules_df.columns:
            logger.error("The 'AutoCat' sheet must contain a 'Category' column.")
            self.rules = []
            return

        for _, row in rules_df.iterrows():
            rule = self._parse_single_rule(row)
            if rule['conditions']:
                self.rules.append(rule)

    def _parse_single_rule(self, row: pd.Series) -> dict:
        """Parse a single rule from a row in the AutoCat sheet."""
        rule = {'category': row['Category'], 'conditions': [], 'auto_fill': {}}
        
        for col_name, value in row.items():
            if pd.isna(value) or col_name == 'Category':
                continue

            # Check if it's a rule column
            rule_condition = self._extract_rule_condition(col_name, value)
            if rule_condition:
                rule['conditions'].append(rule_condition)
                continue

            # Check if it's an auto-fill column
            if col_name in self.excel_handler.existing_columns:
                rule['auto_fill'][col_name] = value
            else:
                logger.warning("Column '%s' in 'AutoCat' sheet is not a valid rule or auto-fill column and will be ignored.", col_name)
        
        return rule

    def _extract_rule_condition(self, col_name: str, value: any) -> dict:
        """Extract a rule condition from a column name and value."""
        # Sort comparisons by length (longest first) to avoid partial matches
        sorted_comparisons = sorted(self.VALID_COMPARISONS.items(), key=lambda x: len(x[0]), reverse=True)
        
        for comp_display, comp_internal in sorted_comparisons:
            if col_name.lower().endswith(' ' + comp_display):
                # Extract the field name by removing the comparison part and the space before it
                # Find the position of the comparison pattern (including the space)
                pattern = ' ' + comp_display
                field_end_pos = col_name.lower().rfind(pattern)
                if field_end_pos != -1:
                    field = col_name[:field_end_pos].strip()
                    if field in self.excel_handler.existing_columns:
                        return {'field': field, 'type': comp_internal, 'value': value}
                    logger.warning("Rule column '%s' ignored: '%s' not found in Transactions table.", col_name, field)
                break
        return None

    def _apply_rules_to_transactions(self, transactions_df: pd.DataFrame) -> int:
        categorized_count = 0
        for df_index, transaction in transactions_df.iterrows():
            for rule in self.rules:
                if self._is_match(transaction, rule['conditions']):
                    # First match wins
                    self._update_transaction(df_index, rule['category'], rule['auto_fill'])
                    categorized_count += 1
                    break
        return categorized_count

    def _is_match(self, transaction: pd.Series, conditions: List[Dict]) -> bool:
        # ALL conditions must be met (AND logic)
        return all(self._evaluate_condition(transaction, cond) for cond in conditions)

    def _evaluate_condition(self, transaction: pd.Series, condition: Dict) -> bool:
        field, comp_type, rule_value = condition['field'], condition['type'], condition['value']
        trans_value = transaction.get(field)

        if pd.isna(trans_value):
            return False

        comparison_func = self._comparison_methods.get(comp_type)
        if not comparison_func:
            logger.warning("Unknown comparison type: %s", comp_type)
            return False

        try:
            return comparison_func(trans_value, rule_value)
        except (ValueError, TypeError) as e:
            logger.debug(
                "Could not evaluate condition %s for value %s: %s",
                condition, trans_value, e
            )
            return False

    # --- Comparison Methods ---
    def _compare_contains(self, trans_value, rule_value) -> bool:
        return str(rule_value).lower() in str(trans_value).lower()

    def _compare_not_contains(self, trans_value, rule_value) -> bool:
        return str(rule_value).lower() not in str(trans_value).lower()

    def _compare_equals(self, trans_value, rule_value) -> bool:
        return str(trans_value) == str(rule_value)

    def _compare_not_equals(self, trans_value, rule_value) -> bool:
        return str(trans_value) != str(rule_value)

    def _compare_starts_with(self, trans_value, rule_value) -> bool:
        return str(trans_value).lower().startswith(str(rule_value).lower())

    def _compare_ends_with(self, trans_value, rule_value) -> bool:
        return str(trans_value).lower().endswith(str(rule_value).lower())

    def _compare_min(self, trans_value, rule_value) -> bool:
        return float(trans_value) >= float(rule_value)

    def _compare_max(self, trans_value, rule_value) -> bool:
        return float(trans_value) <= float(rule_value)

    def _compare_between(self, trans_value, rule_value) -> bool:
        min_val, max_val = map(float, str(rule_value).split(','))
        return min_val <= float(trans_value) <= max_val

    def _compare_regex(self, trans_value, rule_value) -> bool:
        if rule_value not in self._regex_cache:
            self._regex_cache[rule_value] = re.compile(rule_value, re.IGNORECASE)
        return self._regex_cache[rule_value].search(str(trans_value)) is not None

    def _update_transaction(self, df_index: int, category: str, auto_fill_values: Dict):
        # Get the transaction description for better logging
        transaction = self.excel_handler.existing_df.iloc[df_index]
        description = transaction.get('Description', 'Unknown')
        
        logger.debug("Categorizing transaction '%s' (index %d) as '%s' with auto-fills: %s", 
                     description, df_index, category, auto_fill_values)
        self.excel_handler.update_cell(df_index, 'Category', category)
        for col, value in auto_fill_values.items():
            self.excel_handler.update_cell(df_index, col, value)