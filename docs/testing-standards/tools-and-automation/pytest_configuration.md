# pytest Configuration Guide

This guide covers the standard pytest configuration for consistent testing across all projects.

## 📋 Configuration Files

### pyproject.toml (Recommended)

```toml
[tool.pytest.ini_options]
# Test discovery
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

# Output and reporting
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--tb=short",
    "--cov=src",
    "--cov-branch",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-report=xml",
    "--cov-fail-under=90",
]

# Markers
markers = [
    "unit: marks tests as unit tests (fast, isolated)",
    "integration: marks tests as integration tests (slower, with dependencies)",
    "e2e: marks tests as end-to-end tests (slowest, full system)",
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "external_api: marks tests as requiring external API access",
    "database: marks tests as requiring database access",
    "security: marks tests as security-focused",
    "performance: marks tests as performance benchmarks",
]

# Filtering
filterwarnings = [
    "error",
    "ignore::UserWarning",
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
]

# Minimum version
minversion = "6.0"

# Test session configuration
testmon = true  # if using pytest-testmon
```

### Alternative: pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=src
    --cov-branch
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=90

markers =
    unit: marks tests as unit tests
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    slow: marks tests as slow
    external_api: marks tests as requiring external API
    database: marks tests as requiring database
    security: marks tests as security-focused
    performance: marks tests as performance benchmarks

filterwarnings =
    error
    ignore::UserWarning
    ignore::DeprecationWarning

minversion = 6.0
```

## 🛠️ Essential Plugins

### Core Testing Plugins

```bash
# Install essential pytest plugins
pip install pytest pytest-cov pytest-mock pytest-xdist pytest-html
```

```requirements
# requirements-test.txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-xdist>=3.0.0
pytest-html>=3.1.0
pytest-asyncio>=0.21.0  # for async tests
hypothesis>=6.0.0       # property-based testing
pytest-benchmark>=4.0.0 # performance testing
pytest-testmon>=2.0.0   # test selection optimization
```

### Plugin Configuration

```toml
# pyproject.toml additions for plugins

[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/tests/*",
    "*/test_*",
    "*/conftest.py",
    "*/__init__.py",
    "*/migrations/*",
    "*/venv/*",
    "*/.venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\bProtocol\):",
    "@(abc\.)?abstractmethod",
]
show_missing = true
precision = 2

[tool.coverage.html]
directory = "htmlcov"
```

## 🗂️ Project Structure

### Recommended Directory Layout

```
project/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── module1.py
│       └── module2.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_module1.py
│   │   └── test_module2.py
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_api_integration.py
│   └── e2e/
│       ├── __init__.py
│       └── test_user_workflows.py
├── pyproject.toml               # Configuration
└── requirements-test.txt        # Test dependencies
```

## 🔧 conftest.py Configuration

### Global Fixtures and Configuration

```python
"""
Global pytest configuration and fixtures.

This file is automatically loaded by pytest and provides shared fixtures
and configuration for all test modules.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone


# ============================================================================
# Session-scoped fixtures (expensive setup/teardown)
# ============================================================================

@pytest.fixture(scope="session")
def test_database():
    """Provide a test database for integration tests."""
    # Setup test database
    db = create_test_database()
    yield db
    # Cleanup
    db.close()
    drop_test_database()


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration settings."""
    return {
        "database_url": "sqlite:///:memory:",
        "api_base_url": "https://api.test.example.com",
        "debug": True,
        "log_level": "DEBUG",
    }


# ============================================================================
# Function-scoped fixtures (per-test setup/teardown)
# ============================================================================

@pytest.fixture
def temp_dir():
    """Provide a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_datetime():
    """Provide a fixed datetime for consistent testing."""
    fixed_time = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
    with patch('datetime.datetime') as mock_dt:
        mock_dt.now.return_value = fixed_time
        mock_dt.utcnow.return_value = fixed_time
        yield mock_dt


@pytest.fixture
def mock_requests():
    """Mock requests library for HTTP calls."""
    with patch('requests.Session') as mock_session:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.text = '{"status": "success"}'
        mock_session.return_value.get.return_value = mock_response
        mock_session.return_value.post.return_value = mock_response
        yield mock_session


@pytest.fixture
def sample_data():
    """Provide sample data for testing."""
    return {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        ],
        "accounts": [
            {"id": 1, "user_id": 1, "balance": 1000.0, "type": "checking"},
            {"id": 2, "user_id": 2, "balance": 2500.0, "type": "savings"},
        ],
    }


# ============================================================================
# Pytest hooks and configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "requires_network: mark test as requiring network access"
    )
    config.addinivalue_line(
        "markers", "requires_gpu: mark test as requiring GPU"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Auto-mark tests based on file location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        
        # Auto-mark slow tests
        if "slow" in item.name or "performance" in item.name:
            item.add_marker(pytest.mark.slow)


def pytest_runtest_setup(item):
    """Setup run before each test."""
    # Skip tests marked as requiring network if --offline flag is used
    if "requires_network" in item.keywords and item.config.getoption("--offline", default=False):
        pytest.skip("Test requires network access")


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--offline",
        action="store_true",
        default=False,
        help="Run tests in offline mode (skip network-dependent tests)"
    )
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests"
    )


# ============================================================================
# Async fixtures (for async testing)
# ============================================================================

@pytest.fixture
async def async_client():
    """Provide async HTTP client for testing."""
    import aiohttp
    async with aiohttp.ClientSession() as session:
        yield session


# ============================================================================
# Database fixtures
# ============================================================================

@pytest.fixture
def db_session():
    """Provide database session with rollback."""
    session = create_db_session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def populated_db(db_session, sample_data):
    """Provide database session with sample data."""
    # Insert sample data
    for user_data in sample_data["users"]:
        user = User(**user_data)
        db_session.add(user)
    
    for account_data in sample_data["accounts"]:
        account = Account(**account_data)
        db_session.add(account)
    
    db_session.commit()
    yield db_session
```

## 🚀 Common Usage Patterns

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit                    # Only unit tests
pytest -m "not slow"              # Exclude slow tests
pytest -m "unit and not external_api"  # Unit tests without API calls

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run tests in parallel
pytest -n auto                    # Auto-detect CPU cores
pytest -n 4                       # Use 4 workers

# Run specific tests
pytest tests/unit/test_module.py  # Specific file
pytest tests/unit/test_module.py::TestClass::test_method  # Specific test

# Run with verbose output
pytest -v                         # Verbose
pytest -s                         # Don't capture output (see print statements)
pytest -x                         # Stop on first failure
pytest --pdb                      # Drop into debugger on failure

# Generate reports
pytest --html=report.html         # HTML report
pytest --junitxml=junit.xml       # JUnit XML report
```

### Environment-Specific Testing

```bash
# Development environment
pytest --cov=src --cov-report=term-missing -v

# CI/CD environment
pytest --cov=src --cov-report=xml --cov-fail-under=90 --junitxml=junit.xml

# Local testing with file watching
pytest-watch --runner "pytest --cov=src"

# Performance testing
pytest -m performance --benchmark-only

# Integration testing
pytest -m integration --maxfail=5
```

## 📊 Coverage Configuration

### Advanced Coverage Settings

```toml
[tool.coverage.run]
source = ["src"]
branch = true
parallel = true  # For parallel test execution
data_file = ".coverage"

# Include/exclude patterns
include = ["src/*"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/conftest.py",
    "*/__init__.py",
    "*/migrations/*",
    "*/vendor/*",
    "*/.venv/*",
    "*/venv/*",
]

# Plugins
plugins = ["coverage_conditional_plugin"]

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
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if False:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
    "except ImportError:",
    "except ModuleNotFoundError:",
]

[tool.coverage.html]
directory = "htmlcov"
title = "Test Coverage Report"

[tool.coverage.xml]
output = "coverage.xml"
```

## 🔍 Debugging Configuration

### Debug-Friendly Settings

```python
# conftest.py additions for debugging

@pytest.fixture(autouse=True)
def debug_mode(request):
    """Enable debug mode for specific tests."""
    if "debug" in request.keywords:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        # Enable SQL query logging if using SQLAlchemy
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


@pytest.fixture
def capture_logs():
    """Capture logs for test assertions."""
    import logging
    from io import StringIO
    
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    yield log_capture
    
    logger.removeHandler(handler)
```

### Usage in Tests

```python
@pytest.mark.debug
def test_with_debug_logging():
    """This test will have debug logging enabled."""
    pass

def test_log_output(capture_logs):
    """Test that verifies log output."""
    logger = logging.getLogger(__name__)
    logger.info("Test message")
    
    log_output = capture_logs.getvalue()
    assert "Test message" in log_output
```

## 🎯 Best Practices

### Configuration Best Practices

1. **Use pyproject.toml** for modern Python projects
2. **Set strict mode** (`--strict-markers`, `--strict-config`)
3. **Configure coverage thresholds** appropriate for your project
4. **Use markers** to categorize tests effectively
5. **Configure parallel execution** for faster test runs
6. **Set up proper test discovery** patterns
7. **Configure appropriate warning filters**

### Performance Optimization

```toml
[tool.pytest.ini_options]
# Optimize test discovery
collect_ignore = [
    "setup.py",
    "docs",
    "build",
    "dist",
    ".eggs",
    "*.egg-info",
]

# Cache settings
cache_dir = ".pytest_cache"

# Parallel execution
addopts = [
    "-n auto",  # Use all available CPU cores
    "--dist=worksteal",  # Better load balancing
]
```

### CI/CD Integration

```yaml
# Example GitHub Actions configuration
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml --cov-fail-under=90
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

This configuration provides a solid foundation for consistent, maintainable, and scalable testing across all your Python projects.