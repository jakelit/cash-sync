# Test Plan for Auto Categorize Feature

**Version:** 1.0  
**Last Updated:** 2025-06-21
**Author:** Jacob
**Reviewer:** Jacob

## Introduction

The Auto Categorize feature automatically assigns categories and additional fields to uncategorized transactions based on user-defined rules in a worksheet named "AutoCat". This test plan covers the `AutoCategorizer` class and its integration with the Excel workbook system.

**Class Location:** `src/excel_finance_tools/auto_categorizer.py`  
**Test Location:** `tests/test_auto_categorizer*.py` (Multiple files by test category)

## Test Objectives

- [ ] Verify functional correctness of all rule parsing and matching logic
- [ ] Ensure proper handling of all comparison types (contains, min, max, equals, etc.)
- [ ] Validate AutoCat worksheet structure and column validation
- [ ] Confirm integration with ExcelHandler for reading rules and updating transactions
- [ ] Test error handling for invalid rules, missing worksheets, and malformed data
- [ ] Validate performance with large datasets and complex rule sets
- [ ] Ensure data integrity and audit trail functionality
- [ ] Test edge cases and boundary conditions for all rule types

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
  - Excel files with AutoCat worksheets
  - Transaction data in Excel format

## Test Scope

### In Scope
- AutoCategorizer class initialization and configuration
- Rule parsing and validation logic
- All comparison types (contains, min, max, equals, starts with, ends with, regex, etc.)
- AutoCat worksheet structure validation
- Transaction matching and categorization logic
- Auto-fill field population
- Error handling and logging
- Performance with various dataset sizes
- Integration with ExcelHandler

### Out of Scope
- Excel file format validation (handled by ExcelHandler)
- Transaction data validation (handled by other components)
- GUI interactions (handled by GUI components)
- Third-party library internals (pandas, openpyxl)

### Dependencies
- **Mocked:** Excel file operations, logging
- **Real:** Rule parsing logic, comparison algorithms
- **Stubbed:** Complex Excel operations for unit tests

## Test Categories

### Unit Tests
Individual method testing for rule parsing, comparison logic, and validation

### Integration Tests
AutoCategorizer interaction with ExcelHandler and transaction data

### End-to-End Tests
Complete workflow testing from Excel file loading to transaction categorization

### Property-Based Tests
Comprehensive rule validation using hypothesis for various input combinations

### Performance Tests
Rule evaluation speed with large datasets and complex rule sets

### Data Integrity Tests
Verification that only uncategorized transactions are modified

### Security Tests
Input validation, file access permissions, and data sanitization

### Standard Markers
- **Unit Tests:** `@pytest.mark.unit` - Individual method testing
- **Integration Tests:** `@pytest.mark.integration` - Component interaction testing  
- **End-to-End Tests:** `@pytest.mark.e2e` - Full workflow testing
- **Performance Tests:** `@pytest.mark.performance` - Speed and memory testing
- **Property Tests:** `@pytest.mark.property` - Hypothesis-based testing
- **Security Tests:** `@pytest.mark.security` - Input validation and security

## Test File Organization

### Multi-File Structure
Due to the comprehensive nature of the Auto Categorize feature (64 test scenarios across 8 categories), tests are organized into multiple files for better maintainability and parallel execution:

```
tests/
├── test_auto_categorizer_unit.py          # TC001-TC042 (42 unit tests)
├── test_auto_categorizer_integration.py   # TC043-TC049 (7 integration tests)
├── test_auto_categorizer_e2e.py           # TC050-TC053 (4 E2E tests)
├── test_auto_categorizer_performance.py   # TC054-TC056, TC066 (4 performance tests)
├── test_auto_categorizer_property.py      # TC062-TC063 (2 property tests)
├── test_auto_categorizer_security.py      # TC064-TC065 (2 security tests)
└── test_auto_categorizer_data_integrity.py # TC057-TC061 (5 data integrity/error tests)
```

### File Organization Benefits
- **Maintainability:** Easier to locate and modify specific test types
- **Parallel Execution:** Different test categories can run simultaneously
- **Selective Testing:** Run only specific test types during development
- **Clear Separation:** Each file has a single responsibility
- **Team Collaboration:** Multiple developers can work on different test files
- **CI/CD Optimization:** Fast tests (unit) can run before slow tests (performance)

### Test File Execution
```bash
# Run specific test files
pytest tests/test_auto_categorizer_unit.py -v
pytest tests/test_auto_categorizer_e2e.py -v
pytest tests/test_auto_categorizer_performance.py -v

# Run all auto-categorizer tests
pytest tests/test_auto_categorizer*.py -v

# Run by category across all files
pytest -m "unit" tests/test_auto_categorizer*.py
pytest -m "e2e" tests/test_auto_categorizer*.py
pytest -m "performance" tests/test_auto_categorizer*.py
```

## Test Scenarios

| Test ID | Category       | Method/Feature              | Description                          | Input/Setup                                                      | Expected Result                               | Priority | Notes                      |
| ------- | -------------- | --------------------------- | ------------------------------------ | ---------------------------------------------------------------- | --------------------------------------------- | -------- | -------------------------- |
| TC001   | Unit           | `__init__()`                | Valid initialization                 | Valid Excel file path                                            | Object created successfully                   | High     | Happy path                 |
| TC002   | Unit           | `__init__()`                | Invalid file path                    | Non-existent file                                                | Raises FileNotFoundError                      | High     | Error handling             |
| TC003   | Unit           | `load_rules()`              | Valid AutoCat worksheet              | Worksheet with rules                                             | Rules loaded successfully                     | High     | Core functionality         |
| TC004   | Unit           | `load_rules()`              | Missing AutoCat worksheet            | No AutoCat sheet                                                 | Returns None, logs warning                    | High     | Graceful degradation       |
| TC005   | Unit           | `load_rules()`              | Missing Category column              | AutoCat without Category                                         | Raises ValueError                             | High     | Validation                 |
| TC006   | Unit           | `parse_rule_columns()`      | Contains rule                        | "Description Contains"                                           | Parsed correctly                              | High     | Rule parsing               |
| TC007   | Unit           | `parse_rule_columns()`      | Min/Max rules                        | "Amount Min", "Amount Max"                                       | Parsed correctly                              | High     | Numeric rules              |
| TC008   | Unit           | `parse_rule_columns()`      | Equals rule                          | "Account Equals"                                                 | Parsed correctly                              | High     | Exact matching             |
| TC009   | Unit           | `parse_rule_columns()`      | Starts with rule                     | "Description starts with"                                        | Parsed correctly                              | High     | Text prefix                |
| TC010   | Unit           | `parse_rule_columns()`      | Ends with rule                       | "Description ends with"                                          | Parsed correctly                              | High     | Text suffix                |
| TC011   | Unit           | `parse_rule_columns()`      | Regex rule                           | "Description regex"                                              | Parsed correctly                              | High     | Pattern matching           |
| TC012   | Unit           | `parse_rule_columns()`      | Not contains rule                    | "Description not contains"                                       | Parsed correctly                              | High     | Negative matching          |
| TC013   | Unit           | `parse_rule_columns()`      | Not equals rule                      | "Account not equals"                                             | Parsed correctly                              | High     | Negative exact             |
| TC014   | Unit           | `parse_rule_columns()`      | Between rule                         | "Amount between"                                                 | Parsed correctly                              | High     | Range matching             |
| TC015   | Unit           | `parse_rule_columns()`      | Invalid rule format                  | "Invalid Column"                                                 | Logs warning, ignored                         | Medium   | Error handling             |
| TC016   | Unit           | `evaluate_rule()`           | Contains match                       | "WALMART" in description                                         | Returns True                                  | High     | Text matching              |
| TC017   | Unit           | `evaluate_rule()`           | Contains no match                    | "WALMART" not in description                                     | Returns False                                 | High     | Text matching              |
| TC018   | Unit           | `evaluate_rule()`           | Min match                            | Amount >= 100                                                    | Returns True                                  | High     | Numeric comparison         |
| TC019   | Unit           | `evaluate_rule()`           | Min no match                         | Amount < 100                                                     | Returns False                                 | High     | Numeric comparison         |
| TC020   | Unit           | `evaluate_rule()`           | Max match                            | Amount <= 500                                                    | Returns True                                  | High     | Numeric comparison         |
| TC021   | Unit           | `evaluate_rule()`           | Max no match                         | Amount > 500                                                     | Returns False                                 | High     | Numeric comparison         |
| TC022   | Unit           | `evaluate_rule()`           | Equals match                         | Exact text match                                                 | Returns True                                  | High     | Exact matching             |
| TC023   | Unit           | `evaluate_rule()`           | Equals no match                      | Different text                                                   | Returns False                                 | High     | Exact matching             |
| TC024   | Unit           | `evaluate_rule()`           | Starts with match                    | "STAR" in "STARBUCKS"                                            | Returns True                                  | High     | Prefix matching            |
| TC025   | Unit           | `evaluate_rule()`           | Starts with no match                 | "COFFEE" not start of "STARBUCKS"                                | Returns False                                 | High     | Prefix matching            |
| TC026   | Unit           | `evaluate_rule()`           | Ends with match                      | "UCKS" in "STARBUCKS"                                            | Returns True                                  | High     | Suffix matching            |
| TC027   | Unit           | `evaluate_rule()`           | Ends with no match                   | "STAR" not end of "STARBUCKS"                                    | Returns False                                 | High     | Suffix matching            |
| TC028   | Unit           | `evaluate_rule()`           | Regex match                          | Pattern matches text                                             | Returns True                                  | High     | Pattern matching           |
| TC029   | Unit           | `evaluate_rule()`           | Regex no match                       | Pattern doesn't match                                            | Returns False                                 | High     | Pattern matching           |
| TC030   | Unit           | `evaluate_rule()`           | Not contains match                   | Text doesn't contain value                                       | Returns True                                  | High     | Negative matching          |
| TC031   | Unit           | `evaluate_rule()`           | Not contains no match                | Text contains value                                              | Returns False                                 | High     | Negative matching          |
| TC032   | Unit           | `evaluate_rule()`           | Not equals match                     | Values are different                                             | Returns True                                  | High     | Negative exact             |
| TC033   | Unit           | `evaluate_rule()`           | Not equals no match                  | Values are same                                                  | Returns False                                 | High     | Negative exact             |
| TC034   | Unit           | `evaluate_rule()`           | Between match                        | Value in range                                                   | Returns True                                  | High     | Range matching             |
| TC035   | Unit           | `evaluate_rule()`           | Between no match                     | Value outside range                                              | Returns False                                 | High     | Range matching             |
| TC036   | Unit           | `evaluate_rule()`           | Case insensitive                     | "walmart" vs "WALMART"                                           | Returns True                                  | High     | Case handling              |
| TC037   | Unit           | `evaluate_rule()`           | Case sensitive equals                | "Walmart" vs "walmart"                                           | Returns False                                 | High     | Case handling              |
| TC038   | Unit           | `evaluate_rule()`           | Empty rule value                     | Empty cell in rule                                               | Returns True (ignored)                        | Medium   | Empty handling             |
| TC039   | Unit           | `evaluate_rule()`           | Missing transaction column           | Column not in transaction                                        | Returns False                                 | Medium   | Missing data               |
| TC040   | Unit           | `evaluate_rule()`           | Invalid numeric data                 | Text in numeric field                                            | Returns False                                 | Medium   | Data validation            |
| TC041   | Unit           | `load_rules()`              | Rule with no valid conditions        | Rule row with all condition columns empty                        | Rule is not added to self.rules               | Medium   | Ensures only valid rules   |
| TC042   | Unit           | `_extract_rule_condition()` | Valid rule format with invalid field | "Description Contains" but "Description" not in existing_columns | Returns None, logs warning                    | Medium   | Field validation           |
| TC043   | Integration    | `run_auto_categorization()` | Single rule match                    | One matching rule                                                | Category assigned, auto-fill applied          | High     | End-to-end                 |
| TC044   | Integration    | `run_auto_categorization()` | Multiple rules, first match          | Multiple rules, first matches                                    | First rule applied, others ignored            | High     | Priority logic             |
| TC045   | Integration    | `run_auto_categorization()` | No rules match                       | No matching rules                                                | No changes made                               | High     | No-op scenario             |
| TC046   | Integration    | `run_auto_categorization()` | Empty category rule                  | Rule with empty Category                                         | Only auto-fill applied                        | High     | Auto-fill only             |
| TC047   | Integration    | `run_auto_categorization()` | All transactions categorized         | No uncategorized transactions                                    | No changes made                               | High     | Edge case                  |
| TC048   | Integration    | `run_auto_categorization()` | Complex rule combination             | Multiple conditions in one rule                                  | All conditions must match                     | High     | AND logic                  |
| TC049   | Integration    | `run_auto_categorization()` | Invalid auto-fill column             | Column not in transaction table                                  | Auto-fill ignored, logged                     | Medium   | Error handling             |
| TC050   | E2E            | Complete workflow           | Full categorization process          | Excel file with rules and transactions                           | All uncategorized transactions categorized    | High     | End-to-end workflow        |
| TC051   | E2E            | Workflow with errors        | Process with invalid rules           | Excel file with some invalid rules                               | Valid rules applied, invalid rules logged     | High     | Error handling in workflow |
| TC052   | E2E            | Workflow with no matches    | Process with no matching rules       | Excel file with rules that don't match                           | No changes made, process completes            | High     | No-op workflow             |
| TC053   | E2E            | Workflow with complex rules | Process with multiple rule types     | Excel file with various rule combinations                        | All rule types applied correctly              | High     | Complex workflow           |
| TC054   | Performance    | `run_auto_categorization()` | Large dataset                        | 10,000 transactions                                              | Completes within 30 seconds                   | Medium   | Performance                |
| TC055   | Performance    | `run_auto_categorization()` | Many rules                           | 100 rules                                                        | Completes within 60 seconds                   | Medium   | Performance                |
| TC056   | Performance    | `run_auto_categorization()` | Complex rules                        | Regex and multiple conditions                                    | Completes within 45 seconds                   | Medium   | Performance                |
| TC057   | Data Integrity | `run_auto_categorization()` | Categorized transactions             | Already categorized transactions                                 | No changes made                               | High     | Data integrity             |
| TC058   | Data Integrity | `run_auto_categorization()` | Audit trail                          | Changes made                                                     | Log entries created                           | Medium   | Audit functionality        |
| TC059   | Error Handling | `run_auto_categorization()` | Corrupted Excel file                 | Invalid Excel format                                             | Raises appropriate exception                  | High     | Error handling             |
| TC060   | Error Handling | `run_auto_categorization()` | Permission denied                    | Read-only file                                                   | Raises PermissionError                        | High     | Error handling             |
| TC061   | Error Handling | `run_auto_categorization()` | Invalid rule syntax                  | Malformed rule column                                            | Rule ignored, processing continues            | Medium   | Graceful degradation       |
| TC062   | Property       | `parse_rule_columns()`      | Rule parsing consistency             | Hypothesis-generated rule names                                  | Parsing always succeeds or fails consistently | Medium   | Property-based             |
| TC063   | Property       | `evaluate_rule()`           | Rule evaluation properties           | Random rule/transaction combinations                             | Evaluation is deterministic and consistent    | Medium   | Property-based             |
| TC064   | Security       | `__init__()`                | File access validation               | Invalid file paths, permissions                                  | Proper exception handling                     | High     | Security                   |
| TC065   | Security       | `load_rules()`              | Input sanitization                   | Malicious Excel content                                          | Safe handling of malformed data               | High     | Security                   |
| TC066   | Performance    | `run_auto_categorization()` | Memory usage                         | Large datasets                                                   | Memory usage stays within limits              | Medium   | Performance                |

## Test Data Strategy

### Valid Input Examples
- **Simple Rules:**
  - `Description Contains: "WALMART"`
  - `Amount Min: 100`
  - `Account Equals: "Checking"`
- **Complex Rules:**
  - `Description Contains: "STARBUCKS"` AND `Amount Max: 20`
  - `Description regex: ".*GAS.*"` AND `Amount Between: 30,100`
- **Auto-fill Examples:**
  - `Tags: "shopping"`
  - `Notes: "Grocery expense"`
  - `Full Description: "Walmart Grocery Purchase"`

### Invalid Input Examples
- **Malformed Rules:**
  - `Invalid Column Name`
  - `Description invalid_operator`
  - `Amount Min: "not_a_number"`
- **Missing Data:**
  - Empty Category column
  - Non-existent transaction columns
  - Invalid regex patterns

### Test Data Generation
- **Static Data:** Predefined Excel files with various rule configurations
- **Generated Data:** 
  - Hypothesis strategies for rule combinations
  - Property-based transaction data generation
  - Boundary value testing for amounts and text
- **Security Data:** Malicious input patterns, SQL injection attempts
- **Performance Data:** Large datasets (10k+ transactions, 100+ rules)

## Implementation Guidelines

### Code Quality Standards
- Follow PEP 8 for test code formatting
- Use descriptive test method names (e.g., `test_contains_rule_matches_case_insensitive`)
- Include docstrings for complex test methods
- Use type hints in test code
- Maintain consistent assertion styles

### Test Organization
```python
# File: tests/test_auto_categorizer_unit.py
class TestAutoCategorizerInit:
    """Test AutoCategorizer initialization and configuration."""
    
class TestAutoCategorizerRuleParsing:
    """Test rule parsing and validation logic."""
    
class TestAutoCategorizerRuleEvaluation:
    """Test rule evaluation and matching logic."""

# File: tests/test_auto_categorizer_integration.py
class TestAutoCategorizerIntegration:
    """Test integration with ExcelHandler and transaction data."""

# File: tests/test_auto_categorizer_e2e.py
class TestAutoCategorizerE2E:
    """End-to-end workflow testing."""

# File: tests/test_auto_categorizer_performance.py
class TestAutoCategorizerPerformance:
    """Test performance with large datasets."""

# File: tests/test_auto_categorizer_property.py
class TestAutoCategorizerProperty:
    """Property-based tests using hypothesis."""

# File: tests/test_auto_categorizer_security.py
class TestAutoCategorizerSecurity:
    """Test security and input validation."""

# File: tests/test_auto_categorizer_data_integrity.py
class TestAutoCategorizerDataIntegrity:
    """Test data integrity and error handling."""
```

### Mocking Strategy
- **Excel file operations:** Mock using `pytest-mock` for unit tests
- **File system operations:** Use `tmp_path` fixture for integration tests
- **Logging:** Mock logger calls to verify proper logging
- **Time-dependent operations:** Mock `datetime` functions if needed

### Shared Fixtures and Utilities
```python
# File: tests/conftest.py (shared across all test files)
import pytest
from unittest.mock import Mock, patch
import pandas as pd
from openpyxl import Workbook

@pytest.fixture
def sample_excel_file(tmp_path):
    """Create a test Excel file with AutoCat worksheet."""
    file_path = tmp_path / "test_auto_categorize.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "AutoCat"
    
    # Add sample rules
    ws.append(["Category", "Description Contains", "Amount Min", "Amount Max"])
    ws.append(["Groceries", "WALMART", "", "500"])
    ws.append(["Gas", "SHELL", "", ""])
    ws.append(["Coffee", "STARBUCKS", "", "20"])
    
    wb.save(file_path)
    return str(file_path)

@pytest.fixture
def sample_transactions():
    """Create sample transaction data for testing."""
    return pd.DataFrame({
        "Description": ["WALMART GROCERY", "SHELL GAS STATION", "STARBUCKS COFFEE"],
        "Amount": [150.00, 45.50, 5.75],
        "Category": ["", "", ""],
        "Account": ["Checking", "Checking", "Checking"]
    })

@pytest.fixture
def mock_excel_handler():
    """Mock ExcelHandler for unit tests."""
    with patch('src.excel_finance_tools.auto_categorizer.ExcelHandler') as mock:
        mock.return_value.read_worksheet.return_value = pd.DataFrame()
        mock.return_value.find_transaction_table.return_value = ("Transactions", 1, 1)
        yield mock.return_value
```

## Test Execution

### Basic Execution
```bash
# Run all tests for AutoCategorizer
pytest tests/test_auto_categorizer*.py -v

# Run with coverage
pytest --cov=src/excel_finance_tools/auto_categorizer --cov-report=html tests/test_auto_categorizer*.py

# Run specific test categories
pytest -m "unit" tests/test_auto_categorizer*.py
pytest -m "integration" tests/test_auto_categorizer*.py
pytest -m "e2e" tests/test_auto_categorizer*.py
pytest -m "performance" tests/test_auto_categorizer*.py
pytest -m "property" tests/test_auto_categorizer*.py
pytest -m "security" tests/test_auto_categorizer*.py

# Run all tests except slow ones
pytest -m "not slow" tests/test_auto_categorizer*.py
```

### Coverage Requirements
- **Minimum Line Coverage:** 95%
- **Minimum Branch Coverage:** 90%
- **Coverage Exclusions:** 
  - Exception handling for unexpected errors
  - Debug logging statements

### Continuous Integration
- All tests must pass before merge
- Coverage thresholds must be met
- Performance benchmarks must not regress

## Success Criteria

- [ ] All test cases pass consistently
- [ ] Code coverage thresholds met (95% line, 90% branch)
- [ ] No critical or high-priority bugs identified
- [ ] Performance requirements satisfied (30s for 10k transactions)
- [ ] All comparison types working correctly
- [ ] Integration with ExcelHandler working correctly
- [ ] Error handling graceful and informative
- [ ] Property-based tests validate rule consistency
- [ ] Security tests pass input validation
- [ ] Memory usage stays within acceptable limits
- [ ] End-to-end workflows complete successfully

## Deliverables

- [ ] Complete test implementation:
  - [ ] `tests/test_auto_categorizer_unit.py` (42 unit tests)
  - [ ] `tests/test_auto_categorizer_integration.py` (7 integration tests)
  - [ ] `tests/test_auto_categorizer_e2e.py` (4 E2E tests)
  - [ ] `tests/test_auto_categorizer_performance.py` (4 performance tests)
  - [ ] `tests/test_auto_categorizer_property.py` (2 property tests)
  - [ ] `tests/test_auto_categorizer_security.py` (2 security tests)
  - [ ] `tests/test_auto_categorizer_data_integrity.py` (5 data integrity tests)
  - [ ] `tests/conftest.py` (shared fixtures and utilities)
- [ ] HTML coverage report
- [ ] XML coverage report (for CI/CD)
- [ ] Test execution report
- [ ] Performance benchmarks
- [ ] Test data files (Excel templates)

## Assumptions and Constraints

### Assumptions
- Excel files are in valid .xlsx format
- AutoCat worksheet follows the specified structure
- Transaction data is in the expected format
- System has sufficient memory for large datasets

### Constraints
- Excel file size limitations
- Memory constraints for very large datasets
- Processing time requirements for real-time use

### Known Limitations
- Regex performance with complex patterns
- Memory usage with very large rule sets
- Excel file locking during processing

## References

- **Class Implementation:** `src/excel_finance_tools/auto_categorizer.py`
- **Test Implementation:** `tests/test_auto_categorizer*.py`
- **Feature Specification:** `docs/auto_categorize.md`
- **ExcelHandler Integration:** `src/excel_finance_tools/excel_handler.py`
- **Testing Standards:** `docs/testing-standards/README.md`

## Revision History

| Version | Date       | Author           | Changes                    |
| ------- | ---------- | ---------------- | -------------------------- |
| 1.0     | 2024-12-19 | Development Team | Initial test plan creation |