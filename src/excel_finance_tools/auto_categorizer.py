from .excel_handler import ExcelHandler
from .logger import logger
import pandas as pd
from typing import Dict, List
import traceback
import re

class AutoCategorizer:
    """
    Automatically categorizes uncategorized transactions in an Excel file by applying pattern matching rules defined in the AutoCat worksheet.
    """
    
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

    def run_auto_categorization(self) -> tuple[bool, str]:
        """
        Main method to run the auto-categorization process.
        
        Returns:
            A tuple of (bool, str) indicating success and a message.
        """
        logger.info(f"Starting auto-categorization for '{self.excel_file}'...")
        try:
            # 1. Load the workbook and data using ExcelHandler.
            # This is the single point where the "Transactions" table is found and loaded.
            self.excel_handler.load_workbook()
            
            # 2. Get transactions that need categorization
            uncategorized_df = self._get_uncategorized_transactions()
            if uncategorized_df.empty:
                logger.warning("No uncategorized transactions found to process.")
                return True, "No uncategorized transactions to process."

            logger.info(f"Found {len(uncategorized_df)} uncategorized transactions.")

            # 3. Load categorization rules
            self._load_and_parse_rules()
            if not self.rules:
                logger.warning("No valid categorization rules found in 'AutoCat' sheet.")
                return True, "No valid categorization rules found in 'AutoCat' sheet."
            logger.info(f"Successfully loaded and parsed {len(self.rules)} rules.")

            # 4. Apply rules to transactions
            categorized_count = self._apply_rules_to_transactions(uncategorized_df)
            if categorized_count == 0:
                logger.warning("No new transactions were categorized based on the existing rules.")
                return True, "Completed. No updates were applied based on the rules."

            logger.info(f"Successfully categorized {categorized_count} transactions.")

            # 5. Save the workbook
            self.excel_handler.save()

            return True, f"Successfully categorized {categorized_count} transactions!"

        except Exception as e:
            logger.error(f"An error occurred during auto-categorization: {e}")
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
        rules_df = self.excel_handler.get_autocat_rules()
        if rules_df is None or rules_df.empty:
            self.rules = []
            return

        if 'Category' not in rules_df.columns:
            logger.error("The 'AutoCat' sheet must contain a 'Category' column.")
            self.rules = []
            return

        for index, row in rules_df.iterrows():
            # A rule that does not specify a category should not be skipped.
            # It may contain other auto-fill instructions.
            # if pd.isna(row['Category']):
            #     continue

            rule = {'category': row['Category'], 'conditions': [], 'auto_fill': {}}
            
            # A mapping of user-friendly names to internal types
            valid_comparisons = {
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

            for col_name, value in row.items():
                if pd.isna(value) or col_name == 'Category':
                    continue
                
                is_rule_column = False
                # Check if the column name ends with a valid comparison type
                for comp_display, comp_internal in valid_comparisons.items():
                    if col_name.lower().endswith(' ' + comp_display):
                        # It's a rule column
                        field = col_name[:-(len(comp_display) + 1)] # Extract the field name
                        if field in self.excel_handler.existing_columns:
                            rule['conditions'].append({'field': field, 'type': comp_internal, 'value': value})
                        else:
                            logger.warning(f"Rule column '{col_name}' ignored: '{field}' not found in Transactions table.")
                        is_rule_column = True
                        break # Move to next column
                
                if is_rule_column:
                    continue

                # If it wasn't a rule column, check if it's an auto-fill column
                if col_name in self.excel_handler.existing_columns:
                    rule['auto_fill'][col_name] = value
                else:
                    logger.warning(f"Column '{col_name}' in 'AutoCat' sheet is not a valid rule or auto-fill column and will be ignored.")
            
            if rule['conditions']:
                self.rules.append(rule)

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
        field = condition['field']
        comp_type = condition['type']
        rule_value = condition['value']
        
        trans_value = transaction.get(field)
        if pd.isna(trans_value):
            return False
            
        try:
            # Type-specific comparisons
            if comp_type == 'contains':
                return str(rule_value).lower() in str(trans_value).lower()
            if comp_type == 'not_contains':
                return str(rule_value).lower() not in str(trans_value).lower()
            if comp_type == 'equals':
                # Exact match, but handle types
                return str(trans_value) == str(rule_value)
            if comp_type == 'not_equals':
                return str(trans_value) != str(rule_value)
            if comp_type == 'starts_with':
                return str(trans_value).lower().startswith(str(rule_value).lower())
            if comp_type == 'ends_with':
                return str(trans_value).lower().endswith(str(rule_value).lower())
            if comp_type == 'min':
                return float(trans_value) >= float(rule_value)
            if comp_type == 'max':
                return float(trans_value) <= float(rule_value)
            if comp_type == 'between':
                min_val, max_val = map(float, str(rule_value).split(','))
                return min_val <= float(trans_value) <= max_val
            if comp_type == 'regex':
                if rule_value not in self._regex_cache:
                    self._regex_cache[rule_value] = re.compile(rule_value, re.IGNORECASE)
                return self._regex_cache[rule_value].search(str(trans_value)) is not None
        except (ValueError, TypeError) as e:
            logger.debug(f"Could not evaluate condition {condition} for value {trans_value}: {e}")
            return False
        return False

    def _update_transaction(self, df_index: int, category: str, auto_fill_values: Dict):
        logger.debug(f"Updating transaction at index {df_index} with Category '{category}' and auto-fills: {auto_fill_values}")
        self.excel_handler.update_cell(df_index, 'Category', category)
        for col, value in auto_fill_values.items():
            self.excel_handler.update_cell(df_index, col, value)