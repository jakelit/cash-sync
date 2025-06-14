import subprocess
import sys

def run_checks():
    """Run all tests and code quality checks."""
    print("Running tests...")
    test_result = subprocess.run(["pytest", "tests/"], capture_output=True, text=True)
    print(test_result.stdout)
    if test_result.stderr:
        print("Test errors:", test_result.stderr)
    
    print("\nRunning pylint...")
    lint_result = subprocess.run(["pylint", "src/"], capture_output=True, text=True)
    print(lint_result.stdout)
    if lint_result.stderr:
        print("Lint errors:", lint_result.stderr)
    
    # Return success only if both checks pass
    return test_result.returncode == 0 and lint_result.returncode == 0

if __name__ == "__main__":
    success = run_checks()
    sys.exit(0 if success else 1) 