"""
Simple logging for MVP
"""

import logging
import sys


class SimpleLogger:
    """Minimal logger for PDF MCP Server"""
    
    def __init__(self, name: str = "pdf_mcp"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)


# Global logger instance
logger = SimpleLogger()


def log_info(message: str):
    """Quick info logging"""
    logger.info(message)


def log_error(message: str):
    """Quick error logging"""
    logger.error(message)