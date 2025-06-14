import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter, range_boundaries
from openpyxl.worksheet.datavalidation import DataValidation
from typing import List, Dict, Any
from .duplicate_checker import DuplicateChecker
from datetime import datetime
from copy import copy

class ExcelHandler:
    """
    Excel handler that properly works with Excel Tables.
    
    Key fixes:
    1. Creates proper Excel Table if missing
    2. Uses table.ref expansion instead of manual row insertion
    3. Preserves formatting through table structure
    """
    
    def __init__(self, excel_file: str):
        self.excel_file = excel_file
        self.wb = None
        self.ws = None
        self.table = None
        self.existing_df = None
        self.existing_columns = None
    
    def load_workbook(self):
        """Load the Excel workbook and locate the Transactions table."""
        print(f"Loading workbook: {self.excel_file}")
        self.wb = load_workbook(self.excel_file)
        
        # Find the Transactions table across all worksheets
        transactions_table = None
        table_worksheet = None
        
        for sheet_name in self.wb.sheetnames:
            ws = self.wb[sheet_name]
            if ws.tables:
                print(f"Found {len(ws.tables)} table(s) in worksheet '{sheet_name}': {list(ws.tables.keys())}")
                for table_name in ws.tables:
                    if table_name.lower() == 'transactions':
                        transactions_table = ws.tables[table_name]
                        table_worksheet = ws
                        print(f"Found 'Transactions' table in worksheet '{sheet_name}'")
                        break
                if transactions_table:
                    break
        
        if not transactions_table:
            self._raise_table_missing_error()
        
        self.table = transactions_table
        self.ws = table_worksheet
        
        print(f"Table range: {self.table.ref}")
        self._load_existing_data()
    
    def _raise_table_missing_error(self):
        """Raise a clear error with instructions for creating the Transactions table."""
        error_message = """
❌ ERROR: No 'Transactions' table found in the Excel file.

🔧 HOW TO FIX THIS:

1. Open your Excel file
2. Select your transaction data (including headers)
3. Go to Insert → Table (or press Ctrl+T)
4. Make sure "My table has headers" is checked
5. Click OK
6. Right-click the table and select "Table Design"
7. In the "Table Name" box, change the name to: Transactions
8. Save your file

💡 WHY THIS IS REQUIRED:
Excel Tables automatically preserve formatting, data validation, and conditional 
formatting when new rows are added. This eliminates the need for complex 
formatting management in the code.

📋 TABLE REQUIREMENTS:
- Table name must be exactly: Transactions
- Must include column headers
- Should contain your existing transaction data
        """
        raise ValueError(error_message.strip())
    
    def _load_existing_data(self):
        """Load existing data from the Transactions table."""
        # Get table range
        min_col, min_row, max_col, max_row = range_boundaries(self.table.ref)
        
        # Load data from the specific table range
        self.existing_df = pd.read_excel(
            self.excel_file, 
            sheet_name=self.ws.title,
            usecols=f"{get_column_letter(min_col)}:{get_column_letter(max_col)}",
            skiprows=min_row - 1,  # Skip to header row
            nrows=max_row - min_row  # Read only table rows
        )
        
        self.existing_columns = list(self.existing_df.columns)
        print(f"Loaded {len(self.existing_df)} existing transactions")
        print(f"Table columns: {self.existing_columns}")
    
    def update_transactions(self, transactions: List[Dict[str, Any]]) -> int:
        """Add new transactions to the Transactions table."""
        # Check for duplicates
        filtered_transactions = DuplicateChecker.check_for_duplicates(
            self.existing_df, transactions
        )
        
        if not filtered_transactions:
            print("No new transactions to import (all appear to be duplicates)")
            return 0
        
        print(f"Adding {len(filtered_transactions)} new transactions...")
        
        # Validate that transaction columns match table columns
        self._validate_transaction_columns(filtered_transactions[0])
        
        # Add transactions to the table using proper method
        rows_added = self._add_transactions_to_table(filtered_transactions)
        
        print(f"Successfully added {rows_added} transactions to the table")
        return rows_added
    
    def _add_transactions_to_table(self, transactions: List[Dict[str, Any]]) -> int:
        """
        Add transactions using proper table expansion method.
        This preserves formatting and table features.
        """
        # Get current table boundaries
        min_col, min_row, max_col, current_max_row = range_boundaries(self.table.ref)
        
        # Sort transactions by date (newest first)
        sorted_transactions = self._sort_transactions_by_date(transactions)
        
        # Store the last data row for formatting reference
        last_data_row = current_max_row
        
        # Calculate new table dimensions
        new_max_row = current_max_row + len(transactions)
        new_table_range = f"{get_column_letter(min_col)}{min_row}:{get_column_letter(max_col)}{new_max_row}"
        
        # STEP 1: Expand table range first
        self.table.ref = new_table_range
        print(f"Expanded table range to: {new_table_range}")
        
        # STEP 2: Add new rows and copy formatting from the last data row
        for i, transaction in enumerate(sorted_transactions):
            new_row_num = current_max_row + 1 + i
            
            # Copy row formatting from the last data row
            self._copy_row_formatting(last_data_row, new_row_num, min_col, max_col)
            
            # Populate the row with data
            self._populate_table_row(new_row_num, transaction, min_col)
        
        # STEP 3: Now extend conditional formatting and data validation rules AFTER table expansion
        # Look for rules that applied to complete columns ending at the old boundary
        self._extend_conditional_formatting(min_col, min_row, max_col, current_max_row, new_max_row)
        self._extend_data_validation(min_col, min_row, max_col, current_max_row, new_max_row)
        
        return len(transactions)

    def _copy_row_formatting(self, source_row: int, target_row: int, min_col: int, max_col: int):
        """Copy formatting from source row to target row."""
        for col in range(min_col, max_col + 1):
            source_cell = self.ws.cell(row=source_row, column=col)
            target_cell = self.ws.cell(row=target_row, column=col)
            
            # Copy cell formatting
            if source_cell.has_style:
                target_cell.font = copy(source_cell.font)
                target_cell.border = copy(source_cell.border)
                target_cell.fill = copy(source_cell.fill)
                target_cell.number_format = source_cell.number_format
                target_cell.protection = copy(source_cell.protection)
                target_cell.alignment = copy(source_cell.alignment)

    def _extend_conditional_formatting(self, min_col: int, min_row: int, max_col: int, old_max_row: int, new_max_row: int):
        """Extend conditional formatting rules that apply to entire table columns."""
        # First data row (skipping header)
        first_data_row = min_row + 1
        
        rules_updated = 0
        rules_to_recreate = []
        for cf in self.ws.conditional_formatting:
            ranges_to_update = []
            for range_obj in list(cf.cells.ranges):
                try:
                    # Get the coordinate string from the CellRange object
                    range_str = range_obj.coord  # This gives you "D2:D18" format
                    
                    # Parse the range to see if it's a complete table column
                    cf_min_col, cf_min_row, cf_max_col, cf_max_row = range_boundaries(range_str)
                    
                    # Check if this is a complete column rule:
                    # 1. Single column (min_col == max_col)
                    # 2. Within table columns
                    # 3. Starts at first data row
                    # 4. Ends at old table boundary
                    if (cf_min_col == cf_max_col and  # Single column
                        cf_min_col >= min_col and cf_max_col <= max_col and  # Within table
                        cf_min_row == first_data_row and  # Starts at first data row
                        cf_max_row == old_max_row):  # Ends at old table end
                                                
                        # Store rule info for recreation
                        new_range_str = f"{get_column_letter(cf_min_col)}{first_data_row}:{get_column_letter(cf_max_col)}{new_max_row}"
                        
                        for rule in cf.rules:
                            rules_to_recreate.append((new_range_str, rule))
                            rules_updated += 1
                            print(f"Will recreate rule for range {new_range_str}")
                        
                        # Remove the old conditional formatting
                        self.ws.conditional_formatting._cf_rules.pop(cf, None)

                        print(f"Extended conditional formatting from {range_str} to {new_range_str}")
                        
                except Exception as e:
                    import traceback
                    print(f"Failed to process conditional formatting range {range_str}:")
                    print(f"Details: {str(e)}")
                    print(f"Traceback:\n{traceback.format_exc()}")
                    continue
            
            # Re-add the conditional formatting rules with new ranges
            for range_str, rule in rules_to_recreate:
                self.ws.conditional_formatting.add(range_str, rule)
        
        if rules_updated == 0:
            print("Note: No complete column conditional formatting rules were found to extend")

    def _extend_data_validation(self, min_col: int, min_row: int, max_col: int, old_max_row: int, new_max_row: int):
        """Extend data validation rules that apply to entire table columns."""
        # First data row (skipping header)
        first_data_row = min_row + 1
        
        rules_updated = 0
        validations_to_recreate = []
        
        # Find data validation rules that need updating
        for dv in list(self.ws.data_validations.dataValidation):
            for range_obj in dv.cells.ranges:
                try:
                    range_str = range_obj.coord
                    dv_min_col, dv_min_row, dv_max_col, dv_max_row = range_boundaries(range_str)
                    
                    if (dv_min_col == dv_max_col and  # Single column
                        dv_min_col >= min_col and dv_max_col <= max_col and  # Within table
                        dv_min_row == first_data_row and  # Starts at first data row
                        dv_max_row == old_max_row):  # Ends at old table end
                        
                        # Store validation info for recreation
                        new_range_str = f"{get_column_letter(dv_min_col)}{first_data_row}:{get_column_letter(dv_max_col)}{new_max_row}"
                        validations_to_recreate.append((dv, new_range_str))
                        rules_updated += 1
                        print(f"Will recreate data validation for range {new_range_str}")
                        break  # Move to next data validation rule
                            
                except Exception as e:
                    print(f"Error processing data validation range {range_obj}: {e}")
                    continue
        
        # Remove old validations and add new ones
        for old_dv, new_range_str in validations_to_recreate:
            # Remove old validation
            self.ws.data_validations.dataValidation.remove(old_dv)
            
            # Create new validation with same properties but new range
            new_dv = DataValidation(
                type=old_dv.type,
                formula1=old_dv.formula1,
                formula2=old_dv.formula2,
                showErrorMessage=old_dv.showErrorMessage,
                errorTitle=old_dv.errorTitle,
                error=old_dv.error,
                showInputMessage=old_dv.showInputMessage,
                promptTitle=old_dv.promptTitle,
                prompt=old_dv.prompt,
                allow_blank=old_dv.allow_blank
            )
            
            # Add the new range
            new_dv.add(new_range_str)
            
            # Add to worksheet
            self.ws.data_validations.append(new_dv)
        
        if rules_updated == 0:
            print("Note: No complete column data validation rules were found to extend")
   
    def _populate_table_row(self, row_num: int, transaction: Dict[str, Any], start_col: int):
        """Populate a table row with transaction data."""
        for i, col_name in enumerate(self.existing_columns):
            col_idx = start_col + i
            cell = self.ws.cell(row=row_num, column=col_idx)
            
            value = transaction.get(col_name)
            
            if pd.isna(value) or value is None:
                cell.value = None
            elif isinstance(value, (pd.Timestamp, datetime)):
                cell.value = value
            elif isinstance(value, (int, float)):
                cell.value = value
            else:
                cell.value = str(value) if value is not None else None
    
    def _validate_transaction_columns(self, sample_transaction: Dict[str, Any]):
        """Validate transaction columns match table structure."""
        transaction_columns = set(sample_transaction.keys())
        table_columns = set(self.existing_columns)
        
        missing_in_table = transaction_columns - table_columns
        if missing_in_table:
            raise ValueError(
                f"Transaction data contains columns not in the table: {missing_in_table}\n"
                f"Table columns: {table_columns}"
            )
    
    def _sort_transactions_by_date(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort transactions by date, newest first."""
        def get_date_key(transaction):
            date_val = transaction.get('Date')
            if not date_val:
                return datetime.min
            
            try:
                if isinstance(date_val, str):
                    return pd.to_datetime(date_val)
                elif isinstance(date_val, datetime):
                    return date_val
                else:
                    return datetime.min
            except:
                return datetime.min
        
        return sorted(transactions, key=get_date_key, reverse=True)
    
    def save(self):
        """Save the workbook."""
        print(f"Saving workbook to: {self.excel_file}")
        self.wb.save(self.excel_file)
        self.wb.close()
        print("Workbook saved and closed successfully")
