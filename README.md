# Excel Finance Tools

A Python package for importing and managing bank transactions in Excel spreadsheets. This tool supports multiple banks including Ally and Capital One, and provides both command-line and GUI interfaces for importing transactions.

## Features

- **[Transaction Importing](./docs/import_transactions.md)**: Import financial data from CSV files from various banks using either a GUI or CLI. Includes automatic duplicate detection to ensure data integrity.
- **[Auto-Categorization](./docs/auto_categorize.md)**: Automatically categorize transactions based on a powerful and flexible set of user-defined rules in a dedicated "AutoCat" worksheet.
- **Modern GUI**: A clean and modern user interface provides a launchpad for all available tools.
- **Excel Integration**: All data is managed within a standard Excel workbook with structured tables.

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

The application can be started in GUI mode or run directly from the command line for specific tasks.

```bash
# To launch the main application GUI
python run.py

# --- Command-Line Usage ---

# To run the transaction importer
python run.py import <bank> <csv_file> <excel_file>

# To run the auto-categorizer
python run.py autocat <excel_file>

# --- Examples ---
# Import Capital One transactions
python run.py import capitalone transactions.csv my_finances.xlsx

# Auto-categorize transactions in an Excel file
python run.py autocat my_finances.xlsx
```
For more details on specific features, see the documentation in the `docs/` directory.

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

# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

3. Install **both** runtime and development dependencies:
```bash
# Install runtime dependencies (required for the application to work)
pip install -r requirements.txt

# Install development dependencies (for testing, linting, etc.)
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

This project uses separate requirements files to distinguish between runtime and development dependencies:

- **`requirements.txt`**: Runtime dependencies needed to run the application
  - `pandas`: Data manipulation and analysis
  - `openpyxl`: Excel file reading and writing

- **`requirements-dev.txt`**: Development tools and testing dependencies
  - `pytest`: Testing framework
  - `pylint`: Code quality and style checking
  - `pytest-cov`: Test coverage reporting
  - `black`: Code formatting
  - `flake8`: Linting
  - `mypy`: Type checking
  - `sphinx`: Documentation generation
  - `sphinx-rtd-theme`: Documentation theme

**Note**: For production deployments, only `requirements.txt` is needed. Development environments should install both files.

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
