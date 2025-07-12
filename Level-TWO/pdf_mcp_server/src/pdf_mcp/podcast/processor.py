"""
Simple podcast processor for PDF-to-podcast conversion
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from ..config.settings import settings

class PodcastProcessor:
    """Simple processor for generating podcast scripts"""
    
    def __init__(self):
        # Ensure podcast directory exists
        settings.podcast_storage_path.mkdir(parents=True, exist_ok=True)
    
    def generate_podcast_script(self, pdf_text: str, style: str = "interview") -> str:
        """Generate a simple podcast script from PDF content"""
        
        # Take first 2000 characters for the script
        content_summary = pdf_text[:2000] if len(pdf_text) > 2000 else pdf_text
        
        if style.lower() == "interview":
            script = INTERVIEW_TEMPLATE.format(content=content_summary)
        elif style.lower() == "educational":
            script = EDUCATIONAL_TEMPLATE.format(content=content_summary)
        else:
            # Default to interview style
            script = INTERVIEW_TEMPLATE.format(content=content_summary)
        
        return script
    
    def save_podcast_script(self, script: str, filename: str) -> str:
        """Save podcast script to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_filename = f"podcast_{filename}_{timestamp}.txt"
        script_path = settings.podcast_storage_path / script_filename
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("-" * 50 + "\n\n")
            f.write(script)
        
        return str(script_path)
