# Excel Finance Tools

A Python package for importing and managing bank transactions in Excel spreadsheets. This tool supports multiple banks including Ally and Capital One, and provides both command-line and GUI interfaces for importing transactions.

## Features

- Import transactions from multiple bank CSV files
- Support for Ally and Capital One banks
- Command-line and GUI interfaces
- Automatic duplicate detection
- Excel spreadsheet management
- Transaction categorization

## Installation

### For Users

1. Clone the repository:
```bash
git clone https://github.com/jakelit/excelFinanceTools.git
cd excelFinanceTools
```

2. Install runtime dependencies:
```bash
pip install -r requirements.txt
```

3. Run the launcher script:
```bash
python run.py
```

## Usage

### Command Line Interface

```bash
# Using GUI
python -m excel_finance_tools

# Using command line
python -m excel_finance_tools [bank] [csv_file] [excel_file]

# Examples:
python -m excel_finance_tools capitalone transactions.csv transactions.xlsx
python -m excel_finance_tools ally transactions.csv transactions.xlsx
```

### Python API

```python
from excel_finance_tools import AllyImporter, CapitalOneImporter

# Import Ally transactions
importer = AllyImporter()
success, message = importer.import_transactions("transactions.csv", "transactions.xlsx")
```

## Development

### Setup Development Environment

1. Clone the repository:
```bash
git clone https://github.com/jakelit/excelFinanceTools.git
cd excelFinanceTools
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Running Tests and Checks

Run all tests and code quality checks:
```bash
python check.py
```

Or run individual checks:
```bash
pytest tests/          # Run tests
pylint src/           # Run code quality checks
```

### Requirements Files

- `requirements.txt`: Runtime dependencies (pandas, openpyxl)
- `requirements-dev.txt`: Development tools (pytest, pylint, etc.)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the pandas and openpyxl communities for their excellent libraries 