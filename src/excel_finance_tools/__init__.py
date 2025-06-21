"""
Bank CSV to Excel Importer

This script imports transactions from bank CSV files into an Excel spreadsheet.
The Excel spreadsheet must have a worksheet named "Transactions" with a table called "Transactions".
The table must have the following columns:
- Date
- Description
- Category
- Amount
- Account
- Account #

The columns can be in any order. If the Excel file does not have the required worksheet or table,
or if any required columns are missing, the script will raise an error and exit.

It supports multiple banks including Ally and CapitalOne.
It can be used from command line or with a GUI dialog for file selection.

Usage:
    python script.py [bank] [csv_file] [excel_file]
    python script.py  # Opens GUI dialog

Requirements:
    pip install pandas openpyxl
"""

import sys
import argparse
from .capital_one_importer import CapitalOneImporter
from .ally_importer import AllyImporter
from .base_importer import BaseImporter
from .importer_interface import TransactionImporter
from .excel_handler import ExcelHandler
from .csv_handler import CSVHandler
from .duplicate_checker import DuplicateChecker
from .main_gui import ExcelFinanceToolsApp
from .logger import logger
from .auto_categorizer import AutoCategorizer

# Available banks
BANKS = {
    "ally": AllyImporter,
    "capitalone": CapitalOneImporter    
}

def main():
    parser = argparse.ArgumentParser(
        description='Excel Finance Tools.',
        epilog='''
Examples:
  python run.py import capitalone transactions.csv my_finances.xlsx
  python run.py autocat my_finances.xlsx
  python run.py  # Opens the main GUI
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # --- Import Command ---
    import_parser = subparsers.add_parser('import', help='Import transactions from a CSV file.')
    import_parser.add_argument('bank', choices=list(BANKS.keys()), help='Bank name (e.g., capitalone, ally).')
    import_parser.add_argument('csv_file', help='Path to the bank CSV file.')
    import_parser.add_argument('excel_file', help='Path to your main Excel file.')

    # --- Auto-Categorize Command ---
    autocat_parser = subparsers.add_parser('autocat', help='Automatically categorize transactions in an Excel file.')
    autocat_parser.add_argument('excel_file', help='Path to the Excel file to categorize.')

    parser.add_argument('--version', action='version', version='Excel Finance Tools 1.1')
    
    args = parser.parse_args()
    
    if args.command == 'import':
        logger.info("Running Transaction Importer...")
        logger.info("=" * 40)
        importer = BANKS[args.bank]()
        success, message = importer.import_transactions(args.csv_file, args.excel_file)
        logger.info("=" * 40)
        if success:
            logger.info(f"Import completed: {message}")
        else:
            logger.error(f"Import failed: {message}")
            sys.exit(1)
            
    elif args.command == 'autocat':
        logger.info("Running Auto-Categorizer...")
        logger.info("=" * 40)
        categorizer = AutoCategorizer(args.excel_file)
        success, message = categorizer.run_auto_categorization()
        logger.info("=" * 40)
        if success:
            logger.info(f"Auto-categorization completed: {message}")
        else:
            logger.error(f"Auto-categorization failed: {message}")
            sys.exit(1)
            
    else: # This handles no command being provided
        # Show main GUI dialog
        logger.info("No command provided, starting GUI...")
        try:
            app = ExcelFinanceToolsApp()
            app.run()
        except Exception as e:
            logger.error(f"Error starting GUI: {e}")
            logger.error("Please ensure tkinter is installed: pip install tkinter")
            sys.exit(1)

if __name__ == "__main__":
    main()

__all__ = [
    'CapitalOneImporter',
    'AllyImporter',
    'BaseImporter',
    'TransactionImporter',
    'ExcelHandler',
    'CSVHandler',
    'DuplicateChecker',
    'ExcelFinanceToolsApp',
    'AutoCategorizer'
]