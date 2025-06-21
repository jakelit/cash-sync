# Test Implementation Guide

This guide provides concrete patterns and examples for implementing high-quality Python tests following our testing standards.

## 🏗️ Test File Structure

### Standard Test File Template

```python
"""
Test module for [ClassName] class.

This module contains comprehensive tests for the [ClassName] class,
covering all public methods, error conditions, and edge cases.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st

from src.module_name.class_name import ClassName
from src.module_name.exceptions import CustomException  # if applicable


class TestClassNameInit:
    """Test class initialization and configuration."""
    
    def test_init_with_valid_parameters(self):
        """Test successful initialization with valid parameters."""
        # Implementation here
        pass
    
    def test_init_with_invalid_parameters(self):
        """Test initialization fails with invalid parameters."""
        # Implementation here
        pass


class TestClassNameCore:
    """Test core functionality of ClassName."""
    
    @pytest.fixture
    def sample_instance(self):
        """Provide a standard instance for testing."""
        return ClassName(valid_parameters)
    
    def test_method_name_happy_path(self, sample_instance):
        """Test method with valid input produces expected output."""
        # Implementation here
        pass
    
    @pytest.mark.parametrize("input_value,expected", [
        (value1, expected1),
        (value2, expected2),
    ])
    def test_method_name_various_inputs(self, sample_instance, input_value, expected):
        """Test method with various valid inputs."""
        # Implementation here
        pass


class TestClassNameEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_method_name_with_boundary_values(self):
        """Test method behavior at boundary conditions."""
        # Implementation here
        pass
    
    def test_method_name_raises_exception_on_invalid_input(self):
        """Test method raises appropriate exception for invalid input."""
        # Implementation here
        pass


class TestClassNameIntegration:
    """Test integration with external dependencies."""
    
    @pytest.fixture
    def mock_dependency(self):
        """Mock external dependency."""
        return Mock()
    
    def test_integration_with_dependency(self, mock_dependency):
        """Test class interacts correctly with external dependency."""
        # Implementation here
        pass
```

## 🎯 Test Method Patterns

### 1. Arrange-Act-Assert Pattern

```python
def test_deposit_positive_amount_updates_balance():
    """Test that depositing a positive amount increases the balance."""
    # Arrange
    initial_balance = 100
    deposit_amount = 50
    account = BankAccount(initial_balance)
    
    # Act
    result = account.deposit(deposit_amount)
    
    # Assert
    assert account.balance == initial_balance + deposit_amount
    assert result is True  # if method returns success indicator
```

### 2. Exception Testing

```python
def test_withdraw_insufficient_funds_raises_exception():
    """Test that withdrawing more than balance raises InsufficientFundsError."""
    # Arrange
    account = BankAccount(balance=50)
    
    # Act & Assert
    with pytest.raises(InsufficientFundsError) as exc_info:
        account.withdraw(100)
    
    assert "Insufficient funds" in str(exc_info.value)
    assert account.balance == 50  # Balance unchanged
```

### 3. Parametrized Testing

```python
@pytest.mark.parametrize("initial_balance,deposit_amount,expected_balance", [
    (0, 100, 100),
    (50, 25, 75),
    (100, 0, 100),  # Edge case: zero deposit
    (999999, 1, 1000000),  # Large numbers
])
def test_deposit_various_amounts(initial_balance, deposit_amount, expected_balance):
    """Test deposit method with various amount combinations."""
    account = BankAccount(initial_balance)
    account.deposit(deposit_amount)
    assert account.balance == expected_balance
```

### 4. Property-Based Testing

```python
from hypothesis import given, strategies as st

@given(
    initial_balance=st.integers(min_value=0, max_value=1000000),
    deposit_amount=st.integers(min_value=0, max_value=1000000)
)
def test_deposit_always_increases_or_maintains_balance(initial_balance, deposit_amount):
    """Test that deposit never decreases balance (property-based test)."""
    account = BankAccount(initial_balance)
    original_balance = account.balance
    
    account.deposit(deposit_amount)
    
    assert account.balance >= original_balance
    assert account.balance == original_balance + deposit_amount
```

## 🔧 Fixture Patterns

### 1. Simple Fixtures

```python
@pytest.fixture
def empty_account():
    """Provide an empty bank account for testing."""
    return BankAccount(balance=0)

@pytest.fixture
def funded_account():
    """Provide a bank account with initial funds."""
    return BankAccount(balance=1000)
```

### 2. Parametrized Fixtures

```python
@pytest.fixture(params=[0, 100, 1000])
def account_with_various_balances(request):
    """Provide accounts with different starting balances."""
    return BankAccount(balance=request.param)

def test_account_balance_property(account_with_various_balances):
    """Test that balance property returns correct value for various balances."""
    account = account_with_various_balances
    assert isinstance(account.balance, (int, float))
    assert account.balance >= 0
```

### 3. Factory Fixtures

```python
@pytest.fixture
def account_factory():
    """Factory for creating bank accounts with custom parameters."""
    created_accounts = []
    
    def _create_account(balance=0, account_type="checking", **kwargs):
        account = BankAccount(balance=balance, account_type=account_type, **kwargs)
        created_accounts.append(account)
        return account
    
    yield _create_account
    
    # Cleanup
    for account in created_accounts:
        account.close()  # if cleanup is needed
```

### 4. Mock Fixtures

```python
@pytest.fixture
def mock_database():
    """Mock database connection for testing."""
    with patch('src.banking.database.DatabaseConnection') as mock_db:
        mock_db.return_value.save.return_value = True
        mock_db.return_value.load.return_value = {"balance": 100}
        yield mock_db.return_value

@pytest.fixture
def mock_external_api():
    """Mock external API service."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}
        yield mock_post
```

## 🎭 Mocking Strategies

### 1. Method Mocking

```python
def test_transfer_calls_external_validation(mock_external_api):
    """Test that transfer method calls external validation service."""
    account = BankAccount(balance=1000)
    
    account.transfer(500, "123456789")
    
    mock_external_api.assert_called_once()
    call_args = mock_external_api.call_args
    assert call_args[1]['account_number'] == "123456789"
    assert call_args[1]['amount'] == 500
```

### 2. Context Manager Mocking

```python
def test_file_operations_with_context_manager():
    """Test file operations using context manager mocking."""
    mock_file = Mock()
    
    with patch('builtins.open', return_value=mock_file):
        account = BankAccount.load_from_file("test.json")
        
        mock_file.__enter__.assert_called_once()
        mock_file.__exit__.assert_called_once()
```

### 3. Time-Dependent Mocking

```python
from datetime import datetime
from unittest.mock import patch

def test_transaction_timestamp():
    """Test that transactions are timestamped correctly."""
    fixed_time = datetime(2024, 1, 15, 10, 30, 0)
    
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        
        account = BankAccount(balance=100)
        account.deposit(50)
        
        transaction = account.get_last_transaction()
        assert transaction.timestamp == fixed_time
```

## 📊 Assertion Patterns

### 1. Value Assertions

```python
# Basic equality
assert account.balance == 150

# Approximate equality for floats
assert account.interest_rate == pytest.approx(0.025, rel=1e-3)

# Membership testing
assert "deposit" in account.transaction_types
assert account.status in ["active", "inactive", "frozen"]
```

### 2. Collection Assertions

```python
# List/sequence assertions
assert len(account.transactions) == 3
assert account.transactions[0].amount == 100

# Set operations
expected_transaction_types = {"deposit", "withdrawal", "transfer"}
assert set(account.get_transaction_types()) == expected_transaction_types

# Dictionary assertions
account_data = account.to_dict()
assert account_data["balance"] == 150
assert "created_at" in account_data
```

### 3. Type and Attribute Assertions

```python
# Type checking
assert isinstance(account.balance, (int, float))
assert isinstance(account.transactions, list)

# Attribute existence
assert hasattr(account, 'balance')
assert hasattr(account, 'deposit')

# Callable checking
assert callable(account.deposit)
```

### 4. Exception Assertions

```python
# Exception type and message
with pytest.raises(ValueError) as exc_info:
    BankAccount(balance=-100)

assert "Balance cannot be negative" in str(exc_info.value)
assert exc_info.value.args[0] == "Balance cannot be negative"

# Multiple possible exceptions
with pytest.raises((ValueError, TypeError)):
    BankAccount(balance="invalid")
```

## 🏷️ Test Markers and Organization

### 1. Standard Markers

```python
import pytest

@pytest.mark.unit
def test_basic_functionality():
    """Unit test for basic functionality."""
    pass

@pytest.mark.integration
def test_database_integration():
    """Integration test with database."""
    pass

@pytest.mark.slow
def test_performance_benchmark():
    """Performance test that takes significant time."""
    pass

@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    """Test for future functionality."""
    pass

@pytest.mark.skipif(sys.version_info < (3, 9), reason="Requires Python 3.9+")
def test_python39_feature():
    """Test that requires Python 3.9 or later."""
    pass
```

### 2. Custom Markers

```python
# In pytest.ini or pyproject.toml
# markers =
#     database: marks tests as requiring database
#     external_api: marks tests as requiring external 