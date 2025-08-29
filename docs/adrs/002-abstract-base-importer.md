# ADR-002: Abstract Base Class for Importers

## Status

Accepted

## Context

The application needed to support multiple bank CSV formats while maintaining consistent behavior and interfaces. Each bank has different CSV column names, data formats, and parsing requirements. We needed a way to:

- Ensure all importers follow the same interface
- Share common functionality between importers
- Allow easy addition of new bank support
- Maintain consistent error handling and logging
- Enable comprehensive testing of importer behavior

The challenge was to balance code reuse with the flexibility to handle bank-specific requirements.

## Decision

We implemented an abstract base class pattern with two key components:

1. **TransactionImporter Interface** (`importer_interface.py`): Pure abstract interface defining the contract
2. **BaseImporter Abstract Class** (`base_importer.py`): Abstract base class providing common functionality

### Interface Design

```python
class TransactionImporter(ABC):
    @abstractmethod
    def get_expected_columns(self) -> List[str]: ...
    
    @abstractmethod
    def get_institution_name(self) -> str: ...
    
    @abstractmethod
    def get_account_name(self) -> str: ...
    
    @abstractmethod
    def parse_transaction_amount(self, amount_str: str, transaction_type: str = None) -> float: ...    
    
```

### Base Class Implementation

The `BaseImporter` class provides the **shared import workflow** through the template method pattern:
- **Complete import workflow** (`import_transactions()` method) - **DO NOT OVERRIDE**
- Common CSV validation logic
- Duplicate checking functionality
- Excel writing operations
- Error handling and logging
- Template method pattern for the import workflow
- Date parsing with optional override capability

The abstract methods enable this shared workflow by providing bank-specific configuration points that the base class can call during the import process.

### Bank-Specific Implementations

- `AllyImporter`: Handles Ally Bank CSV format
- `CapitalOneImporter`: Handles Capital One CSV format

Each implementation provides bank-specific:
- Column mappings (via `get_expected_columns()`)
- Institution and account identification (via `get_institution_name()` and `get_account_name()`)
- Amount parsing logic (via `parse_transaction_amount()`)

**Important**: Implementations should **NOT** override the `import_transactions()` method. This method contains the shared workflow logic that all importers use. For additional flexibility, implementations can optionally override:

- `parse_transaction_date()` - Handle bank-specific date formats

Configuration methods like `set_column_mapping()` and `set_default_value()` should be called in `__init__()` rather than overridden.

## Consequences

### Positive Consequences
- **Shared Workflow**: All importers use the same proven import workflow logic
- **Consistency**: All importers follow the same interface and behavior patterns
- **Code Reuse**: Common functionality is shared through the base class
- **Extensibility**: New banks can be added by implementing only the required abstract methods
- **Testability**: Interface allows for comprehensive testing with mocks
- **Maintainability**: Changes to common logic only need to be made in one place
- **Type Safety**: Abstract methods ensure all required functionality is implemented
- **Flexibility**: Optional method overrides allow for bank-specific customizations

### Negative Consequences
- **Complexity**: Additional abstraction layers increase code complexity
- **Learning Curve**: Developers need to understand both interface and base class
- **Inheritance Coupling**: Bank implementations are coupled to the base class design
- **Interface Evolution**: Changes to the interface require updates to all implementations

### Testing Implications
- **Interface Testing**: Can test the interface contract independently
- **Base Class Testing**: Common functionality can be tested once in the base class
- **Implementation Testing**: Each bank implementation can be tested with bank-specific test data
- **Mock Testing**: Interface allows for easy mocking in higher-level tests
- **Coverage**: Each implementation must meet our [official coverage requirements](../testing-standards/tools-and-automation/coverage_requirements.md)

## Compliance

### Testing Standards Compliance
- **Unit Tests**: Each importer implementation has dedicated unit tests
- **Interface Tests**: Abstract interface is tested through concrete implementations
- **Base Class Tests**: Common functionality is tested in base class unit tests
- **Integration Tests**: Full import workflow is tested end-to-end
- **Property Tests**: Hypothesis-based tests validate data integrity across implementations

### Code Standards Compliance
See [Architecture Standards](../architecture-standards.md) for comprehensive code standards including:
- **PEP 8 Compliance**: Style guidelines and formatting
- **Type Hints**: Comprehensive type annotations for abstract methods
- **Documentation**: Component and interface documentation
- **Error Handling**: See [Architecture Standards](../architecture-standards.md) for error handling patterns

### Security Compliance
See [Architecture Standards](../architecture-standards.md) for comprehensive security standards including:
- **Input Validation**: Bank-specific validation requirements
- **Data Sanitization**: Secure data processing
- **Error Handling**: Secure error handling practices

## Implementation Example

```python
class AllyImporter(BaseImporter):
    def get_expected_columns(self) -> List[str]:
        return ['Date', 'Description', 'Amount', 'Balance', 'Account Number']
    
    def get_institution_name(self) -> str:
        return "Ally Bank"
    
    def get_account_name(self) -> str:
        return "Ally Checking"
    
    def parse_transaction_amount(self, amount_str: str, transaction_type: str = None) -> float:
        # Ally-specific amount parsing logic
        return float(amount_str.replace('$', '').replace(',', ''))
    
    # Optional: Override for bank-specific date parsing
    def parse_transaction_date(self, date_str: str) -> str:
        # Ally-specific date parsing if needed
        return date_str  # Default implementation
    
    def __init__(self):
        super().__init__()
        # Configure column mappings for Ally's CSV format
        self.set_column_mapping("Transaction Date", "Date")
        self.set_column_mapping("Transaction Description", "Description")
        # Set default values for missing columns
        self.set_default_value("Account Number", "Ally-1234")
```

## References

- [Architecture Documentation](../architecture.md)
- [Testing Standards](../testing-standards/)
- [Template Method Pattern](https://en.wikipedia.org/wiki/Template_method_pattern)
- [Strategy Pattern](https://en.wikipedia.org/wiki/Strategy_pattern)
