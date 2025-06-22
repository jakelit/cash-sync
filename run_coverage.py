import subprocess
import sys
import webbrowser
import os

def main():
    """
    Run pytest with coverage, generate an HTML report, and open it in the default web browser.
    """
    print("Running tests with coverage...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", "--cov=src/excel_finance_tools", "--cov-report=html"
    ])
    if result.returncode != 0:
        print("\nTests failed. Coverage report may be incomplete.")
    else:
        html_path = os.path.abspath("htmlcov/index.html")
        print(f"\nCoverage HTML report generated at: {html_path}")
        if os.path.exists(html_path):
            print("Opening coverage report in your default browser...")
            webbrowser.open(f"file://{html_path}")
        else:
            print("Coverage HTML report not found.")

if __name__ == "__main__":
    main() 