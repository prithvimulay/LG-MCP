"""
Simple podcast processor for PDF-to-podcast conversion
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Audio generation imports
try:
    from gtts import gTTS
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

from ..config.settings import settings
from ..langchain_integration import langchain_manager
from .prompts import INTERVIEW_SYSTEM_PROMPT, INTERVIEW_CONTENT_PROMPT, EDUCATIONAL_SYSTEM_PROMPT, EDUCATIONAL_CONTENT_PROMPT

class SimplePodcastProcessor:
    """Simple processor for generating podcast scripts and audio"""
    
    def __init__(self):
        # Ensure podcast directory exists
        settings.podcast_storage_path.mkdir(parents=True, exist_ok=True)
    
    def generate_podcast(self, 
                        content_chunks: List[Dict[str, Any]], 
                        style: str = "interview",
                        topic: str = "PDF Analysis") -> Dict[str, Any]:
        """Generate podcast script from PDF content"""
        
        try:
            combined_content = ""
            for chunk in content_chunks[:5]:  
                combined_content += f"{chunk['content']}\n\n"
            
            if style.lower() == "interview":
                system_prompt = INTERVIEW_SYSTEM_PROMPT
                user_prompt = INTERVIEW_CONTENT_PROMPT.format(
                    content=combined_content,
                    duration=15
                )
            elif style.lower() == "educational":
                system_prompt = EDUCATIONAL_SYSTEM_PROMPT
                user_prompt = EDUCATIONAL_CONTENT_PROMPT.format(
                    content=combined_content,
                    duration=15
                )
            else:
                raise ValueError(f"Unsupported style: {style}")
            
            script = langchain_manager.generate_response(system_prompt, user_prompt)
            
            return {
                "success": True,
                "script": script,
                "topic": topic,
                "style": style,
                "chunks_used": len(content_chunks[:5])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_audio(self, script: str, filename: str) -> Dict[str, Any]:
        """Generate audio from script using gTTS"""
        
        if not AUDIO_AVAILABLE:
            return {
                "success": False,
                "message": "Audio generation not available. Install gtts: pip install gtts"
            }
        
        try:
            clean_script = self._clean_script_for_audio(script)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"{filename}_{timestamp}.mp3"
            audio_path = settings.podcast_storage_path / audio_filename
            
            tts = gTTS(text=clean_script, lang='en', slow=False)
            tts.save(str(audio_path))
            
            return {
                "success": True,
                "audio_path": str(audio_path),
                "filename": audio_filename
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _clean_script_for_audio(self, script: str) -> str:
        """Clean script for better audio generation"""
        lines = script.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove speaker labels (Host:, Expert:, Narrator:)
            if ':' in line and any(label in line for label in ['Host:', 'Expert:', 'Narrator:']):
                content = line.split(':', 1)[1].strip()
                if content:
                    cleaned_lines.append(content)
            else:
                cleaned_lines.append(line)
        
        return ' '.join(cleaned_lines)
    
    def save_podcast_files(self, script: str, audio_path: str, topic: str, style: str) -> Dict[str, Any]:
        """Save podcast script and return file paths"""
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            script_filename = f"podcast_{style}_{timestamp}.txt"
            script_path = settings.podcast_storage_path / script_filename
            
            # Save script
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(f"Topic: {topic}\n")
                f.write(f"Style: {style}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write("-" * 50 + "\n\n")
                f.write(script)
            
            return {
                "success": True,
                "script_path": str(script_path),
                "audio_path": audio_path,
                "message": f"Podcast saved successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
