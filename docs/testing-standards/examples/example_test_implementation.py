"""
Test module for BankAccount class.

This module contains comprehensive tests for the BankAccount class,
covering all public methods, error conditions, and edge cases.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st
from datetime import datetime, timezone

from src.banking.bank_account import BankAccount
from src.banking.exceptions import (
    InsufficientFundsError,
    AccountFrozenError,
    AccountClosedError,
    AccountNotEmptyError,
)


class TestBankAccountInit:
    """Test class initialization and configuration."""
    
    def test_init_with_valid_parameters(self):
        """Test successful initialization with valid parameters."""
        account = BankAccount(balance=1000, account_type="checking")
        
        assert account.balance == 1000
        assert account.account_type == "checking"
        assert account.status == "active"
        assert len(account.transactions) == 0
    
    def test_init_with_zero_balance(self):
        """Test initialization with zero balance."""
        account = BankAccount(balance=0, account_type="savings")
        
        assert account.balance == 0
        assert account.account_type == "savings"
    
    def test_init_with_negative_balance_raises_error(self):
        """Test initialization fails with negative balance."""
        with pytest.raises(ValueError) as exc_info:
            BankAccount(balance=-100, account_type="checking")
        
        assert "Balance cannot be negative" in str(exc_info.value)
    
    def test_init_with_invalid_account_type_raises_error(self):
        """Test initialization fails with invalid account type."""
        with pytest.raises(ValueError) as exc_info:
            BankAccount(balance=1000, account_type="invalid")
        
        assert "Invalid account type" in str(exc_info.value)
    
    @pytest.mark.parametrize("account_type", ["checking", "savings", "business"])
    def test_init_with_valid_account_types(self, account_type):
        """Test initialization succeeds with all valid account types."""
        account = BankAccount(balance=1000, account_type=account_type)
        assert account.account_type == account_type


class TestBankAccountDeposits:
    """Test deposit operations and validation."""
    
    @pytest.fixture
    def account(self):
        """Provide a standard account for testing."""
        return BankAccount(balance=1000, account_type="checking")
    
    def test_deposit_positive_amount_increases_balance(self, account):
        """Test that depositing a positive amount increases the balance."""
        initial_balance = account.balance
        deposit_amount = 500
        
        result = account.deposit(deposit_amount)
        
        assert result is True
        assert account.balance == initial_balance + deposit_amount
        assert len(account.transactions) == 1
        assert account.transactions[0].type == "deposit"
        assert account.transactions[0].amount == deposit_amount
    
    def test_deposit_zero_amount_no_change(self, account):
        """Test that depositing zero amount doesn't change balance."""
        initial_balance = account.balance
        initial_transaction_count = len(account.transactions)
        
        result = account.deposit(0)
        
        assert result is False
        assert account.balance == initial_balance
        assert len(account.transactions) == initial_transaction_count
    
    def test_deposit_negative_amount_raises_error(self, account):
        """Test that depositing negative amount raises ValueError."""
        initial_balance = account.balance
        
        with pytest.raises(ValueError) as exc_info:
            account.deposit(-100)
        
        assert "Deposit amount must be positive" in str(exc_info.value)
        assert account.balance == initial_balance
    
    @pytest.mark.parametrize("amount,expected_balance", [
        (50, 1050),
        (0.01, 1000.01),
        (999999.99, 1000999.99),
    ])
    def test_deposit_various_amounts(self, account, amount, expected_balance):
        """Test deposit method with various valid amounts."""
        account.deposit(amount)
        assert account.balance == expected_balance
    
    def test_deposit_very_large_amount(self, account):
        """Test deposit handles very large amounts correctly."""
        large_amount = Decimal('1000000000.00')  # 1 billion
        
        account.deposit(large_amount)
        
        assert account.balance == 1000 + large_amount
    
    @patch('datetime.datetime')
    def test_deposit_records_timestamp(self, mock_datetime, account):
        """Test that deposit operations are timestamped correctly."""
        fixed_time = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_time
        
        account.deposit(100)
        
        transaction = account.transactions[0]
        assert transaction.timestamp == fixed_time


class TestBankAccountWithdrawals:
    """Test withdrawal operations and error handling."""
    
    @pytest.fixture
    def funded_account(self):
        """Provide an account with sufficient funds for testing."""
        return BankAccount(balance=1000, account_type="checking")
    
    def test_withdraw_with_sufficient_funds_decreases_balance(self, funded_account):
        """Test withdrawal with sufficient funds decreases balance."""
        initial_balance = funded_account.balance
        withdrawal_amount = 300
        
        result = funded_account.withdraw(withdrawal_amount)
        
        assert result is True
        assert funded_account.balance == initial_balance - withdrawal_amount
        assert len(funded_account.transactions) == 1
        assert funded_account.transactions[0].type == "withdrawal"
        assert funded_account.transactions[0].amount == withdrawal_amount
    
    def test_withdraw_exact_balance_empties_account(self, funded_account):
        """Test withdrawing exact balance results in zero balance."""
        withdrawal_amount = funded_account.balance
        
        result = funded_account.withdraw(withdrawal_amount)
        
        assert result is True
        assert funded_account.balance == 0
    
    def test_withdraw_insufficient_funds_raises_error(self, funded_account):
        """Test withdrawal with insufficient funds raises exception."""
        initial_balance = funded_account.balance
        withdrawal_amount = initial_balance + 500
        
        with pytest.raises(InsufficientFundsError) as exc_info:
            funded_account.withdraw(withdrawal_amount)
        
        assert f"Insufficient funds" in str(exc_info.value)
        assert funded_account.balance == initial_balance  # Balance unchanged
        assert len(funded_account.transactions) == 0  # No transaction recorded
    
    def test_withdraw_negative_amount_raises_error(self, funded_account):
        """Test that withdrawing negative amount raises ValueError."""
        initial_balance = funded_account.balance
        
        with pytest.raises(ValueError) as exc_info:
            funded_account.withdraw(-100)
        
        assert "Withdrawal amount must be positive" in str(exc_info.value)
        assert funded_account.balance == initial_balance
    
    def test_withdraw_zero_amount_no_change(self, funded_account):
        """Test that withdrawing zero amount doesn't change balance."""
        initial_balance = funded_account.balance
        initial_transaction_count = len(funded_account.transactions)
        
        result = funded_account.withdraw(0)
        
        assert result is False
        assert funded_account.balance == initial_balance
        assert len(funded_account.transactions) == initial_transaction_count


class TestBankAccountBalance:
    """Test balance calculations and retrievals."""
    
    def test_get_balance_returns_current_balance(self):
        """Test that get_balance returns the current account balance."""
        account = BankAccount(balance=1500, account_type="savings")
        assert account.get_balance() == 1500
    
    def test_balance_property_returns_current_balance(self):
        """Test that balance property returns current balance."""
        account = BankAccount(balance=2500, account_type="checking")
        assert account.balance == 2500
    
    def test_balance_reflects_transaction_history(self):
        """Test that balance reflects all transactions."""
        account = BankAccount(balance=1000, account_type="checking")
        
        account.deposit(500)
        account.withdraw(200)
        account.deposit(100)
        
        assert account.balance == 1400
        assert len(account.transactions) == 3


class TestBankAccountTransactions:
    """Test transaction history tracking."""
    
    @pytest.fixture
    def account_with_transactions(self):
        """Provide an account with sample transactions."""
        account = BankAccount(balance=1000, account_type="checking")
        account.deposit(500)
        account.withdraw(200)
        account.deposit(100)
        return account
    
    def test_get_transactions_returns_complete_history(self, account_with_transactions):
        """Test that get_transactions returns complete transaction history."""
        transactions = account_with_transactions.get_transactions()
        
        assert len(transactions) == 3
        assert transactions[0].type == "deposit"
        assert transactions[0].amount == 500
        assert transactions[1].type == "withdrawal"
        assert transactions[1].amount == 200
        assert transactions[2].type == "deposit"
        assert transactions[2].amount == 100
    
    def test_transaction_ordering_by_timestamp(self, account_with_transactions):
        """Test that transactions are ordered by timestamp."""
        transactions = account_with_transactions.get_transactions()
        
        timestamps = [t.timestamp for t in transactions]
        assert timestamps == sorted(timestamps)
    
    def test_empty_account_has_no_transactions(self):
        """Test that new account has empty transaction history."""
        account = BankAccount(balance=0, account_type="savings")
        assert len(account.get_transactions()) == 0


class TestBankAccountStateManagement:
    """Test account status changes (freeze, close, etc.)."""
    
    @pytest.fixture
    def active_account(self):
        """Provide an active account for testing."""
        return BankAccount(balance=1000, account_type="checking")
    
    def test_freeze_account_changes_status(self, active_account):
        """Test that freeze_account changes status to frozen."""
        result = active_account.freeze_account()
        
        assert result is True
        assert active_account.status == "frozen"
    
    def test_unfreeze_account_changes_status(self, active_account):
        """Test that unfreeze_account changes status to active."""
        active_account.freeze_account()
        
        result = active_account.unfreeze_account()
        
        assert result is True
        assert active_account.status == "active"
    
    def test_close_empty_account_succeeds(self):
        """Test that closing an empty account succeeds."""
        account = BankAccount(balance=0, account_type="checking")
        
        result = account.close_account()
        
        assert result is True
        assert account.status == "closed"
    
    def test_close_account_with_balance_raises_error(self, active_account):
        """Test that closing account with balance raises exception."""
        with pytest.raises(AccountNotEmptyError) as exc_info:
            active_account.close_account()
        
        assert "Cannot close account with remaining balance" in str(exc_info.value)
        assert active_account.status == "active"  # Status unchanged
    
    def test_account_status_property(self, active_account):
        """Test that status property returns current status."""
        assert active_account.status == "active"
        
        active_account.freeze_account()
        assert active_account.status == "frozen"


class TestBankAccountFrozenOperations:
    """Test operations on frozen accounts."""
    
    @pytest.fixture
    def frozen_account(self):
        """Provide a frozen account for testing."""
        account = BankAccount(balance=1000, account_type="checking")
        account.freeze_account()
        return account
    
    def test_deposit_on_frozen_account_raises_error(self, frozen_account):
        """Test that deposit on frozen account raises exception."""
        with pytest.raises(AccountFrozenError) as exc_info:
            frozen_account.deposit(100)
        
        assert "Account is frozen" in str(exc_info.value)
    
    def test_withdraw_on_frozen_account_raises_error(self, frozen_account):
        """Test that withdrawal on frozen account raises exception."""
        with pytest.raises(AccountFrozenError) as exc_info:
            frozen_account.withdraw(100)
        
        assert "Account is frozen" in str(exc_info.value)
    
    def test_balance_check_on_frozen_account_allowed(self, frozen_account):
        """Test that balance checking is allowed on frozen account."""
        balance = frozen_account.get_balance()
        assert balance == 1000  # Should work without error


class TestBankAccountClosedOperations:
    """Test operations on closed accounts."""
    
    @pytest.fixture
    def closed_account(self):
        """Provide a closed account for testing."""
        account = BankAccount(balance=0, account_type="checking")
        account.close_account()
        return account
    
    def test_deposit_on_closed_account_raises_error(self, closed_account):
        """Test that deposit on closed account raises exception."""
        with pytest.raises(AccountClosedError) as exc_info:
            closed_account.deposit(100)
        
        assert "Account is closed" in str(exc_info.value)
    
    def test_withdraw_on_closed_account_raises_error(self, closed_account):
        """Test that withdrawal on closed account raises exception."""
        with pytest.raises(AccountClosedError) as exc_info:
            closed_account.withdraw(100)
        
        assert "Account is closed" in str(exc_info.value)
    
    def test_freeze_closed_account_raises_error(self, closed_account):
        """Test that freezing closed account raises exception."""
        with pytest.raises(AccountClosedError) as exc_info:
            closed_account.freeze_account()
        
        assert "Cannot modify closed account" in str(exc_info.value)


class TestBankAccountPropertyBased:
    """Property-based tests for mathematical correctness."""
    
    @given(
        initial_balance=st.integers(min_value=0, max_value=1000000),
        deposit_amount=st.integers(min_value=1, max_value=1000000)
    )
    def test_deposit_always_increases_balance(self, initial_balance, deposit_amount):
        """Test that deposit never decreases balance (property-based test)."""
        account = BankAccount(balance=initial_balance, account_type="checking")
        original_balance = account.balance
        
        account.deposit(deposit_amount)
        
        assert account.balance > original_balance
        assert account.balance == original_balance + deposit_amount
    
    @given(
        initial_balance=st.integers(min_value=100, max_value=1000000),
        withdrawal_amount=st.integers(min_value=1, max_value=99)
    )
    def test_valid_withdrawal_decreases_balance(self, initial_balance, withdrawal_amount):
        """Test that valid withdrawal always decreases balance."""
        account = BankAccount(balance=initial_balance, account_type="checking")
        original_balance = account.balance
        
        account.withdraw(withdrawal_amount)
        
        assert account.balance < original_balance
        assert account.balance == original_balance - withdrawal_amount
    
    @given(
        operations=st.lists(
            st.tuples(
                st.sampled_from(["deposit", "withdraw"]),
                st.integers(min_value=1, max_value=100)
            ),
            min_size=1,
            max_size=20
        )
    )
    def test_balance_consistency_across_operations(self, operations):
        """Test that balance remains mathematically consistent across operations."""
        account = BankAccount(balance=10000, account_type="checking")  # Start with high balance
        expected_balance = 10000
        
        for operation, amount in operations:
            if operation == "deposit":
                account.deposit(amount)
                expected_balance += amount
            elif operation == "withdraw" and account.balance >= amount:
                account.withdraw(amount)
                expected_balance -= amount
        
        assert account.balance == expected_balance
    
    @given(
        deposit_amounts=st.lists(
            st.integers(min_value=1, max_value=1000),
            min_size=1,
            max_size=10
        )
    )
    def test_transaction_count_matches_operations(self, deposit_amounts):
        """Test that transaction count matches number of operations."""
        account = BankAccount(balance=0, account_type="checking")
        
        for amount in deposit_amounts:
            account.deposit(amount)
        
        assert len(account.transactions) == len(deposit_amounts)


class TestBankAccountSecurity:
    """Test security-related functionality."""
    
    def test_string_input_for_amounts_raises_error(self):
        """Test that string input for amounts raises appropriate error."""
        account = BankAccount(balance=1000, account_type="checking")
        
        with pytest.raises(TypeError):
            account.deposit("100")
        
        with pytest.raises(TypeError):
            account.withdraw("50")
    
    def test_none_input_for_amounts_raises_error(self):
        """Test that None input for amounts raises appropriate error."""
        account = BankAccount(balance=1000, account_type="checking")
        
        with pytest.raises(TypeError):
            account.deposit(None)
        
        with pytest.raises(TypeError):
            account.withdraw(None)
    
    def test_infinity_input_raises_error(self):
        """Test that infinity input raises appropriate error."""
        account = BankAccount(balance=1000, account_type="checking")
        
        with pytest.raises(ValueError):
            account.deposit(float('inf'))
        
        with pytest.raises(ValueError):
            account.withdraw(float('inf'))
    
    def test_nan_input_raises_error(self):
        """Test that NaN input raises appropriate error."""
        account = BankAccount(balance=1000, account_type="checking")
        
        with pytest.raises(ValueError):
            account.deposit(float('nan'))
        
        with pytest.raises(ValueError):
            account.withdraw(float('nan'))


class TestBankAccountIntegration:
    """Test interactions between account operations."""
    
    def test_complex_transaction_sequence(self):
        """Test complex sequence of operations maintains consistency."""
        account = BankAccount(balance=1000, account_type="checking")
        
        # Perform sequence of operations
        account.deposit(500)    # Balance: 1500
        account.withdraw(200)   # Balance: 1300
        account.deposit(100)    # Balance: 1400
        account.withdraw(300)   # Balance: 1100
        
        assert account.balance == 1100
        assert len(account.transactions) == 4
        
        # Verify transaction types
        transaction_types = [t.type for t in account.transactions]
        expected_types = ["deposit", "withdrawal", "deposit", "withdrawal"]
        assert transaction_types == expected_types
    
    def test_account_lifecycle_operations(self):
        """Test complete account lifecycle from creation to closure."""
        # Create account
        account = BankAccount(balance=1000, account_type="checking")
        assert account.status == "active"
        
        # Perform operations
        account.deposit(500)
        account.withdraw(200)
        
        # Freeze account
        account.freeze_account()
        assert account.status == "frozen"
        
        # Unfreeze account
        account.unfreeze_account()
        assert account.status == "active"
        
        # Empty account
        account.withdraw(account.balance)
        assert account.balance == 0
        
        # Close account
        account.close_account()
        assert account.status == "closed"
    
    @patch('src.banking.audit_logger.log_transaction')
    def test_transaction_logging_integration(self, mock_log):
        """Test that transactions are properly logged to audit system."""
        account = BankAccount(balance=1000, account_type="checking")
        
        account.deposit(500)
        account.withdraw(200)
        
        # Verify audit logging was called
        assert mock_log.call_count == 2
        
        # Verify log call arguments
        deposit_call = mock_log.call_args_list[0]
        withdrawal_call = mock_log.call_args_list[1]
        
        assert deposit_call[0][0].type == "deposit"
        assert deposit_call[0][0].amount == 500
        assert withdrawal_call[0][0].type == "withdrawal"
        assert withdrawal_call[0][0].amount == 200


@pytest.mark.performance
class TestBankAccountPerformance:
    """Test performance characteristics."""
    
    def test_large_number_of_transactions_performance(self, benchmark):
        """Benchmark performance with large number of transactions."""
        account = BankAccount(balance=100000, account_type="checking")
        
        def perform_transactions():
            for i in range(1000):
                if i % 2 == 0:
                    account.deposit(10)
                else:
                    account.withdraw(5)
        
        result = benchmark(perform_transactions)
        
        # Verify final state
        assert account.balance == 100000 + (500 * 10) - (500 * 5)  # Net +2500
        assert len(account.transactions) == 1000
    
    @pytest.mark.slow
    def test_memory_usage_with_many_transactions(self):
        """Test memory usage doesn't grow excessively with many transactions."""
        import sys
        
        account = BankAccount(balance=10000, account_type="checking")
        initial_size = sys.getsizeof(account)
        
        # Perform many transactions
        for i in range(10000):
            account.deposit(1)
        
        final_size = sys.getsizeof(account)
        
        # Memory growth should be reasonable (less than 10x)
        assert final_size < initial_size * 10


# Utility functions for test data generation
def create_test_account(balance=1000, account_type="checking"):
    """Helper function to create test accounts."""
    return BankAccount(balance=balance, account_type=account_type)


def create_account_with_history(operations):
    """Helper function to create account with predefined transaction history."""
    account = BankAccount(balance=1000, account_type="checking")
    
    for operation, amount in operations:
        if operation == "deposit":
            account.deposit(amount)
        elif operation == "withdraw":
            account.withdraw(amount)
    
    return account