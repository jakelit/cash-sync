# ADR-003: Excel Table-Based Data Storage

## Status

Accepted

## Context

The application needed a data storage solution that would:
- Be accessible to end users without technical expertise
- Preserve formatting and data validation when new data is added
- Support complex financial data structures
- Allow for easy data manipulation and analysis
- Provide a familiar interface for financial data management
- Support both reading and writing operations efficiently

The target users are individuals managing personal finances who are comfortable with Excel but may not have technical backgrounds. The solution needed to balance simplicity with functionality.

## Decision

We chose to use Excel's built-in Table feature as the primary data storage mechanism, specifically:

1. **Excel Tables**: Using Excel's native Table functionality for data storage
2. **Structured References**: Leveraging Excel's structured reference system
3. **Data Validation**: Utilizing Excel's built-in data validation features
4. **Format Preservation**: Maintaining formatting when new rows are added

### Key Implementation Details

#### Table Structure
- **Table Name**: "Transactions" (exact name required)
- **Required Columns**: Date, Description, Category, Amount, Account, Account #
- **Optional Columns**: Institution, Transaction Type, Balance
- **Data Types**: Properly formatted dates, numbers, and text

#### ExcelHandler Responsibilities
- **Table Detection**: Automatically locate the "Transactions" table
- **Structure Validation**: Verify required columns are present
- **Data Integrity**: Ensure data types and formats are correct
- **Format Preservation**: Maintain existing formatting when adding data

#### Error Handling
- **Clear Error Messages**: User-friendly instructions for table creation
- **Validation Feedback**: Specific guidance on missing requirements
- **Recovery Instructions**: Step-by-step fix instructions

## Consequences

### Positive Consequences
- **User Familiarity**: Excel is widely understood and used for financial data
- **Format Preservation**: Excel Tables automatically maintain formatting
- **Data Validation**: Built-in Excel validation features can be utilized
- **No Database Setup**: Users don't need to install or configure databases
- **Portability**: Excel files can be easily shared and backed up
- **Rich Formatting**: Excel provides extensive formatting and visualization options
- **Structured References**: Excel's structured reference system provides data integrity

### Negative Consequences
- **File Size Limitations**: Large datasets may impact performance
- **Concurrent Access**: No built-in support for multiple users
- **Data Integrity**: Limited transaction support compared to databases
- **Performance**: Excel operations can be slower than database operations for large datasets
- **Dependency**: Requires Microsoft Excel or compatible spreadsheet software

### Testing Implications
- **File System Testing**: Tests need to create and manage temporary Excel files
- **Table Structure Testing**: Validate table creation and structure requirements
- **Data Integrity Testing**: Ensure data is correctly written and read
- **Format Preservation Testing**: Verify formatting is maintained during operations
- **Error Handling Testing**: Test various error conditions and user guidance

## Compliance

### Testing Standards Compliance
- **Unit Tests**: ExcelHandler has comprehensive unit tests for all operations
- **Integration Tests**: End-to-end testing of Excel file operations
- **Property Tests**: Hypothesis-based tests for data integrity
- **Performance Tests**: Testing with various file sizes and data volumes
- **Error Scenario Tests**: Testing all error conditions and user guidance

### Code Standards Compliance
See [Architecture Standards](../architecture-standards.md) for comprehensive code standards including:
- **PEP 8 Compliance**: Style guidelines and formatting
- **Type Hints**: Comprehensive type annotations for Excel operations
- **Documentation**: Component and API documentation
- **Error Messages**: Clear, actionable error messages for users

### Security Compliance
- **File Validation**: Validate Excel file structure before processing
- **Path Security**: Prevent directory traversal attacks
- **Data Sanitization**: Clean and validate all data before writing to Excel
- **Permission Handling**: Proper handling of file permission errors

## Implementation Example

```python
class ExcelHandler:
    def load_workbook(self):
        """Load the Excel workbook and locate the Transactions table."""
        self.wb = load_workbook(self.excel_file)
        
        # Find the Transactions table across all worksheets
        for sheet_name in self.wb.sheetnames:
            ws = self.wb[sheet_name]
            if ws.tables:
                for table_name in ws.tables:
                    if table_name.lower() == 'transactions':
                        self.table = ws.tables[table_name]
                        self.ws = ws
                        break
```

## User Requirements

### Table Creation Instructions
1. Open Excel file
2. Select transaction data (including headers)
3. Go to Insert → Table (or press Ctrl+T)
4. Check "My table has headers"
5. Click OK
6. Right-click table → Table Design
7. Change table name to: "Transactions"
8. Save file

### Required Columns
- **Date**: Transaction date
- **Description**: Transaction description
- **Category**: Transaction category
- **Amount**: Transaction amount
- **Account**: Account name
- **Account #**: Account number

## References

- [Architecture Documentation](../architecture.md)
- [Testing Standards](../testing-standards/)
- [Excel Tables Documentation](https://support.microsoft.com/en-us/office/overview-of-excel-tables-7ab0bb7d-3a9e-4b56-a3c9-6c94334e492c)
- [openpyxl Documentation](https://openpyxl.readthedocs.io/)
