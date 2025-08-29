# ADR-007: Logging Strategy

## Status

Accepted

## Context

The Cash Sync application processes financial data and performs critical operations that require comprehensive tracking for debugging, monitoring, and user support. We needed a logging strategy that:

- Provides detailed debugging information for developers
- Enables effective troubleshooting of user issues
- Maintains audit trails for financial data operations
- Supports both development and production environments
- Balances detail with performance and storage requirements
- Provides user-friendly error reporting

The challenge was to implement logging that serves multiple stakeholders (developers, users, system administrators) while maintaining performance and managing log volume.

## Decision

We implemented a centralized logging strategy with the following key components:

### 1. Centralized Logger Configuration

**Logger Module** (`logger.py`):
- Centralized configuration for all logging across the application
- Consistent formatting and output destinations
- Configurable log levels for different environments
- File and console output support

**Log Format**:
- Timestamp with millisecond precision
- Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Module and function name for easy tracing
- Descriptive message with context information

### 2. Log Level Strategy

**DEBUG**: Detailed information for debugging (development only)
- Function entry/exit points
- Variable values and state information
- Step-by-step operation details
- Stack traces and technical details
- Only enabled in development environments

**INFO**: User-centric operational information
- Start/completion of major operations in user-friendly language
- File operations (read, write, save) with user context
- Import/categorization progress for user understanding
- User actions and selections
- **All messages must be understandable by end users**

**WARNING**: User-centric non-critical issues
- Missing optional files or configurations (user-friendly explanation with suggested fix)
- Data format inconsistencies (what the user should know and how to correct)
- Performance degradation indicators (user impact and optimization suggestions)
- Deprecated feature usage (user guidance on alternatives)
- **All messages must suggest specific mitigation actions**

**ERROR**: User-centric problems that prevent normal operation
- File not found or permission errors (user-friendly explanation with file location guidance)
- Data validation failures (what the user can fix with specific steps)
- External library errors (user impact description with workaround suggestions)
- User input validation failures (clear guidance on correct format)
- **All messages must provide specific steps to resolve the issue**

**CRITICAL**: User-centric system-level failures
- Data corruption detected (user impact and specific recovery steps)
- Critical file system errors (user guidance on backup and recovery)
- Unrecoverable application errors (user action required with clear instructions)
- **All messages must provide immediate action steps for the user**

### 3. Logging Patterns

**Operation Logging**:
- Log the start and completion of major operations
- Include relevant parameters and context
- Track operation duration for performance monitoring
- Log success/failure status with appropriate detail

**Error Logging**:
- Log all exceptions with full context
- Include stack traces for debugging (DEBUG level only)
- Preserve original error messages
- Add application-specific context
- **User-facing error messages must be clear, actionable, and suggest specific mitigations**

**User Action Logging**:
- Log user selections and inputs
- Track file operations initiated by users
- Record configuration changes
- Maintain audit trail for data operations

**Performance Logging**:
- Log operation timing for performance analysis
- Track memory usage for large operations
- Monitor file I/O operations
- Identify bottlenecks and optimization opportunities

### 4. Log Output Strategy

**Development Environment**:
- Console output with detailed formatting
- File logging for persistent debugging
- DEBUG level enabled for comprehensive information
- Stack traces for all errors

**Production Environment**:
- File logging only (no console output)
- INFO level and above only
- Rotating log files to manage storage
- Error aggregation and reporting

**User Interface Integration**:
- Display user-friendly error messages
- Show progress information for long operations
- Provide actionable guidance for common issues
- Hide technical details from end users
- **All non-DEBUG log messages should be suitable for user display**

## Consequences

### Positive Consequences
- **Debugging**: Comprehensive logging enables effective troubleshooting
- **User Support**: Detailed logs help resolve user issues quickly
- **Audit Trail**: Complete record of data operations for compliance
- **Performance Monitoring**: Operation timing helps identify bottlenecks
- **Error Tracking**: Systematic error logging improves reliability
- **Development Efficiency**: Detailed logs accelerate development and testing

### Negative Consequences
- **Storage Overhead**: Log files consume disk space
- **Performance Impact**: Logging adds overhead to operations
- **Information Overload**: Too much logging can obscure important information
- **Privacy Concerns**: Logs may contain sensitive information
- **Maintenance**: Log rotation and cleanup require ongoing management

### Testing Implications
- **Log Verification**: Tests verify appropriate logging occurs
- **Error Logging**: Test error conditions ensure proper logging
- **Performance Testing**: Verify logging doesn't significantly impact performance
- **Log Level Testing**: Test different log levels in different environments
- **Coverage**: Logging code must meet our [official coverage requirements](../testing-standards/tools-and-automation/coverage_requirements.md)

## Compliance

### Testing Standards Compliance
- **Unit Tests**: Test logging behavior in all components
- **Integration Tests**: Verify logging across component boundaries
- **Performance Tests**: Ensure logging doesn't impact performance significantly
- **Error Tests**: Verify error logging captures all necessary information

### Code Standards Compliance
See [Architecture Standards](../architecture-standards.md) for comprehensive code standards including:
- **Logging Patterns**: Consistent logging patterns across all components
- **Error Handling**: Integration with error handling strategy
- **Documentation**: Logging behavior documented in component APIs

### Security Compliance
See [Architecture Standards](../architecture-standards.md) for comprehensive security standards including:
- **Data Privacy**: Avoid logging sensitive financial information
- **File Security**: Secure log file storage and access
- **Information Disclosure**: Prevent sensitive data in error messages

## Implementation Example

```python
import logging
from typing import Optional

# Centralized logger configuration
logger = logging.getLogger(__name__)

def import_transactions(self, csv_file: str, excel_file: str) -> Tuple[bool, str]:
    """
    Main import function with comprehensive logging.
    
    Args:
        csv_file (str): Path to the CSV file containing transaction data
        excel_file (str): Path to the Excel file where transactions will be added
    
    Returns:
        Tuple[bool, str]: Success status and descriptive message
    """
    logger.info("Starting transaction import: CSV=%s, Excel=%s", csv_file, excel_file)
    
    try:
        # Validate files first
        logger.debug("Validating input files")
        self.validate_files(csv_file, excel_file)
        logger.debug("File validation completed successfully")
        
        # Read and validate CSV
        logger.info("Reading CSV file: %s", csv_file)
        df = self.csv_handler.read_csv()
        logger.info("Found %d transactions in CSV", len(df))
        
        # Validate columns
        logger.debug("Validating CSV columns against expected format")
        self.csv_handler.validate_columns(self.get_expected_columns())
        logger.debug("Column validation completed successfully")
        
        # Transform and import transactions
        logger.info("Transforming transactions to standardized format")
        transactions = self.transform_transactions(df, self.excel_handler.existing_columns)
        logger.info("Transformed %d transactions", len(transactions))
        
        # Update Excel file
        logger.info("Updating Excel file: %s", excel_file)
        count = self.excel_handler.update_transactions(transactions)
        self.excel_handler.save()
        
        if count > 0:
            logger.info("Successfully imported %d new transactions!", count)
            return True, f"Successfully imported {count} new transactions!"
        else:
            logger.warning("No new transactions to import (all appear to be duplicates)")
            return True, "No new transactions to import (all appear to be duplicates)"
            
    except FileNotFoundError as e:
        logger.error("File not found during import. Please check the file path and ensure the file exists: %s", e)
        return False, f"File not found: {e}. Please check the file path and ensure the file exists."
    except ValueError as e:
        logger.error("Invalid file format detected. Please ensure the CSV file has the correct column structure: %s", e)
        return False, f"Invalid file format: {e}. Please check that your CSV file has the expected columns."
    except Exception as e:
        logger.error("An unexpected error occurred during import. Please check the file format and try again.")
        logger.debug("Technical error details: %s", e)
        logger.debug("Full traceback:\n%s", traceback.format_exc())
        return False, "An unexpected error occurred. Please check the file format and try again."
    finally:
        logger.info("Transaction import operation completed")
```

## References

- [Architecture Documentation](../architecture.md)
- [Testing Standards](../testing-standards/)
- [Error Handling Strategy](006-error-handling-strategy.md)
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
