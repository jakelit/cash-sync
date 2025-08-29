# Cash Sync Architecture

## Overview

Cash Sync is a Python-based financial transaction management application that imports bank CSV files into Excel spreadsheets and provides automatic transaction categorization. The application follows a modular, layered architecture with clear separation of concerns.

## Architecture Principles

- **Separation of Concerns**: Each module has a single, well-defined responsibility
- **Interface Segregation**: Abstract interfaces define contracts between components
- **Dependency Inversion**: High-level modules depend on abstractions, not concrete implementations
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed Principle**: Open for extension, closed for modification

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
├─────────────────────────────────────────────────────────────┤
│  MainGUI ── ImporterGUI ── AutoCategorizeGUI               │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                         │
├─────────────────────────────────────────────────────────────┤
│  CashSyncApp ── AutoCategorizer ── TransactionImporter     │
├─────────────────────────────────────────────────────────────┤
│                    Domain Layer                              │
├─────────────────────────────────────────────────────────────┤
│  BaseImporter ── AllyImporter ── CapitalOneImporter        │
├─────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                      │
├─────────────────────────────────────────────────────────────┤
│  ExcelHandler ── CSVHandler ── DuplicateChecker ── Logger   │
├─────────────────────────────────────────────────────────────┤
│                    External Dependencies                     │
├─────────────────────────────────────────────────────────────┤
│  Excel Files ── CSV Files ── File System ── Tkinter GUI    │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Presentation Layer

#### MainGUI (`main_gui.py`)
- **Purpose**: Main application window and navigation controller
- **Responsibilities**:
  - Application lifecycle management
  - Frame switching and navigation
  - UI styling and theming
- **Dependencies**: Tkinter, other GUI frames

#### ImporterGUI (`importer_gui.py`)
- **Purpose**: User interface for transaction import operations
- **Responsibilities**:
  - File selection dialogs
  - Bank selection interface
  - Import progress feedback
- **Dependencies**: BaseImporter implementations

#### AutoCategorizeGUI (`auto_categorize_gui.py`)
- **Purpose**: User interface for auto-categorization operations
- **Responsibilities**:
  - Excel file selection
  - Categorization progress display
  - Results reporting
- **Dependencies**: AutoCategorizer

### 2. Application Layer

#### CashSyncApp (`__init__.py`)
- **Purpose**: Application entry point and command-line interface
- **Responsibilities**:
  - Command-line argument parsing
  - Routing to appropriate functionality
  - Error handling and logging
- **Dependencies**: All major components

#### AutoCategorizer (`auto_categorizer.py`)
- **Purpose**: Automatically categorizes transactions using pattern matching
- **Responsibilities**:
  - Rule parsing and validation
  - Pattern matching against transaction descriptions
  - Batch categorization processing
- **Dependencies**: ExcelHandler, rule definitions

### 3. Domain Layer

#### TransactionImporter Interface (`importer_interface.py`)
- **Purpose**: Abstract contract for all transaction importers
- **Responsibilities**:
  - Defines required methods for importers
  - Ensures consistent interface across implementations
- **Dependencies**: None (pure interface)

#### BaseImporter (`base_importer.py`)
- **Purpose**: Abstract base class providing common import functionality
- **Responsibilities**:
  - CSV validation and parsing
  - Duplicate detection
  - Excel writing operations
  - Error handling and logging
- **Dependencies**: CSVHandler, ExcelHandler, DuplicateChecker

#### Bank-Specific Importers
- **AllyImporter** (`ally_importer.py`): Ally Bank CSV format support
- **CapitalOneImporter** (`capital_one_importer.py`): Capital One CSV format support
- **Responsibilities**:
  - Institution-specific column mapping
  - Transaction parsing logic
  - Data cleaning and formatting

### 4. Infrastructure Layer

#### ExcelHandler (`excel_handler.py`)
- **Purpose**: Manages all Excel workbook operations
- **Responsibilities**:
  - Workbook loading and saving
  - Table structure validation
  - Data reading and writing
  - Format preservation
- **Dependencies**: openpyxl, pandas

#### CSVHandler (`csv_handler.py`)
- **Purpose**: Handles CSV file operations
- **Responsibilities**:
  - CSV file reading and validation
  - Column detection and mapping
  - Data type conversion
- **Dependencies**: pandas

#### DuplicateChecker (`duplicate_checker.py`)
- **Purpose**: Identifies and prevents duplicate transactions
- **Responsibilities**:
  - Transaction comparison logic
  - Duplicate detection algorithms
  - Similarity scoring
- **Dependencies**: pandas

#### Logger (`logger.py`)
- **Purpose**: Centralized logging configuration
- **Responsibilities**:
  - Log formatting and output
  - Log level management
  - File and console logging
- **Dependencies**: Python logging module

## Data Flow

### Transaction Import Flow
```
CSV File → CSVHandler → BaseImporter → DuplicateChecker → ExcelHandler → Excel File
```

### Auto-Categorization Flow
```
Excel File → ExcelHandler → AutoCategorizer → Rule Processing → ExcelHandler → Excel File
```

### GUI Navigation Flow
```
MainGUI → ImporterGUI/AutoCategorizeGUI → Application Components → Infrastructure
```

## Design Patterns

The application employs several design patterns to achieve maintainability and extensibility:

### 1. Template Method Pattern
- **Location**: `BaseImporter` class
- **Purpose**: Defines the algorithm structure while allowing subclasses to override specific steps
- **Details**: See [ADR-002: Abstract Base Class for Importers](adrs/002-abstract-base-importer.md)

### 2. Strategy Pattern
- **Location**: Bank-specific importers
- **Purpose**: Allows runtime selection of different import strategies
- **Details**: See [ADR-002: Abstract Base Class for Importers](adrs/002-abstract-base-importer.md)

### 3. Factory Pattern
- **Location**: `BANKS` dictionary in `__init__.py`
- **Purpose**: Creates appropriate importer instances based on bank type

### 4. Observer Pattern
- **Location**: GUI components
- **Purpose**: Allows components to react to state changes

## Error Handling Strategy

### 1. Graceful Degradation
- GUI components handle missing dependencies gracefully
- Fallback to command-line interface when GUI unavailable

### 2. Comprehensive Logging
- All operations logged with appropriate detail levels
- Error context preserved for debugging
- **Detailed Implementation**: See [ADR-007: Logging Strategy](adrs/007-logging-strategy.md) for comprehensive logging architecture and patterns

### 3. User-Friendly Messages
- Clear error messages with actionable guidance
- Step-by-step instructions for common issues

## Security Considerations

### 1. Input Validation
- CSV file format validation
- Excel file structure verification
- Transaction data sanitization

### 2. File System Security
- Path validation to prevent directory traversal
- File permission checks
- Safe file operations

### 3. Data Privacy
- No external data transmission
- Local processing only
- Secure file handling

## Performance Characteristics

### 1. Memory Management
- Streaming CSV processing for large files
- Efficient pandas operations
- Minimal memory footprint

### 2. Processing Speed
- Optimized duplicate checking algorithms
- Batch processing for categorization
- Efficient Excel operations

### 3. Scalability
- Modular design supports easy extension
- Plugin architecture for new banks
- Configurable processing parameters

## Testing Strategy

The application follows comprehensive testing standards defined in `docs/testing-standards/`:

### 1. Unit Testing
- Individual component testing with coverage meeting [official requirements](testing-standards/tools-and-automation/coverage_requirements.md)
- Mock external dependencies
- Follow patterns in [Test Implementation Guide](testing-standards/test-implementation-guide.md)

### 2. Integration Testing
- Component interaction testing
- End-to-end workflow validation
- Real file system operations

### 3. Property-Based Testing
- Hypothesis-based validation for data integrity
- Edge case discovery
- See [Testing Standards Overview](testing-standards/testing_standards_readme.md) for details

## Deployment Architecture

### 1. Local Installation
- Python virtual environment
- pip-based dependency management
- Platform-independent operation

### 2. Distribution
- Source code distribution
- Requirements file for dependencies
- Clear installation instructions

### 3. Configuration
- Environment-based configuration
- File-based settings
- User-specific preferences

## Future Architecture Considerations

### 1. Extensibility
- Plugin system for new banks
- Custom categorization rules
- Export format support

### 2. Scalability
- Database backend option
- Multi-user support
- Cloud synchronization

### 3. Integration
- API endpoints for external tools
- Web interface option
- Mobile application support

## Compliance and Standards

### 1. Code Standards
See [Architecture Standards](architecture-standards.md) for comprehensive code standards including:
- **PEP 8 Compliance**: Style guidelines and formatting
- **Type Hints**: Comprehensive type annotations
- **Documentation**: Component and API documentation

### 2. Testing Standards
- **Coverage Requirements**: See [official coverage requirements](testing-standards/tools-and-automation/coverage_requirements.md)
- **Test Organization**: Follow patterns in `docs/testing-standards/`
- **Property-Based Testing**: Use hypothesis for comprehensive validation
- **Security Testing**: Input validation and boundary testing
- **Implementation Guide**: See `docs/testing-standards/test-implementation-guide.md`

### 3. Documentation Standards
- **Architecture Decision Records**: See `docs/adrs/` for historical decisions
- **ADR Format**: Follow standard format in `docs/adrs/README.md`
- **Architecture Standards**: See [Architecture Standards](architecture-standards.md) for comprehensive standards
- **API Documentation**: Comprehensive docstrings and type hints
- **User Guides**: Clear, actionable documentation for end users

## Key Architectural Decisions

The following major architectural decisions are documented in detail in their respective ADRs:

- **[Layered Architecture](adrs/001-layered-architecture.md)**: Four-layer architecture with clear separation of concerns
- **[Abstract Base Classes](adrs/002-abstract-base-importer.md)**: Template method pattern for bank importers
- **[Excel Table Storage](adrs/003-excel-table-storage.md)**: Excel Tables for data persistence
- **[Tkinter GUI](adrs/004-tkinter-gui-framework.md)**: Cross-platform GUI with graceful degradation
- **[Pandas Processing](adrs/005-pandas-data-processing.md)**: Data processing and manipulation

## Related Documentation

### Architecture Decision Records (ADRs)
Detailed architectural decisions are documented in `docs/adrs/`:

- **[ADR-001: Layered Architecture Pattern](adrs/001-layered-architecture.md)**
- **[ADR-002: Abstract Base Class for Importers](adrs/002-abstract-base-importer.md)**
- **[ADR-003: Excel Table-Based Data Storage](adrs/003-excel-table-storage.md)**
- **[ADR-004: Tkinter GUI Framework](adrs/004-tkinter-gui-framework.md)**
- **[ADR-005: Pandas for Data Processing](adrs/005-pandas-data-processing.md)**
- **[ADR-006: Error Handling Strategy](adrs/006-error-handling-strategy.md)**
- **[ADR-007: Logging Strategy](adrs/007-logging-strategy.md)**

See [ADR Index](adrs/README.md) for complete overview and format guidelines.

### Testing Standards
This architecture aligns with comprehensive testing standards in `docs/testing-standards/`:

- **[Testing Standards Overview](testing-standards/testing_standards_readme.md)**
  - Complete testing framework and requirements
  - Coverage standards and quality gates
  - Test organization and naming conventions

- **[Test Implementation Guide](testing-standards/test-implementation-guide.md)**
  - Detailed coding standards for tests
  - Mocking strategies and fixture patterns
  - Property-based testing with hypothesis

- **[Test Plan Template](testing-standards/test-plan-template.md)**
  - Standard template for creating test plans
  - Required test categories and coverage requirements
  - Integration with CI/CD pipeline

### User Documentation
- **[Transaction Import Guide](import_transactions.md)**: Complete guide for importing bank transactions
- **[Auto-Categorization Guide](auto_categorize.md)**: Guide for automatic transaction categorization
- **[Main Documentation Index](README.md)**: Overview of all documentation

## Documentation Maintenance

### When Architecture Changes
1. **Update this document**: Reflect architectural changes in this file
2. **Create new ADRs**: Document significant architectural decisions
3. **Update related ADRs**: Modify existing ADRs if they're affected
4. **Review testing impact**: Ensure testing standards still apply
5. **Update user guides**: Modify user documentation if needed

### Cross-Reference Maintenance
- Keep all cross-references current and accurate
- Update ADR status when decisions change
- Ensure testing standards reflect architectural requirements
- Maintain consistency across all documentation
