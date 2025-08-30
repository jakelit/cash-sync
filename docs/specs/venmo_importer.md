# Venmo Transaction Importer Specification

## Overview
The Venmo Transaction Importer allows users to import financial transaction data from Venmo CSV export files into a structured Excel table for tracking and analysis. This importer handles Venmo's unique CSV format, maps it to the standard format, checks for duplicates, and appends new transactions to the "Transactions" table in the specified Excel file.

## Venmo CSV Format Analysis

### Expected CSV Structure
Venmo exports transaction data in CSV format with a specific structure that includes header information and transaction data:

**File Structure:**
- **Line 1**: Account Statement header with username (e.g., "Account Statement - (@username)")
- **Line 2**: "Account Activity" section header
- **Line 3**: Column headers (first column is blank, followed by actual column headers)
- **Line 4**: Beginning Balance row (only contains value in "Beginning Balance" column)
- **Line 5+**: Transaction data rows (actual transaction records)
- **Last line**: Ending Balance row with legal disclaimer (contains values in "Ending Balance", "Statement Period Venmo Fees", and "Disclaimer" columns, where the Disclaimer column contains multi-line legal text)

**Important Format Notes:**
- The first column is empty/blank (no header)
- Column headers are on the 3rd line, not the 1st line
- Line 4 contains only the beginning balance (no transaction data)
- Transaction data starts from line 5
- The last line contains ending balance, fees, and legal disclaimer (no transaction data)
- The legal disclaimer is a multi-line value within the "Disclaimer" column of the last row
- Only rows with valid transaction IDs should be processed as transactions

**Transaction Columns (starting from 2nd column):**
- `ID` - Unique transaction identifier (e.g., "4345080794249066591")
- `Datetime` - Transaction date and time in ISO format (e.g., "2025-06-01T01:39:54")
- `Type` - Transaction type (e.g., "Payment")
- `Status` - Transaction status (e.g., "Complete")
- `Note` - User-provided note/description (e.g., "Dinner payment", "Coffee", "Rent")
- `From` - Sender's full name (e.g., "John Smith")
- `To` - Recipient's full name (e.g., "Jane Doe")
- `Amount (total)` - Transaction amount with sign and currency (e.g., "- $50.00", "+ $25.00")
- `Amount (tip)` - Tip amount (usually empty for personal payments)
- `Amount (tax)` - Tax amount (usually 0 for personal payments)
- `Amount (fee)` - Venmo fee amount (usually 0 for personal payments)
- `Tax Rate` - Tax rate percentage
- `Tax Exempt` - Tax exemption status
- `Funding Source` - Source of funds (e.g., "Venmo balance", empty for received payments)
- `Destination` - Account destination (e.g., "Venmo balance")
- `Beginning Balance` - Account balance at start of statement period
- `Ending Balance` - Account balance at end of statement period
- `Statement Period Venmo Fees` - Total fees for the statement period
- `Terminal Location` - Location information (usually empty)
- `Year to Date Venmo Fees` - YTD fee total
- `Disclaimer` - Legal disclaimer text

### Example CSV File
Below is an example of a typical Venmo statement CSV file showing the format and structure:

```csv
Account Statement - (@user123) ,,,,,,,,,,,,,,,,,,,,,
Account Activity,,,,,,,,,,,,,,,,,,,,,
,ID,Datetime,Type,Status,Note,From,To,Amount (total),Amount (tip),Amount (tax),Amount (fee),Tax Rate,Tax Exempt,Funding Source,Destination,Beginning Balance,Ending Balance,Statement Period Venmo Fees,Terminal Location,Year to Date Venmo Fees,Disclaimer
,,,,,,,,,,,,,,,,"$1,250.00",,,,,
,1234567890123456789,2024-01-15T14:30:22,Payment,Complete,Help with moving expenses,Alex Johnson,Sarah Wilson,- $75.00,,0,,0,,Venmo balance,,,,,Venmo,,,
,1234567890123456790,2024-01-18T19:45:33,Payment,Complete,Dinner 🍕 🍷,Alex Johnson,Mike Chen,- $45.50,,0,,0,,Venmo balance,,,,,Venmo,,,
,1234567890123456791,2024-01-20T12:15:10,Payment,Complete,Coffee ☕,Alex Johnson,Emily Davis,- $8.75,,0,,0,,Venmo balance,,,,,Venmo,,,
,1234567890123456792,2024-01-22T16:20:45,Payment,Complete,Concert tickets 🎵 🎫,David Lee,Alex Johnson,+ $120.00,,0,,0,,,Venmo balance,,,,Venmo,,,
,1234567890123456793,2024-01-25T09:30:18,Payment,Complete,Grocery split 🥕 🍎,Alex Johnson,Rachel Green,- $32.25,,0,,0,,Venmo balance,,,,,Venmo,,,
,1234567890123456794,2024-01-28T21:10:55,Payment,Complete,Weekend trip 🚗 🏨,Chris Brown,Alex Johnson,+ $200.00,,0,,0,,,Venmo balance,,,,Venmo,,,
,,,,,,,,,,,,,,,,,$1,407.50,$0.00,,$0.00,"In case of errors or questions about your
        electronic transfers:
        - Telephone us at 855-812-4430
        - Write the Venmo Error Resolution Department at
          222  W. Merchandise Plaza, Suite 800, Chicago, IL 60654; or
        - Write to us through the Contact Us page
          (https://help.venmo.com/hc/en-us/requests/new)
        Contact us as soon as you can if you think your statement or
        receipt is wrong or if you need more information about
        a transfer on the statement or receipt. We must hear from
        you no later than 60 days after we sent you the FIRST
        statement on which the error or problem appeared.
        1. Tell us your name and username or phone number.
        2. Describe the error or the transfer you are unsure about,
           and explain as clearly as you can why you believe it is
           an error or why you need more information.
        3. Tell us the dollar amount of the suspected error.
        We will investigate your complaint and will correct any
        error promptly. If we take more than 10 business days to do
        this, we will credit your account for the amount you think
        is in error, so that you will have the use of the money
        during the time it takes us to complete our investigation.
        In case of errors or questions about your transactions made
        with your Venmo Mastercard, please consult your
        Cardholder Agreement
        (https://venmo.com/legal/bancorp-cardholder-agreement).
        "
```

**Key Features of the Example:**
- Shows the header structure with username extraction (`@user123`)
- Line 4 contains only the beginning balance (`$1,250.00`)
- Demonstrates various transaction types and amounts (lines 5-9)
- Includes emojis in notes (🍕 🍷, ☕, 🎵 🎫, 🥕 🍎, 🚗 🏨)
- Shows both sent (negative amounts) and received (positive amounts) transactions
- Includes the blank first column structure
- Last line contains ending balance (`$1,407.50`), fees (`$0.00`), and multi-line legal disclaimer
- The legal disclaimer spans multiple lines within a single CSV cell (quoted value)

### Data Mapping Requirements
The importer must map Venmo-specific fields to the standardized Excel format:

| Venmo Field      | Standard Field     | Notes                                                                |
| ---------------- | ------------------ | -------------------------------------------------------------------- |
| `Datetime`       | `Date`             | Parse ISO datetime format (e.g., "2025-06-01T01:39:54") to date only |
| `From`/`To`      | `Description`      | Use From field for credits, To field for debits                      |
| `Amount (total)` | `Amount`           | Parse currency format (e.g., "- $50.00") to numeric, preserve sign   |
| `Note`           | `Notes`            | Include original note text                                           |
| `Type`           | `Notes`            | Include the original Venmo transaction type in the Notes field       |

## Implementation Requirements

### Class Structure
Create `VenmoImporter` class in `src/cash_sync/venmo_importer.py` that inherits from `BaseImporter`.

### Required Methods
The importer must implement the following methods:
- `get_expected_columns()` - Return the expected Venmo CSV columns as defined in the data mapping table above
- `get_institution_name()` - Return "Venmo"
- `get_account_name()` - Extract username from line 1 CSV header (e.g., "Account Statement - (@username)") and return as account name
- `read_csv_data()` - Override base method to handle Venmo's unconventional CSV format with multi-line headers and blank first column
- `parse_transaction_date()` - Override base method to handle ISO datetime format (e.g., "2025-06-01T01:39:54")
- `parse_transaction_amount()` - Parse currency format (e.g., "- $50.00", "+ $25.00") to numeric, preserve sign. Negative = money sent (debit), positive = money received (credit)

### Column Mapping Configuration
In the constructor of `VenmoImporter`, use the `set_column_mapping` method (inherited from `BaseImporter`) to map Venmo's CSV column names to the standardized internal column names. For example:

### CSV Reading Implementation
The `VenmoImporter` must override the `read_csv_data()` method to handle Venmo's unconventional CSV format:

**Key Implementation Requirements:**
1. **Header Processing**: Read the first line to extract username from "Account Statement - (@username)" format
2. **Data Section Identification**: Skip lines 1-3 (header and "Account Activity" section) to find the actual column headers
3. **Blank Column Handling**: Remove the blank first column that appears in all Venmo CSV files
4. **Balance Row Filtering**: Skip line 4 (beginning balance row) and last line (ending balance/fees/disclaimer row)
5. **Transaction Validation**: Ensure only rows with valid transaction IDs are included as transactions
6. **Multi-line Handling**: Handle the multi-line legal disclaimer within the last row's "Disclaimer" column

**Implementation Steps:**
1. Read the file line by line to extract account name from line 1
2. Find the "Account Activity" section to locate the start of column headers
3. Use `pandas.read_csv()` with `skiprows` parameter to start from line 3 (column headers)
4. Remove the blank first column using DataFrame slicing
5. Filter out balance rows (line 4 and last line) that don't contain transaction data
6. Filter out rows without valid transaction IDs (empty or non-numeric ID values)
7. Handle multi-line legal disclaimer within the last row's "Disclaimer" column
8. Return a clean DataFrame with only transaction data

**Example Implementation Structure:**
```python
def read_csv_data(self, csv_file: str) -> pd.DataFrame:
    # Read file line by line to extract account name from line 1
    # Find "Account Activity" section to locate column headers
    # Read CSV with skiprows=2 to start from line 3 (column headers)
    # Remove blank first column using DataFrame slicing
    # Filter out balance rows (line 4 and last line)
    # Filter out rows without valid transaction IDs
    # Handle multi-line legal disclaimer in last row's "Disclaimer" column
    # Return clean DataFrame with only transaction data
```

## Integration Requirements

### GUI Integration
Add Venmo to the bank selection dropdown in the importer GUI.

### CLI Integration
Add Venmo to the available banks in the CLI interface.

### Import Statement
Add import statement in the main package initialization.

## Error Handling

### CSV Format Validation
- Validate that required columns are present (starting from 2nd column due to blank first column)
- Handle missing or malformed ISO datetime values
- Validate amount fields are in currency format
- Handle empty or null values gracefully
- Skip header rows (lines 1-3) and footer disclaimer text
- Handle the blank first column in all data rows
- Validate that transaction data starts from line 5 (after beginning balance row)
- Filter out balance rows (line 4 and last line) that don't contain transaction data
- Validate that only rows with valid transaction IDs are processed as transactions
- Parse username from header line (e.g., "Account Statement - (@username)") for account identification
- Handle file reading errors in the `read_csv_data()` method
- Validate CSV structure before attempting to parse transaction data
- Handle multi-line values within CSV cells (legal disclaimer in "Disclaimer" column)

### Data Quality Checks
- Verify transaction dates are within reasonable range
- Validate amount values are not zero or extreme values
- Check for malformed description strings
- Handle special characters in notes and descriptions

### Error Messages
Provide clear error messages for:
- Missing required CSV columns
- Invalid ISO datetime formats
- Non-currency format amount values
- File access issues
- Header/footer parsing issues
- Invalid CSV structure (missing "Account Activity" section)
- Malformed header line (missing username extraction)
- File encoding issues during CSV reading
- Missing or invalid transaction data (no valid transaction rows found)
- Balance row parsing issues (beginning/ending balance rows not found)
- Multi-line CSV parsing issues (legal disclaimer handling)

## Testing
See the dedicated [Venmo Importer Test Plan](../test-plans/venmo-importer-test-plan.md) for comprehensive testing requirements, test cases, and validation criteria.

## Performance Considerations

### Large File Handling
- Efficient CSV parsing for large transaction files
- Memory management for bulk imports
- Progress reporting for long-running imports

### Duplicate Detection
- Optimize duplicate checking for Venmo's transaction patterns
- Handle Venmo's unique transaction identifiers
- Consider time-based duplicate detection

## Security Considerations

### Data Privacy
- Ensure sensitive information in notes is handled appropriately
- Validate file paths to prevent directory traversal
- Sanitize user input in descriptions and notes

### File Validation
- Verify CSV file integrity before processing
- Check file size limits
- Validate file encoding (UTF-8 expected)

## Documentation Updates

### User Documentation
Update `docs/import_transactions.md` to include:
- Venmo in supported institutions list
- Venmo-specific usage instructions
- Example CSV format for Venmo

### Code Documentation
- Comprehensive docstrings for all methods
- Type hints for all function parameters
- Inline comments for complex logic
- README updates for new importer

## Future Enhancements

### Potential Features
- Support for Venmo API integration (future)
- Enhanced transaction categorization for Venmo patterns
- Support for Venmo business accounts
- Integration with Venmo's transaction categories
- **Balance Tracking**: Extract and store beginning/ending balances from balance rows for account reconciliation
- **Fee Analysis**: Parse and track Venmo fees from the ending balance row

### Scalability
- Support for batch processing multiple Venmo files
- Incremental import capabilities
- Real-time transaction monitoring (future)

## Implementation Timeline

### Phase 1: Core Implementation
1. Create `VenmoImporter` class with basic functionality
2. Implement `read_csv_data()` method to handle Venmo's unconventional CSV format
3. Implement column mapping and data parsing
4. Add to GUI and CLI interfaces
5. Basic unit tests

### Phase 2: Testing and Refinement
1. Comprehensive test suite
2. Error handling improvements
3. Performance optimization
4. Documentation updates

### Phase 3: Integration and Deployment
1. Integration testing
2. User acceptance testing
3. Documentation finalization
4. Release preparation

## Success Criteria

### Functional Requirements
- Successfully import Venmo CSV files with 100% accuracy
- Proper duplicate detection for Venmo transactions
- Correct mapping of all Venmo fields to standard format
- Error handling for all edge cases

### Performance Requirements
- Import 1000+ transactions in under 30 seconds
- Memory usage under 100MB for large files
- No data loss during import process

### Quality Requirements
- 90%+ test coverage for Venmo importer
- All linting and type checking passes
- Comprehensive error handling and logging
- User-friendly error messages
