#!/usr/bin/env python3
"""
Development helper script to run tests and code quality checks using the virtual environment.
This ensures we always use the correct Python environment.
"""

import subprocess
import sys
import os
from pathlib import Path

def get_python_executable():
    """Get the appropriate Python executable to use."""
    project_root = Path(__file__).parent
    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    
    # Check if virtual environment exists and use it
    if venv_python.exists():
        return str(venv_python)
    
    # Fall back to system Python (for CI environments)
    print("📝 No virtual environment found, using system Python")
    return sys.executable

def run_command(cmd_args, description="Command"):
    """Run a command using the appropriate Python executable."""
    python_exe = get_python_executable()
    full_cmd = [python_exe] + cmd_args
    
    print(f"🔧 Running {description}: {' '.join(full_cmd)}")
    print(f"📁 Using Python: {python_exe}")
    
    try:
        result = subprocess.run(full_cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def run_checks():
    """Run all checks and return True if all passed."""
    print("🚀 Starting development checks...")
    
    # Run tests with coverage
    tests_passed = run_command(
        ["-m", "pytest", "--cov=src", "--cov-report=xml"],
        "tests"
    )
    
    # Run pylint
    lint_passed = run_command(
        ["-m", "pylint", "src/"],
        "pylint"
    )
    
    return tests_passed and lint_passed

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "help":
            print("""
🔧 Development Check Script

Usage:
  python check.py [command]

Available commands:
  test    - Run tests only
  lint    - Run pylint only  
  all     - Run all checks (default)
  help    - Show this help message

Examples:
  python check.py test    # Run tests only
  python check.py lint    # Run pylint only
  python check.py all     # Run all checks
  python check.py         # Run all checks (default)
            """)
            return
        
        elif command == "test":
            success = run_command(
                ["-m", "pytest", "--cov=src", "--cov-report=xml"],
                "tests"
            )
        elif command == "lint":
            success = run_command(
                ["-m", "pylint", "src/"],
                "pylint"
            )
        elif command == "all":
            success = run_checks()
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python check.py help' for available commands")
            sys.exit(1)
    else:
        # Default: run all checks
        success = run_checks()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 