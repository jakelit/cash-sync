import os
import sys

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from excel_finance_tools import main

if __name__ == "__main__":
    main() 