#!/usr/bin/env python3
"""
Development helper script to run tests and code quality checks using the virtual environment.
This ensures we always use the correct Python environment.
"""

import subprocess
import sys
import os
from pathlib import Path

def get_venv_python():
    """Get the path to the virtual environment's Python executable."""
    project_root = Path(__file__).parent
    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    
    if not venv_python.exists():
        print("❌ Virtual environment not found at .venv/Scripts/python.exe")
        print("Please ensure the virtual environment is set up correctly.")
        sys.exit(1)
    
    return str(venv_python)

def run_command(cmd_args, description="Command"):
    """Run a command using the virtual environment's Python."""
    venv_python = get_venv_python()
    full_cmd = [venv_python, "-m"] + cmd_args
    
    print(f"🔧 {description}: {' '.join(full_cmd)}")
    print(f"📁 Using virtual environment: {venv_python}")
    print("-" * 50)
    
    try:
        result = subprocess.run(full_cmd, check=True)
        print(f"✅ {description} completed successfully")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return e.returncode

def run_checks():
    """Run all tests and code quality checks."""
    print("🚀 Starting development checks...")
    print("=" * 60)
    
    # Run tests
    test_result = run_command(["pytest", "tests/"], "Running tests")
    
    # Run pylint
    lint_result = run_command(["pylint", "src/"], "Running pylint")
    
    print("=" * 60)
    
    # Return success only if all checks pass
    all_passed = all(result == 0 for result in [test_result, lint_result])
    
    if all_passed:
        print("🎉 All checks passed!")
    else:
        print("⚠️  Some checks failed. Please review the output above.")
    
    return all_passed

def run_specific_check(check_type):
    """Run a specific type of check."""
    checks = {
        "test": (["pytest", "tests/"], "Running tests"),
        "pytest": (["pytest", "tests/"], "Running tests"),
        "lint": (["pylint", "src/"], "Running pylint"),
        "pylint": (["pylint", "src/"], "Running pylint"),
        "all": None  # Special case handled in main
    }
    
    if check_type not in checks:
        print(f"❌ Unknown check type: {check_type}")
        print("Available checks: test, pytest, lint, pylint, all")
        return False
    
    if check_type == "all":
        return run_checks()
    
    cmd_args, description = checks[check_type]
    result = run_command(cmd_args, description)
    return result == 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific check
        check_type = sys.argv[1].lower()
        success = run_specific_check(check_type)
    else:
        # Run all checks (default behavior)
        success = run_checks()
    
    sys.exit(0 if success else 1) 