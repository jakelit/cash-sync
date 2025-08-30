# Venmo Importer Test Plan

**Version:** 1.0  
**Last Updated:** 2025-08-29  
**Author:** AI
**Reviewer:** Jacob

## Introduction

The Venmo Transaction Importer handles Venmo's unique CSV format with multi-line headers, ISO datetime formats, signed currency amounts, and username extraction from headers. This test plan focuses on Venmo-specific functionality while leveraging existing infrastructure components.

**Class Location:** `src/cash_sync/venmo_importer.py`  
**Test Location:** `tests/test_venmo_importer*.py`  

## Test Objectives

- [ ] Verify accurate parsing of Venmo's unique CSV format (multi-line headers, ISO datetime)
- [ ] Ensure proper username extraction from CSV headers (`(@username)` format)
- [ ] Validate signed currency amount parsing with proper sign preservation
- [ ] Test Venmo-specific column mapping and data transformation logic
- [ ] Ensure robust error handling for Venmo-specific edge cases
- [ ] Validate integration with existing import infrastructure (CSVHandler, ExcelHandler, DuplicateChecker)
- [ ] Meet performance requirements for large Venmo CSV files

## Test Environment

- **Python Version:** 3.9+
- **Primary Framework:** pytest
- **Additional Libraries:**
  - `pytest-cov` (coverage reporting)
  - `pytest-mock` (mocking utilities)
  - `hypothesis` (property-based testing)
  - `pandas` (data manipulation)
  - `openpyxl` (Excel file handling)
- **External Dependencies:** 
  - Venmo CSV files with various formats
  - Excel files with Transactions tables

## Test Scope

### In Scope
- Venmo-specific CSV format parsing (multi-line headers, blank columns)
- ISO datetime parsing (`2025-06-01T01:39:54` format)
- Username extraction from CSV headers (`(@username)` pattern)
- Signed currency amount parsing (`+ $25.00`, `- $150.00`)
- Venmo-specific column mapping and data transformation
- Integration with existing infrastructure components
- Venmo-specific error handling and edge cases
- Performance with large Venmo CSV files

### Out of Scope
- General CSV parsing logic (covered by CSVHandler tests)
- General Excel operations (covered by ExcelHandler tests)
- General duplicate detection (covered by DuplicateChecker tests)
- Venmo API integration (future feature)
- Business account support (future feature)
- Real-time transaction monitoring (future feature)

### Dependencies
- **Mocked:** File system operations, GUI interactions
- **Real:** CSV parsing logic, data transformation algorithms
- **Leveraged:** Existing CSVHandler, ExcelHandler, DuplicateChecker tests

## Test Categories

### Unit Tests
Individual method testing for Venmo-specific parsing and transformation logic

### Integration Tests
Component interaction testing with existing infrastructure

### Property-Based Tests
Comprehensive data validation using hypothesis for Venmo CSV formats

### Performance Tests
Import speed with large Venmo CSV files

### Security Tests
Input validation and data sanitization for Venmo-specific content

### Standard Markers
- **Unit Tests:** `@pytest.mark.unit` - Individual method testing
- **Integration Tests:** `@pytest.mark.integration` - Component interaction testing  
- **Property Tests:** `@pytest.mark.property` - Hypothesis-based testing
- **Performance Tests:** `@pytest.mark.performance` - Speed and memory testing
- **Security Tests:** `@pytest.mark.security` - Input validation and security

## Test File Organization

Tests are organized into module-specific files for maintainability and selective execution:

### File Structure
- `tests/test_venmo_importer_unit.py` - VenmoImporter unit tests (UT001-UT020)
- `tests/test_venmo_importer_integration.py` - Integration tests (IT001-IT010)
- `tests/test_venmo_importer_performance.py` - Performance tests (PERF001-PERF005)
- `tests/test_venmo_importer_property.py` - Property-based tests (PROP001-PROP005)
- `tests/test_venmo_importer_security.py` - Security tests (SEC001-SEC005)

### Test Counts by File
- VenmoImporter unit tests: 23 test cases (UT001-UT023)
- Integration tests: 10 test cases (IT001-IT010)
- Performance tests: 5 test cases (PERF001-PERF005)
- Property-based tests: 5 test cases (PROP001-PROP005)
- Security tests: 5 test cases (SEC001-SEC005)
- **Total: 48 test cases**

### Test Case Numbering Convention
- **UT###**: Unit Tests (UT001, UT002, UT003...)
- **IT###**: Integration Tests (IT001, IT002, IT003...)
- **PERF###**: Performance Tests (PERF001, PERF002, PERF003...)
- **PROP###**: Property-Based Tests (PROP001, PROP002, PROP003...)
- **SEC###**: Security Tests (SEC001, SEC002, SEC003...)

### Execution Commands
```bash
# Run all Venmo importer tests
pytest tests/test_venmo_importer*.py -v

# Run with coverage
pytest --cov=src/cash_sync --cov-report=html tests/test_venmo_importer*.py

# Run specific test categories
pytest -m "unit" tests/test_venmo_importer*.py
pytest -m "integration" tests/test_venmo_importer*.py
pytest -m "performance" tests/test_venmo_importer*.py
pytest -m "property" tests/test_venmo_importer*.py
pytest -m "security" tests/test_venmo_importer*.py

# Run specific test case ranges
pytest -k "UT001 or UT002" tests/test_venmo_importer_unit.py
pytest -k "IT001 or IT002" tests/test_venmo_importer_integration.py
pytest -k "PERF001" tests/test_venmo_importer_performance.py
```

## Test Scenarios

| Test ID | Category | Method/Feature | Description | Input/Setup | Expected Result | Priority | Notes |
|---------|----------|----------------|-------------|-------------|-----------------|----------|-------|
| UT001 | Unit | `__init__()` | Valid initialization | Valid parameters | Object created successfully | High | Happy path |
| UT002 | Unit | `__init__()` | Column mappings | Constructor call | Venmo-specific mappings set | High | Configuration |
| UT003 | Unit | `get_expected_columns()` | Required columns | Method call | Returns 7 required Venmo columns | High | Column validation |
| UT004 | Unit | `get_institution_name()` | Institution name | Method call | Returns "Venmo" | Medium | Institution-specific |
| UT005 | Unit | `get_account_name()` | Username extraction | Header "Account Statement - (@testuser)" | Extracts "@testuser" | High | Venmo-specific |
| UT006 | Unit | `get_account_name()` | Complex username | Header with special chars | Handles complex usernames | High | Edge case |
| UT007 | Unit | `get_account_name()` | Malformed header | Invalid header format | Returns appropriate error | High | Error handling |
| UT008 | Unit | `parse_transaction_date()` | ISO datetime | "2025-06-01T01:39:54" | Parses to date object | High | Venmo-specific |
| UT009 | Unit | `parse_transaction_date()` | Timezone formats | Various ISO formats | Handles timezone info | High | Format variations |
| UT010 | Unit | `parse_transaction_date()` | Invalid ISO format | Malformed datetime | Returns None, logs warning | High | Error handling |
| UT011 | Unit | `parse_transaction_amount()` | Positive amount | "+ $25.00" | Parses to 25.00 | High | Venmo-specific |
| UT012 | Unit | `parse_transaction_amount()` | Negative amount | "- $150.00" | Parses to -150.00 | High | Sign preservation |
| UT013 | Unit | `parse_transaction_amount()` | Zero amount | "$0.00" | Parses to 0.00 | Medium | Edge case |
| UT014 | Unit | `parse_transaction_amount()` | Invalid format | Non-currency string | Returns appropriate error | High | Error handling |
| UT015 | Unit | `transform_transactions()` | Venmo CSV row | Single valid row | Transformed transaction dict | High | Data transformation |
| UT016 | Unit | `transform_transactions()` | Multi-line header | CSV with 3-line header | Skips header rows correctly | High | Venmo-specific |
| UT017 | Unit | `transform_transactions()` | From/To mapping | Transaction with From/To | Correct description logic | High | Venmo-specific |
| UT018 | Unit | `transform_transactions()` | Special characters | Emojis in notes | Handles Unicode correctly | Medium | Edge case |
| UT019 | Unit | `transform_transactions()` | Empty fields | Missing From/To fields | Handles gracefully | Medium | Edge case |
| UT020 | Unit | `transform_transactions()` | Multi-line disclaimer | CSV with multi-line disclaimer in last row | Handles multi-line disclaimer correctly | Medium | Venmo-specific |
| UT021 | Unit | `read_csv_data()` | Balance row filtering | CSV with beginning/ending balance rows | Filters out balance rows correctly | High | Venmo-specific |
| UT022 | Unit | `read_csv_data()` | Multi-line CSV parsing | CSV with quoted multi-line values | Parses multi-line cells correctly | High | Venmo-specific |
| UT023 | Unit | `read_csv_data()` | Transaction ID validation | CSV with invalid/missing IDs | Only processes rows with valid IDs | High | Venmo-specific |
| IT001 | Integration | CSV file reading | Valid Venmo CSV | Standard Venmo export | Successfully reads format | High | Integration |
| IT002 | Integration | Data transformation | Complete pipeline | Sample Venmo CSV | All fields transformed | High | End-to-end |
| IT003 | Integration | Duplicate detection | Venmo transactions | Same file imported twice | Duplicates filtered | High | Integration |
| IT004 | Integration | Excel integration | Write to Excel | Venmo data to Excel | Data written correctly | High | Integration |
| IT005 | Integration | Error recovery | Invalid then valid | Failed import then retry | Second attempt succeeds | Medium | Error recovery |
| IT006 | Integration | Large file handling | 1000+ transactions | Large Venmo CSV | All processed correctly | Medium | Performance integration |
| IT007 | Integration | Mixed data types | Various formats | CSV with mixed data | All handled correctly | Medium | Data handling |
| IT008 | Integration | Column validation | Missing columns | CSV missing required | Clear error message | High | Error handling |
| IT009 | Integration | Date format variations | Different ISO formats | Various datetime formats | All parsed correctly | High | Format handling |
| IT010 | Integration | Amount format variations | Different currency formats | Various amount formats | All parsed correctly | High | Format handling |
| PERF001 | Performance | Large file import | 1000+ transactions | Large Venmo CSV | Completes in < 30 seconds | Medium | Performance |
| PERF002 | Performance | Memory usage | Large dataset | Large CSV processing | Memory < 100MB | Medium | Performance |
| PERF003 | Performance | Duplicate detection | Many duplicates | Large dataset with duplicates | Detection completes quickly | Medium | Performance |
| PERF004 | Performance | Excel file size | Large existing Excel | Excel with many transactions | No performance issues | Medium | Performance |
| PERF005 | Performance | Throughput | Processing rate | Standard Venmo CSV | > 100 transactions/second | Medium | Performance |
| PROP001 | Property-Based | CSV data validation | Hypothesis-generated | Random Venmo CSV data | All valid data processed | Medium | Property-based |
| PROP002 | Property-Based | Username formats | Random usernames | Various username patterns | All extracted correctly | Medium | Property-based |
| PROP003 | Property-Based | ISO datetime formats | Random datetime | Various ISO formats | All parsed correctly | Medium | Property-based |
| PROP004 | Property-Based | Currency amounts | Random amounts | Various currency formats | All parsed correctly | Medium | Property-based |
| PROP005 | Property-Based | Special characters | Random Unicode | Various special chars | All handled correctly | Medium | Property-based |
| SEC001 | Security | File path validation | Malicious paths | Path traversal attempts | Proper exception handling | High | Security |
| SEC002 | Security | CSV content validation | Malicious content | Injection attempts | Safe handling | High | Security |
| SEC003 | Security | Username extraction | Malicious headers | Header injection attempts | Safe extraction | High | Security |
| SEC004 | Security | Unicode normalization | Unicode attacks | Malicious Unicode content | Safe processing | High | Security |
| SEC005 | Security | Data sanitization | Various input types | Malicious input data | All sanitized properly | High | Security |

## Test Data Strategy

### Valid Input Examples
- **Venmo CSV Headers:**
  - "Account Statement - (@testuser)"
  - "Account Statement - (@user123_456)"
- **ISO DateTime Formats:**
  - "2025-06-01T01:39:54"
  - "2025-06-01T01:39:54Z"
  - "2025-06-01T01:39:54-05:00"
- **Currency Amounts:**
  - "+ $25.00" (credit)
  - "- $150.00" (debit)
  - "$0.00" (zero)
- **Transaction Types:**
  - Payment to friend
  - Payment from friend
  - Charge
  - Standard Transfer
- **Balance Rows (to be filtered out):**
  - Beginning balance row: `,,,,,,,,,,,,,,,,"$1,250.00",,,,,`
  - Ending balance row: `,,,,,,,,,,,,,,,,$1,407.50,$0.00,,$0.00,"Multi-line disclaimer text..."`
- **Multi-line Disclaimer Content:**
  - Quoted multi-line legal text within "Disclaimer" column
  - Contains newlines, contact information, and legal terms

### Invalid Input Examples
- **Malformed Headers:**
  - Missing username pattern
  - Invalid username characters
  - Malformed header structure
- **Invalid DateTime:**
  - Non-ISO format strings
  - Malformed ISO strings
  - Invalid timezone formats
- **Invalid Amounts:**
  - Non-currency strings
  - Malformed currency format
  - Invalid numeric values

### Test Data Generation
- **Static Data:** Predefined Venmo CSV files with various formats
- **Generated Data:** 
  - Hypothesis strategies for Venmo CSV generation
  - Property-based username and datetime generation
  - Boundary value testing for amounts and dates
- **Security Data:** Malicious input patterns, injection attempts
- **Performance Data:** Large datasets (1000+ transactions)

## Implementation Guidelines

### Code Quality Standards
- Follow PEP 8 for test code formatting
- Use descriptive test method names (e.g., `test_parse_iso_datetime_valid_format`)
- Include docstrings for complex test methods
- Use type hints in test code
- Maintain consistent assertion styles

### Test Organization
```python
# File: tests/test_venmo_importer_unit.py
class TestVenmoImporterUnit:
    """Unit tests for VenmoImporter class."""
    
    @pytest.fixture
    def venmo_importer(self):
        """Fixture providing a standard VenmoImporter instance."""
        return VenmoImporter()
    
    @pytest.fixture
    def sample_venmo_csv_header(self):
        """Fixture providing a standard Venmo CSV header."""
        return "Account Statement - (@testuser)"

# File: tests/test_venmo_importer_integration.py
class TestVenmoImporterIntegration:
    """Test integration between VenmoImporter and other components."""

# File: tests/test_venmo_importer_performance.py
class TestVenmoImporterPerformance:
    """Test performance with large Venmo datasets."""

# File: tests/test_venmo_importer_property.py
class TestVenmoImporterProperty:
    """Property-based tests using hypothesis."""

# File: tests/test_venmo_importer_security.py
class TestVenmoImporterSecurity:
    """Test security and input validation."""
```

### Mocking Strategy
- **File system operations:** Use `tmp_path` fixture
- **CSV reading:** Mock pandas read_csv for unit tests
- **Excel operations:** Mock openpyxl operations
- **Time-dependent operations:** Mock `datetime` functions

## Test Execution

### Basic Execution
```bash
# Run all Venmo importer tests
pytest tests/test_venmo_importer*.py -v

# Run with coverage
pytest --cov=src/cash_sync --cov-report=html tests/test_venmo_importer*.py

# Run specific test categories
pytest -m "unit" tests/test_venmo_importer*.py
pytest -m "integration" tests/test_venmo_importer*.py
pytest -m "performance" tests/test_venmo_importer*.py
pytest -m "property" tests/test_venmo_importer*.py
pytest -m "security" tests/test_venmo_importer*.py
```

### Coverage Requirements
- **Minimum Line Coverage:** 90%
- **Minimum Branch Coverage:** 85%
- **Coverage Exclusions:** 
  - Exception handling for unexpected errors
  - Debug logging statements
  - GUI event handlers

### Continuous Integration
- All tests must pass before merge
- Coverage thresholds must be met
- Performance benchmarks must not regress

## Success Criteria

- [ ] All test cases pass consistently
- [ ] Code coverage thresholds met (90% line, 85% branch)
- [ ] No critical or high-priority bugs identified
- [ ] Performance requirements satisfied (30s for 1000 transactions)
- [ ] Venmo-specific logic working correctly
- [ ] Integration with existing infrastructure working
- [ ] Error handling graceful and informative
- [ ] Property-based tests validate data consistency
- [ ] Security tests pass input validation
- [ ] Memory usage stays within acceptable limits

## Deliverables

- [ ] Complete test implementation:
  - [ ] `tests/test_venmo_importer_unit.py` (23 unit tests)
  - [ ] `tests/test_venmo_importer_integration.py` (10 integration tests)
  - [ ] `tests/test_venmo_importer_performance.py` (5 performance tests)
  - [ ] `tests/test_venmo_importer_property.py` (5 property tests)
  - [ ] `tests/test_venmo_importer_security.py` (5 security tests)
- [ ] HTML coverage report
- [ ] XML coverage report (for CI/CD)
- [ ] Test execution report
- [ ] Performance benchmarks
- [ ] Test data files (Venmo CSV templates)

## Assumptions and Constraints

### Assumptions
- Venmo CSV files follow documented format
- Excel files have a "Transactions" table
- System has sufficient memory for large datasets
- Existing infrastructure components work correctly

### Constraints
- CSV file size limitations
- Excel file size limitations
- Memory constraints for very large datasets
- Processing time requirements for real-time use

### Known Limitations
- Limited to personal Venmo accounts (not business)
- CSV format must match Venmo export structure
- Excel file must have proper table structure

## References

- **Class Implementation:** `src/cash_sync/venmo_importer.py`
- **Test Implementation:** `tests/test_venmo_importer*.py`
- **Import Transactions Test Plan:** `docs/test-plans/import-transactions-test-plan.md`
- **Testing Standards:** `docs/testing-standards/README.md`
- **Test Plan Template:** `docs/testing-standards/test-plan-template.md`
- **Venmo CSV Specification:** `docs/specs/venmo_importer.md`

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-08-29 | AI | Initial test plan creation |
