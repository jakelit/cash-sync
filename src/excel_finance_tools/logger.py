"""
This module configures and provides a centralized logging instance for the
entire application.
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[41m',  # Red background
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        # Add timestamp to the record
        record.asctime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Get the color for this level
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        
        # Format the message with color
        formatted_msg = f"{color}{record.asctime} - {record.levelname} - {record.getMessage()}{self.COLORS['RESET']}"
        
        # Add exception info if present
        if record.exc_info:
            formatted_msg += f"\n{self.formatException(record.exc_info)}"
            
        return formatted_msg

def setup_logger(name: str = 'excel_finance_tools', 
                log_file: Optional[str] = None) -> logging.Logger:
    """Set up and configure the logger.
    
    Args:
        name: Name of the logger
        log_file: Path to log file (default: logs/app.log)
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Create logs directory if it doesn't exist
    if log_file is None:
        log_file = 'logs/app.log'
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # File handler (no colors)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Console handler (with colors)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter()
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create default logger instance
logger = setup_logger() 