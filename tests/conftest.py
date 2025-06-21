"""
Pytest configuration file.

This file adds the project's source directory to the Python path
so that pytest can find the `excel_finance_tools` package.
"""
import sys
import os

# Add the src directory to the Python path so that tests can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))) 