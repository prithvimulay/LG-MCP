#!/usr/bin/env python3
"""
PDF Query and Podcast Generation System

This script allows querying PDFs using natural language and generating podcast-style
conversations based on PDF content using LangGraph and MCP tools.
"""

import sys
import os
import asyncio
from src.pdf_mcp.run_graph import main

if __name__ == "__main__":
    # Ensure PDFs directory exists
    os.makedirs("data/pdfs", exist_ok=True)
    
    # Run the main function from run_graph.py
    sys.exit(asyncio.run(main()))
