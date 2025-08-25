from pdf_mcp.pdf.processor import PDFProcessor
from pdf_mcp.config.settings import settings
from pathlib import Path
from typing import Dict, Any, Optional
import datetime
import logging

processor = PDFProcessor()
logger = logging.getLogger(__name__)

def generate_podcast(query: str, pdf_filename: str, generate_audio: bool = False) -> Dict[str, Any]:
    """
    Generate a podcast script using S1/S2 speaker tags (compatible with Dia TTS) 
    and optionally convert it to audio.
    
    Args:
        query: Topic for podcast generation
        pdf_filename: PDF file to base content on
        generate_audio: Whether to generate audio file using Dia TTS
        
    Returns:
        Dictionary containing script text, audio path (if generated), and metadata
    """
    pdf_path = settings.pdf_storage_path / pdf_filename
    
    if not pdf_path.exists():
        return {
            "success": False,
            "error": f"PDF not found: {pdf_filename}. Available PDFs are in {settings.pdf_storage_path}",
            "script": None,
            "audio_path": None
        }
    
    try:
        # Extract text from PDF
        text = processor.extract_text(str(pdf_path))
        
        intro = f"🎙️ Welcome to this AI-powered podcast about '{query}'!\n\n"
        
        lines = [line.strip() for line in text.splitlines() if line.strip() and len(line.strip()) > 20]
        
        # Generate dialogue using S1 (Host) and S2 (Expert) tags for Dia compatibility
        dialogue = []
        dialogue.append(f"S1: Today we're discussing '{query}' based on insights from {pdf_filename}.")
        dialogue.append(f"S2: That's right! Let me share some key points from this document.")
        
        # Create more natural dialogue flow with S1/S2 tags
        for i, line in enumerate(lines[:10]):  
            if i % 2 == 0:
                # S2 (Expert) shares content
                content = line[:150].replace('\n', ' ').strip()
                if content.endswith('.'):
                    dialogue.append(f"S2: {content}")
                else:
                    dialogue.append(f"S2: {content}...")
            else:
                # S1 (Host) provides reactions and transitions
                reactions = [
                    "That's fascinating! Can you elaborate on that?",
                    "That's really interesting. What else should our listeners know?",
                    "Great point! How does this connect to the bigger picture?",
                    "This is valuable insight. Tell us more about this."
                ]
                dialogue.append(f"S1: {reactions[i % len(reactions)]}")
        
        dialogue.append(f"S1: Thank you for this insightful discussion about '{query}'!")
        dialogue.append(f"S2: My pleasure! This topic from {pdf_filename} really highlights important concepts.")
        
        # Create the script with S1/S2 format
        podcast_script = intro + "\n\n".join(dialogue)
        
        result = {
            "success": True,
            "script": podcast_script,
            "query": query,
            "source_pdf": pdf_filename,
            "generated_at": datetime.datetime.now().isoformat(),
            "audio_path": None,
            "audio_generated": False,
            "speaker_format": "S1 (Host), S2 (Expert)"
        }
        
        # Generate audio if requested
        if generate_audio:
            try:
                from pdf_mcp.audio.dia_tts import create_tts_engine
                
                tts_engine = create_tts_engine()
                
                if not tts_engine.is_available():
                    result["audio_error"] = "TTS not available. Install required dependencies: pip install torch transformers"
                    logger.warning("Audio generation requested but TTS dependencies not available")
                else:
                    # Create audio filename
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    audio_filename = f"podcast_{query.replace(' ', '_')}_{timestamp}.mp3"
                    audio_path = settings.audio_storage_path / audio_filename
                    
                    # Generate audio - script is already in S1/S2 format
                    logger.info(f"Generating audio for podcast: {query}")
                    audio_result = tts_engine.generate_audio(
                        text=podcast_script,
                        output_path=str(audio_path)
                    )
                    
                    if audio_result["success"]:
                        result["audio_path"] = str(audio_path)
                        result["audio_generated"] = True
                        result["audio_duration_estimate"] = audio_result["audio_duration_estimate"]
                        result["generation_params"] = audio_result["generation_params"]
                        logger.info(f"Audio generated successfully: {audio_path}")
                    else:
                        result["audio_error"] = f"Audio generation failed: {audio_result['error']}"
                        logger.error(f"Audio generation failed: {audio_result['error']}")
                        
            except ImportError as e:
                result["audio_error"] = f"Audio generation unavailable: {str(e)}"
                logger.warning(f"Audio generation failed due to missing dependencies: {e}")
            except Exception as e:
                result["audio_error"] = f"Unexpected audio generation error: {str(e)}"
                logger.error(f"Unexpected error in audio generation: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Podcast generation failed: {str(e)}")
        return {
            "success": False,
            "error": f"Error generating podcast: {str(e)}",
            "script": None,
            "audio_path": None
        }
