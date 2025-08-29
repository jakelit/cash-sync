# Coverage Requirements and Standards

This document defines our code coverage standards, measurement practices, and enforcement policies.

## 📊 Coverage Thresholds

### Minimum Requirements

| Component Type | Line Coverage | Branch Coverage | Notes |
|---------------|---------------|-----------------|-------|
| **Core Business Logic** | 95% | 90% | Critical path functionality |
| **API Endpoints** | 90% | 85% | Public interfaces |
| **Data Processing** | 90% | 85% | Data transformation logic |
| **Utility Functions** | 85% | 80% | Helper and support functions |
| **Integration Code** | 80% | 75% | External system interfaces |
| **Configuration** | 70% | 65% | Settings and configuration |

### Project-Level Targets

> **📋 COVERAGE REQUIREMENTS - SINGLE SOURCE OF TRUTH**
> 
> These are the official coverage requirements for the Cash Sync project. All other documentation should reference these values.
> 
> **🎯 DRY PRINCIPLE**: This document follows the "Don't Repeat Yourself" principle. Coverage requirements defined here should be referenced by other documentation rather than duplicated.

- **Overall Project:** 90% line coverage, 85% branch coverage
- **New Code:** 95% line coverage, 90% branch coverage
- **Critical Modules:** 95% line coverage, 95% branch coverage

### Coverage Constants

For programmatic access and documentation consistency:

```python
# Coverage thresholds - single source of truth
PROJECT_LINE_COVERAGE = 90
PROJECT_BRANCH_COVERAGE = 85
NEW_CODE_LINE_COVERAGE = 95
NEW_CODE_BRANCH_COVERAGE = 90
CRITICAL_MODULE_COVERAGE = 95
```

## 🎯 Coverage Configuration

### pyproject.toml Configuration

```toml
[tool.coverage.run]
source = ["src"]
branch = true
parallel = true
data_file = ".coverage"

# Include patterns
include = [
    "src/*",
    "src/**/*.py"
]

# Exclude patterns
omit = [
    "*/tests/*",
    "*/test_*",
    "**/conftest.py",
    "*/__init__.py",
    "*/migrations/*",
    "*/vendor/*",
    "*/.venv/*",
    "*/venv/*",
    "*/build/*",
    "*/dist/*",
    "setup.py",
    "*/settings/local.py",
    "*/settings/test.py",
]

# Coverage plugins
plugins = [
    "coverage_conditional_plugin"
]

[tool.coverage.report]
# Reporting options
show_missing = true
skip_covered = false
skip_empty = true
precision = 2
sort = "Cover"

# Fail under threshold
fail_under = 90

# Exclude lines from coverage
exclude_lines = [
    # Standard excludes
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if False:",
    "if __name__ == .__main__.:",
    
    # Type checking
    "if TYPE_CHECKING:",
    "if typing.TYPE_CHECKING:",
    
    # Abstract methods
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
    
    # Exception handling
    "except ImportError:",
    "except ModuleNotFoundError:",
    "except .*Error:",
    
    # Platform specific
    "if sys.platform",
    "if platform.system",
    
    # Defensive code
    "assert False",
    "raise AssertionError",
    "return NotImplemented",
    
    # Logging
    "logger\\.(debug|info|warning|error|critical)",
]

[tool.coverage.html]
directory = "htmlcov"
title = "Code Coverage Report"
show_contexts = true

[tool.coverage.xml]
output = "coverage.xml"

[tool.coverage.json]
output = "coverage.json"
show_contexts = true
```

### Advanced Coverage Settings

```toml
# Additional coverage configurations for specific scenarios

[tool.coverage.paths]
# Combine coverage from different environments
source = [
    "src/",
    "*/site-packages/myproject/",
    "*\\site-packages\\myproject\\",
]

[tool.coverage.run]
# Context switching for detailed analysis
dynamic_contexts = ["test_function"]

# Concurrency support
concurrency = ["thread", "multiprocessing"]

# Debug options
debug = ["config", "dataio"]  # Enable for troubleshooting

[tool.coverage.report]
# Precision and formatting
precision = 2
show_missing = true
skip_covered = false
skip_empty = true

# Sorting options
sort = "-Cover"  # Sort by coverage descending

# Context reporting
show_contexts = true
```

## 📋 Coverage Analysis Guidelines

### What to Measure

#### ✅ Include in Coverage
- **Business logic functions** - Core application functionality
- **API endpoint handlers** - Request/response processing
- **Data validation** - Input sanitization and validation
- **Error handling paths** - Exception handling and recovery
- **State management** - Object lifecycle and state transitions
- **Integration points** - External service interfaces
- **Security checks** - Authentication and authorization
- **Configuration loading** - Application setup and configuration

#### ❌ Exclude from Coverage
- **Third-party code** - External libraries and frameworks
- **Generated code** - Auto-generated files (migrations, protobuf)
- **Development tools** - Debug utilities and development helpers
- **Platform-specific code** - OS-specific implementations (when not testable)
- **Deprecated code** - Code marked for removal
- **Import statements** - Simple module imports
- **Type definitions** - Type hints and protocol definitions

### Coverage Quality Metrics

#### Line Coverage
```python
# Good: Covers all execution paths
def calculate_discount(price, customer_type):
    if customer_type == "premium":
        return price * 0.9  # Covered by test
    elif customer_type == "regular":
        return price * 0.95  # Covered by test
    else:
        raise ValueError("Invalid customer type")  # Covered by test
```

#### Branch Coverage
```python
# Example: Testing all branches
def process_payment(amount, payment_method):
    if amount <= 0:
        raise ValueError("Amount must be positive")  # Branch 1
    
    if payment_method == "credit":
        return process_credit_payment(amount)  # Branch 2
    elif payment_method == "debit":
        return process_debit_payment(amount)   # Branch 3
    else:
        raise ValueError("Invalid payment method")  # Branch 4

# Test should cover all 4 branches
```

## 🔍 Coverage Measurement Tools

### Command Line Usage

```bash
# Basic coverage run
coverage run -m pytest tests/

# With branch coverage
coverage run --branch -m pytest tests/

# Parallel coverage (for multiprocessing)
coverage run --parallel-mode -m pytest tests/

# Generate reports
coverage report                    # Terminal report
coverage html                      # HTML report
coverage xml                       # XML report for CI/CD
coverage json                      # JSON report for analysis

# Combine parallel runs
coverage combine

# Specific source focus
coverage run --source=src/mymodule -m pytest tests/

# Debug coverage issues
coverage debug sys                 # System information
coverage debug config              # Configuration details
coverage debug data                # Data file information
```

### Integration with pytest

```bash
# Using pytest-cov plugin
pytest --cov=src                   # Basic coverage
pytest --cov=src --cov-branch     # With branch coverage
pytest --cov=src --cov-report=html # HTML report
pytest --cov=src --cov-report=term-missing # Terminal with missing lines
pytest --cov=src --cov-fail-under=90 # Fail if under threshold

# Multiple report formats
pytest --cov=src --cov-report=html --cov-report=xml --cov-report=term

# Append to existing coverage
pytest --cov=src --cov-append

# Coverage for specific modules
pytest --cov=src.banking --cov=src.payments tests/
```

## 📊 Coverage Reporting and Analysis

### HTML Report Features

The HTML coverage report provides:

1. **Overview Page**: Overall statistics and module breakdown
2. **Module Pages**: Line-by-line coverage for each file
3. **Context Information**: Which tests cover each line
4. **Missing Coverage**: Highlighted uncovered lines
5. **Branch Information**: Conditional branch coverage details

### Reading Coverage Reports

#### Terminal Report
```
Name                      Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------
src/banking/__init__.py       2      0      0      0   100%
src/banking/account.py       45      2     12      1    94%   23, 67
src/banking/payment.py       38      5      8      2    84%   12, 34-38, 45
src/banking/utils.py         20      0      4      0   100%
---------------------------------------------------------------------
TOTAL                       105      7     24      3    91%
```

#### Understanding the Columns
- **Stmts**: Total executable statements
- **Miss**: Uncovered statements
- **Branch**: Total branches (if/else, loops, etc.)
- **BrPart**: Partially covered branches
- **Cover**: Coverage percentage
- **Missing**: Line numbers of uncovered code

### JSON Report Analysis

```python
# scripts/analyze_coverage.py
"""Analyze coverage JSON report for insights."""

import json
from pathlib import Path

def analyze_coverage_report():
    """Analyze coverage.json for detailed insights."""
    with open('coverage.json') as f:
        data = json.load(f)
    
    # Overall statistics
    total_coverage = data['totals']['percent_covered']
    print(f"Overall coverage: {total_coverage:.2f}%")
    
    # Module analysis
    files = data['files']
    low_coverage_files = []
    
    for filepath, stats in files.items():
        coverage = stats['summary']['percent_covered']
        if coverage < 80:
            low_coverage_files.append((filepath, coverage))
    
    # Report low coverage files
    if low_coverage_files:
        print("\nFiles with coverage below 80%:")
        for filepath, coverage in sorted(low_coverage_files, key=lambda x: x[1]):
            print(f"  {filepath}: {coverage:.2f}%")
    
    # Missing coverage analysis
    for filepath, stats in files.items():
        missing_lines = stats['missing_lines']
        if missing_lines:
            print(f"\n{filepath} missing coverage on lines: {missing_lines}")

if __name__ == "__main__":
    analyze_coverage_report()
```

## 🚨 Coverage Enforcement

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: coverage-check
        name: coverage-check
        entry: bash -c 'pytest --cov=src --cov-fail-under=90 --cov-report=term-missing'
        language: system
        types: [python]
        pass_filenames: false
```

### CI/CD Integration

```yaml
# GitHub Actions coverage enforcement
- name: Test with coverage
  run: |
    pytest --cov=src --cov-branch \
           --cov-report=xml \
           --cov-report=term-missing \
           --cov-fail-under=90

- name: Coverage comment
  uses: py-cov-action/python-coverage-comment-action@v3
  with:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    MINIMUM_GREEN: 95
    MINIMUM_ORANGE: 85
```

### Quality Gates

```python
# scripts/coverage_gate.py
"""Enforce coverage quality gates."""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def check_coverage_gate():
    """Check if coverage meets quality gate requirements."""
    coverage_xml = Path("coverage.xml")
    
    if not coverage_xml.exists():
        print("❌ Coverage report not found")
        return False
    
    tree = ET.parse(coverage_xml)
    root = tree.getroot()
    
    # Overall coverage
    line_rate = float(root.get('line-rate', 0)) * 100
    branch_rate = float(root.get('branch-rate', 0)) * 100
    
    print(f"Line Coverage: {line_rate:.2f}%")
    print(f"Branch Coverage: {branch_rate:.2f}%")
    
    # Check thresholds
    line_threshold = 90
    branch_threshold = 85
    
    if line_rate < line_threshold:
        print(f"❌ Line coverage {line_rate:.2f}% below threshold {line_threshold}%")
        return False
    
    if branch_rate < branch_threshold:
        print(f"❌ Branch coverage {branch_rate:.2f}% below threshold {branch_threshold}%")
        return False
    
    # Check per-file coverage
    for package in root.findall(".//package"):
        for class_elem in package.findall("classes/class"):
            filename = class_elem.get('filename')
            class_line_rate = float(class_elem.get('line-rate', 0)) * 100
            
            # Special requirements for critical files
            if 'banking' in filename and class_line_rate < 95:
                print(f"❌ Critical file {filename} coverage {class_line_rate:.2f}% below 95%")
                return False
    
    print("✅ All coverage gates passed")
    return True

if __name__ == "__main__":
    success = check_coverage_gate()
    sys.exit(0 if success else 1)
```

## 📈 Coverage Improvement Strategies

### Identifying Coverage Gaps

1. **Missing Line Analysis**
   ```bash
   # Find uncovered lines
   coverage report --show-missing
   
   # Focus on specific modules
   coverage report --include="src/banking/*" --show-missing
   ```

2. **Branch Coverage Analysis**
   ```bash
   # Detailed branch information
   coverage html
   # Open htmlcov/index.html and review branch coverage
   ```

3. **Context Analysis**
   ```bash
   # See which tests cover which lines
   coverage html --show-contexts
   ```

### Writing Tests for Coverage

#### Target Uncovered Lines
```python
# Before: Uncovered error handling
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")  # Uncovered
    return a / b

# Test to cover error case
def test_divide_by_zero_raises_error():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
```

#### Cover All Branches
```python
# Before: Missing branch coverage
def calculate_grade(score):
    if score >= 90:
        return "A"  # Covered
    elif score >= 80:
        return "B"  # Covered
    elif score >= 70:
        return "C"  # Not covered
    else:
        return "F"  # Not covered

# Add tests for missing branches
@pytest.mark.parametrize("score,expected", [
    (95, "A"),  # Existing
    (85, "B"),  # Existing
    (75, "C"),  # New test
    (65, "F"),  # New test
])
def test_calculate_grade(score, expected):
    assert calculate_grade(score) == expected
```

### Property-Based Testing for Coverage

```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=0, max_value=100))
def test_grade_calculation_comprehensive(score):
    """Property-based test to ensure all score ranges are covered."""
    grade = calculate_grade(score)
    
    if score >= 90:
        assert grade == "A"
    elif score >= 80:
        assert grade == "B"
    elif score >= 70:
        assert grade == "C"
    else:
        assert grade == "F"
```

## 🛡️ Coverage Best Practices

### Do's

1. **Focus on Meaningful Coverage**
   - Test business logic thoroughly
   - Cover error handling paths
   - Test edge cases and boundary conditions

2. **Use Coverage to Guide Testing**
   - Identify untested code paths
   - Ensure critical functionality is covered
   - Review coverage reports regularly

3. **Combine Coverage Types**
   - Use both line and branch coverage
   - Consider path coverage for complex logic
   - Monitor coverage trends over time

4. **Integrate with Development Workflow**
   - Run coverage checks in CI/CD
   - Set up pre-commit hooks
   - Include coverage in code reviews

### Don'ts

1. **Don't Chase 100% Coverage Blindly**
   - Some code doesn't need testing (simple getters/setters)
   - Platform-specific code may not be testable
   - Focus on quality over quantity

2. **Don't Write Tests Just for Coverage**
   - Tests should verify behavior, not just execute code
   - Meaningless tests provide false confidence
   - Focus on valuable test scenarios

3. **Don't Ignore Context**
   - High coverage doesn't guarantee good tests
   - Consider the quality of test assertions
   - Review what each test actually verifies

## 📋 Coverage Checklist

### Pre-Release Coverage Review

- [ ] Overall project coverage meets threshold (90%+)
- [ ] Critical modules have high coverage (95%+)
- [ ] New code has adequate coverage (95%+)
- [ ] Error handling paths are tested
- [ ] Edge cases are covered
- [ ] Integration points are tested
- [ ] No significant coverage regressions
- [ ] Coverage report reviewed for quality
- [ ] Missing coverage is justified or addressed

### Regular Coverage Maintenance

- [ ] Weekly coverage trend analysis
- [ ] Monthly coverage goal review
- [ ] Quarterly threshold adjustment
- [ ] Annual coverage strategy review
- [ ] Tool and plugin updates
- [ ] Team training on coverage practices