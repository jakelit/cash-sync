# CI/CD Integration Guide

This guide covers integrating our testing standards with various CI/CD platforms and automation tools.

## 🚀 GitHub Actions

### Basic Test Workflow

```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PYTHONPATH: src

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --tb=short \
          --cov=src --cov-branch \
          --cov-report=xml --cov-report=term-missing \
          --cov-fail-under=90 \
          --junitxml=junit/test-results-unit.xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v --tb=short \
          --junitxml=junit/test-results-integration.xml
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results-${{ matrix.python-version }}
        path: junit/test-results-*.xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true
```

### Advanced Multi-Stage Workflow

```yaml
# .github/workflows/comprehensive-tests.yml
name: Comprehensive Test Suite

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 0'  # Weekly full test run

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install linting tools
      run: |
        pip install black isort flake8 mypy
    
    - name: Run linting
      run: |
        black --check src tests
        isort --check-only src tests
        flake8 src tests
        mypy src

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run security checks
      uses: pypa/gh-action-pip-audit@v1.0.8

  unit-tests:
    runs-on: ubuntu-latest
    needs: [lint]
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt -r requirements-test.txt
    
    - name: Run unit tests with coverage
      run: |
        pytest tests/unit/ -v -x \
          --cov=src --cov-branch --cov-report=xml \
          --cov-fail-under=90 \
          --junitxml=junit/test-results.xml
    
    - name: Upload coverage
      if: matrix.python-version == '3.11'
      uses: codecov/codecov-action@v3

  integration-tests:
    runs-on: ubuntu-latest
    needs: [unit-tests]
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt -r requirements-test.txt
    
    - name: Run integration tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
      run: |
        pytest tests/integration/ -v \
          --junitxml=junit/integration-results.xml

  performance-tests:
    runs-on: ubuntu-latest
    needs: [integration-tests]
    if: github.event_name == 'schedule' || contains(github.event.head_commit.message, '[perf]')
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt -r requirements-test.txt
    
    - name: Run performance tests
      run: |
        pytest tests/performance/ -v \
          --benchmark-json=benchmark.json
    
    - name: Store benchmark results
      uses: benchmark-action/github-action-benchmark@v1
      with:
        tool: 'pytest'
        output-file-path: benchmark.json
        github-token: ${{ secrets.GITHUB_TOKEN }}
        auto-push: true

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [integration-tests]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt -r requirements-test.txt
    
    - name: Run end-to-end tests
      run: |
        pytest tests/e2e/ -v --tb=short \
          --junitxml=junit/e2e-results.xml
```

## 🔧 Pre-commit Hooks

### .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]

  - repo: local
    hooks:
      - id: pytest-unit
        name: pytest-unit
        entry: pytest tests/unit/ -x --tb=short
        language: system
        types: [python]
        pass_filenames: false
        always_run: true

      - id: pytest-integration
        name: pytest-integration
        entry: pytest tests/integration/ -x --tb=short
        language: system
        types: [python]
        pass_filenames: false
        stages: [manual]
```

### Setup Instructions

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# Run against all files
pre-commit run --all-files

# Run integration tests manually
pre-commit run pytest-integration --hook-stage manual
```

## 🐳 Docker Integration

### Test Dockerfile

```dockerfile
# Dockerfile.test
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements-test.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-test.txt

# Copy source code
COPY src/ src/
COPY tests/ tests/
COPY pyproject.toml ./

# Set Python path
ENV PYTHONPATH=/app/src

# Default command
CMD ["pytest", "tests/", "-v", "--cov=src", "--cov-report=term-missing"]
```

### Docker Compose for Testing

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  test:
    build:
      context: .
      dockerfile: Dockerfile.test
    environment:
      - PYTHONPATH=/app/src
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/test_db
    depends_on:
      - db
    volumes:
      - ./htmlcov:/app/htmlcov
      - ./junit:/app/junit
    command: >
      bash -c "
        pytest tests/unit/ -v --cov=src --cov-report=html --cov-report=xml --junitxml=junit/unit.xml &&
        pytest tests/integration/ -v --junitxml=junit/integration.xml
      "

  db:
    image: postgres:14-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=test_db
    ports:
      - "5432:5432"

  test-performance:
    build:
      context: .
      dockerfile: Dockerfile.test
    command: pytest tests/performance/ -v --benchmark-json=benchmark.json
    volumes:
      - ./benchmark.json:/app/benchmark.json
```

### Run Tests with Docker

```bash
# Run all tests
docker-compose -f docker-compose.test.yml up --build

# Run specific test suites
docker-compose -f docker-compose.test.yml run test pytest tests/unit/ -v

# Run with coverage
docker-compose -f docker-compose.test.yml run test \
  pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

## 📊 Quality Gates and Reporting

### SonarQube Integration

```yaml
# .github/workflows/sonarqube.yml
name: SonarQube Analysis

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  sonarqube:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install dependencies and run tests
      run: |
        pip install -r requirements.txt -r requirements-test.txt
        pytest tests/ --cov=src --cov-report=xml --junitxml=junit.xml

    - name: SonarQube Scan
      uses: sonarqube-quality-gate-action@master
      env:
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      with:
        scanMetadataReportFile: coverage.xml
```

### Quality Gate Configuration

```bash
# sonar-project.properties
sonar.projectKey=my-python-project
sonar.organization=my-org
sonar.sources=src
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=junit.xml

# Quality gate thresholds
sonar.coverage.minimum=90
sonar.duplicated_lines_density.maximum=3
sonar.maintainability_rating.minimum=A
sonar.reliability_rating.minimum=A
sonar.security_rating.minimum=A
```

## 📈 Test Result Aggregation

### Test Report Generation

```python
# scripts/generate_test_report.py
"""Generate comprehensive test report from multiple test runs."""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

def generate_html_report():
    """Generate HTML test report."""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Report</title>
        <style>
            body { font-family: Arial, sans-serif; }
            .passed { color: green; }
            .failed { color: red; }
            .summary { background: #f0f0f0; padding: 10px; }
        </style>
    </head>
    <body>
        <h1>Test Report</h1>
        <div class="summary">
            <h2>Summary</h2>
            <p>Generated: {timestamp}</p>
            <p>Total Tests: {total}</p>
            <p>Passed: <span class="passed">{passed}</span></p>
            <p>Failed: <span class="failed">{failed}</span></p>
            <p>Coverage: {coverage}%</p>
        </div>
        {test_details}
    </body>
    </html>
    """
    
    # Implementation here
    pass

if __name__ == "__main__":
    generate_html_report()
```

### Notification Integration

```yaml
# .github/workflows/notify.yml
name: Test Notifications

on:
  workflow_run:
    workflows: ["Tests"]
    types:
      - completed

jobs:
  notify:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    steps:
    - name: Notify Slack on failure
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ github.event.workflow_run.conclusion }}
        channel: '#dev-alerts'
        text: 'Test suite failed on ${{ github.event.workflow_run.head_branch }}'
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## 🔄 Continuous Deployment Integration

### Deploy on Test Success

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  workflow_run:
    workflows: ["Comprehensive Test Suite"]
    types:
      - completed
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    
    steps:
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # Deployment commands here
    
    - name: Run smoke tests
      run: |
        pytest tests/smoke/ -v --tb=short
    
    - name: Deploy to production
      if: success()
      run: |
        echo "Deploying to production environment"
        # Production deployment commands here
```

## 📋 Best Practices Summary

### CI/CD Configuration

1. **Fail Fast**: Run quick tests (lint, unit) before expensive tests
2. **Parallel Execution**: Use matrix builds for multiple Python versions
3. **Caching**: Cache dependencies to speed up builds
4. **Artifacts**: Store test results and reports
5. **Quality Gates**: Enforce coverage and quality thresholds
6. **Notifications**: Alert team on failures
7. **Security**: Scan dependencies and code for vulnerabilities

### Test Organization

1. **Separate test types**: Unit, integration, e2e in different stages
2. **Environment isolation**: Use containers for consistent environments
3. **Test data management**: Use fixtures and factories for clean test data
4. **Parallel execution**: Run tests in parallel when possible
5. **Selective testing**: Run only affected tests for faster feedback

### Monitoring and Alerting

1. **Test result tracking**: Store historical test results
2. **Performance regression detection**: Track test execution times
3. **Coverage trends**: Monitor coverage changes over time
4. **Failure analysis**: Categorize and track failure patterns
5. **Team notifications**: Alert relevant team members on failures

### Documentation

1. **Pipeline documentation**: Document CI/CD processes
2. **Troubleshooting guides**: Common issues and solutions
3. **Performance baselines**: Document expected test execution times
4. **Environment setup**: Clear instructions for local development