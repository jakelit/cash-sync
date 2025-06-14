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
from .importer_gui import ImporterGUI
from .logger import logger

# Available banks
BANKS = {
    "ally": AllyImporter,
    "capitalone": CapitalOneImporter    
}

def main():
    parser = argparse.ArgumentParser(
        description='Import bank CSV transactions to Excel',
        epilog='''
Examples:
  python script.py capitalone transactions.csv transactions.xlsx
  python script.py ally transactions.csv transactions.xlsx
  python script.py  # Opens GUI dialog
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('bank', nargs='?', choices=list(BANKS.keys()), 
                       help='Bank to import from (capitalone or ally)')
    parser.add_argument('csv_file', nargs='?', help='Path to bank CSV file')
    parser.add_argument('excel_file', nargs='?', help='Path to Excel file')
    parser.add_argument('--version', action='version', version='Bank to Excel Importer 1.0')
    
    args = parser.parse_args()
    
    # If all arguments provided via command line, process directly
    if args.bank and args.csv_file and args.excel_file:
        logger.info("Bank to Excel Importer")
        logger.info("=" * 40)
        importer = BANKS[args.bank]()
        success, message = importer.import_transactions(args.csv_file, args.excel_file)
        logger.info("\n" + "=" * 40)
        if success:
            logger.info("Import completed successfully!")
        else:
            logger.error("Import failed!")
            sys.exit(1)
    else:
        # Show GUI dialog
        try:
            gui = ImporterGUI()
            gui.run()
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
    'DuplicateChecker'
]