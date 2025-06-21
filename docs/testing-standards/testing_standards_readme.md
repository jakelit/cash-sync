# Testing Standards

This directory contains our standardized approach to testing Python code. These standards ensure consistency, quality, and maintainability across all projects.

## 📋 Quick Reference

### Creating Test Plans
Use the comprehensive template: **[test-plan-template.md](./test-plan-template.md)**

### Implementation Guidelines  
Follow our coding standards: **[test-implementation-guide.md](./test-implementation-guide.md)**

### Tools & Configuration
Setup and automation guides: **[tools-and-automation/](./tools-and-automation/)**

## 🎯 Testing Standards Overview

### Coverage Requirements
- **Minimum Line Coverage:** 90%
- **Minimum Branch Coverage:** 85%
- **Critical Components:** 95%+ coverage required

### Testing Framework Stack
- **Primary:** `pytest` with `pytest-cov`
- **Mocking:** `pytest-mock`
- **Property Testing:** `hypothesis`
- **Performance:** `pytest-benchmark` (when needed)

### Test Categories
- **Unit Tests:** Individual component testing (`@pytest.mark.unit`)
- **Integration Tests:** Component interaction testing (`@pytest.mark.integration`)
- **End-to-End Tests:** Full workflow testing (`@pytest.mark.e2e`)
- **Performance Tests:** Speed and memory testing (`@pytest.mark.performance`)

## 🤖 AI Agent Usage

When working with AI agents, reference these standards for consistent test generation:

### For Test Plan Creation:
```
Create a test plan for the [ClassName] class following our testing standards 
in docs/testing-standards/test-plan-template.md.
```

### For Test Implementation:
```
Implement tests for [ClassName] following our testing standards. 
Reference: docs/testing-standards/test-implementation-guide.md
```

### For Test Review:
```
Review this test implementation against our testing standards and 
suggest improvements based on docs/testing-standards/.
```

## 📚 Documentation Structure

```
testing-standards/
├── README.md                           # This file - overview and quick reference
├── test-plan-template.md              # Comprehensive test plan template
├── test-implementation-guide.md       # Code-specific guidelines and patterns
├── examples/
│   ├── test_plan_bank_account.md      # Complete test plan example
│   └── test_bank_account.py           # Example test implementation
└── tools-and-automation/
    ├── pytest-configuration.md        # pytest setup and configuration
    ├── ci-cd-integration.md           # GitHub Actions and CI/CD
    └── coverage-requirements.md       # Coverage standards and enforcement
```

## 🚀 Getting Started

### For New Projects
1. Copy `test-plan-template.md` for each major class
2. Follow `test-implementation-guide.md` for coding standards
3. Configure pytest using `tools-and-automation/pytest-configuration.md`
4. Set up CI/CD following `tools-and-automation/ci-cd-integration.md`

### For Existing Projects
1. Audit current tests against these standards
2. Create test plans for undertested components
3. Refactor tests to match implementation guidelines
4. Update CI/CD configuration

## 📊 Quality Gates

### Pre-Commit Requirements
- All new tests must follow the implementation guide
- Test files must have corresponding test plans (for major components)
- Coverage must not decrease

### CI/CD Requirements
- All tests must pass
- Coverage thresholds must be met
- No high-priority security or quality issues

### Code Review Requirements
- Test plans reviewed for completeness
- Test implementation follows standards
- Edge cases adequately covered

## 🔄 Continuous Improvement

### Monthly Reviews
- Review test failure patterns
- Update standards based on lessons learned
- Evaluate new testing tools and techniques

### Quarterly Updates
- Review coverage requirements
- Update tool recommendations
- Refresh example implementations

## 💡 Best Practices Summary

### Test Naming
```python
def test_method_name_condition_expected_result():
    """Clear description of what is being tested."""
```

### Test Structure (Arrange-Act-Assert)
```python
def test_deposit_positive_amount_increases_balance():
    # Arrange
    account = BankAccount(initial_balance=100)
    
    # Act
    account.deposit(50)
    
    # Assert
    assert account.balance == 150
```

### Fixture Usage
```python
@pytest.fixture
def sample_account():
    """Provides a standard account for testing."""
    return BankAccount(initial_balance=100)
```

### Parameterized Tests
```python
@pytest.mark.parametrize("amount,expected", [
    (50, 150),
    (0, 100),
    (100, 200),
])
def test_deposit_various_amounts(sample_account, amount, expected):
    sample_account.deposit(amount)
    assert sample_account.balance == expected
```

## 📞 Support and Questions

- **Documentation Issues:** Create an issue in this repository
- **Standards Questions:** Tag the testing team in discussions
- **Tool Problems:** Check `tools-and-automation/` documentation first

---

**Remember:** These standards are living documents. Contribute improvements through pull requests!