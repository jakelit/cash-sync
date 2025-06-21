# Import Transactions Feature Specification

## Overview
The Import Transactions feature allows users to import financial transaction data from CSV files, provided by their financial institutions, into a structured Excel table for tracking and analysis. The feature handles data from different institutions, maps it to a standard format, checks for duplicates, and appends new transactions to a "Transactions" table in the specified Excel file.

## User Interface (GUI)

The import process is managed through a simple and intuitive graphical interface.

### Steps:
1.  **Select Institution**: The user chooses their financial institution from a dropdown list. This determines which data mapping and format to use.
2.  **Select Source CSV File**: The user clicks a "Browse" button to open a file dialog and select the CSV file they downloaded from their bank.
3.  **Select Destination Excel File**: The user clicks another "Browse" button to select the main Excel workbook where their transactions should be stored.
4.  **Run Import**: The user clicks the "Import Transactions" button to start the process.
5.  **Feedback**: The application displays status messages indicating the progress and outcome of the import, including how many new transactions were successfully added.

## Command-Line Interface (CLI)

In addition to the GUI, the import feature can be run directly from the command line, making it suitable for scripting and automation.

### Usage
The script is run from the root directory of the project.

```bash
python run.py [bank] [csv_file] [excel_file]
```

### Arguments
- **`bank`** (required): The identifier for the financial institution. Must be one of the supported banks.
- **`csv_file`** (required): The full path to the source CSV file downloaded from the bank.
- **`excel_file`** (required): The full path to the destination Excel workbook.

### Example

```bash
python run.py capitalone "C:\\Users\\YourUser\\Downloads\\card_transactions.csv" "C:\\Users\\YourUser\\Documents\\finances.xlsx"
```

## Supported Institutions

The importer uses specific logic for each institution to correctly map the columns from their unique CSV format to the standardized format in the Excel file.

### Currently Supported:
- **Ally Bank**: Expects the standard transaction export format from Ally Bank's online portal.
- **Capital One**: Expects the standard transaction export format from Capital One's online portal.

### Standardized Transaction Columns:
The importer will map the source data to the following standard columns in the "Transactions" Excel table:
- `Date`
- `Description`
- `Amount`
- `Category`
- `Account`
- `Institution`
- `Notes`
- *(Other custom fields can exist but are not populated by the importer)*

## Processing Logic

1.  **File Selection**: The GUI captures the paths for the source CSV and the destination Excel file.
2.  **Importer Initialization**: Based on the selected institution, the application instantiates the corresponding importer module (e.g., `AllyImporter`).
3.  **CSV Parsing**: The selected importer reads the source CSV file and parses it into a list of transaction records. It uses institution-specific logic to handle unique date formats, column names, and credit/debit conventions.
4.  **Duplicate Detection**: Before importing, the system reads the existing transactions from the destination Excel file. It then compares each new transaction from the CSV against the existing ones. A transaction is considered a duplicate if its `Date`, `Description`, and `Amount` exactly match an existing record.
5.  **Data Appending**: Any transaction that is not identified as a duplicate is appended as a new row to the "Transactions" table in the Excel file.
6.  **Save Workbook**: After all new transactions have been appended, the Excel workbook is saved.

## Duplicate Detection System

The duplicate checker prevents the same transaction from being imported multiple times, ensuring data integrity.

### How It Works

The system creates a unique comparison key for each transaction using three fields:
- **Date**: Transaction date
- **Amount**: Transaction amount (including sign)
- **Full Description**: First 20 characters of the original bank description

**Comparison Key Format:**
```
{date}|{amount}|{first_20_chars_of_full_description}
```

### Why "Full Description"?

The system uses the original bank description (not user-editable "Description") because:
- Bank descriptions never change, providing consistent duplicate detection
- Users can modify transaction descriptions for categorization without affecting duplicate detection

### Detection Process

1. Load existing transactions from Excel file
2. Generate comparison keys for all existing transactions
3. For each new transaction:
   - Generate its comparison key
   - If key exists → Skip as duplicate
   - If key doesn't exist → Add to import list
4. Report how many duplicates were filtered out

### Example Scenarios

**Duplicate Detected:**
- Existing: `2024-01-15 | -45.67 | STARBUCKS COFFEE #1234`
- New: `2024-01-15 | -45.67 | STARBUCKS COFFEE #1234`
- **Result**: Filtered out

**Not a Duplicate:**
- Existing: `2024-01-15 | -45.67 | STARBUCKS COFFEE #1234`
- New: `2024-01-15 | -45.67 | STARBUCKS COFFEE #5678`
- **Result**: Imported (different store location)

## Error Handling
- **Invalid File Format**: If a selected CSV file does not match the expected format for the chosen institution, the import will fail, and an error message will be displayed to the user.
- **File Not Found**: Errors are shown if the source or destination files cannot be read or written to.
- **Logging**: Detailed logs are written to the `logs/` directory for debugging purposes, capturing each step of the import process and any errors that occur.

## Data Integrity
- **Duplicate Prevention**: The core data integrity feature is the robust duplicate check, which prevents the same transaction from being recorded multiple times.
- **Transactional Safety**: The system reads all data first, processes it in memory, and then writes all new transactions in a single batch operation before saving the file. 