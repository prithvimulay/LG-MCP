"""
Nari Labs Dia TTS integration for podcast audio generation.
Handles conversion from dialogue text to audio using the Dia model.
"""

import os
import torch
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from pdf_mcp.config.settings import settings

logger = logging.getLogger(__name__)

class DiaTTS:
    """
    Wrapper for Nari Labs Dia TTS model with lazy loading and error handling.
    """
    
    def __init__(self, model_checkpoint: str = "nari-labs/Dia-1.6B-0626", device: Optional[str] = None):
        self.model_checkpoint = model_checkpoint
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.processor = None
        self._loaded = False
        
        logger.info(f"DiaTTS initialized with device: {self.device}")
    
    def _load_model(self):
        """Lazy load the Dia model and processor."""
        if self._loaded:
            return
            
        try:
            # Import transformers here to handle missing dependency gracefully
            from transformers import AutoProcessor, DiaForConditionalGeneration
            
            logger.info(f"Loading Dia model: {self.model_checkpoint}")
            
            # Load processor
            self.processor = AutoProcessor.from_pretrained(self.model_checkpoint)
            
            # Load model with appropriate precision
            compute_dtype = torch.float16 if self.device == "cuda" else torch.float32
            self.model = DiaForConditionalGeneration.from_pretrained(
                self.model_checkpoint,
                torch_dtype=compute_dtype
            ).to(self.device)
            
            self._loaded = True
            logger.info("Dia model loaded successfully")
            
        except ImportError as e:
            raise ImportError(
                "Transformers library not found. Install with: pip install transformers>=4.40.0"
            ) from e
        except Exception as e:
            logger.error(f"Failed to load Dia model: {str(e)}")
            raise RuntimeError(f"Model loading failed: {str(e)}") from e
    
    def convert_to_dia_format(self, dialogue_text: str) -> str:
        """
        Convert podcast dialogue format to Dia format.
        Since we now generate with S1/S2 tags directly, just add brackets and clean up.
        
        Args:
            dialogue_text: Text with "S1:" and "S2:" prefixes
            
        Returns:
            Text formatted with [S1] and [S2] tags for Dia
        """
        lines = []
        for line in dialogue_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Convert S1:/S2: to [S1]/[S2] format for Dia
            if line.startswith('S1:'):
                content = line.replace('S1:', '').strip()
                lines.append(f'[S1] {content}')
            elif line.startswith('S2:'):
                content = line.replace('S2:', '').strip()
                lines.append(f'[S2] {content}')
            elif line.startswith('🎙️'):
                # Skip intro emoji line
                continue
            elif line.startswith('===') or 'Welcome to this AI-powered podcast' in line:
                # Skip intro lines that aren't part of dialogue
                continue
            else:
                # Default to S1 for any other content (shouldn't happen with new format)
                if line.strip():
                    lines.append(f'[S1] {line}')
        
        # Join with spaces for Dia format (single line preferred)
        formatted_text = ' '.join(lines)
        
        # Validate format requirements
        if not formatted_text.startswith('[S1]'):
            formatted_text = f'[S1] {formatted_text}'
            
        return formatted_text
    
    def generate_audio(
        self, 
        text: str, 
        output_path: str,
        max_new_tokens: int = 3072,
        guidance_scale: float = 3.0,
        temperature: float = 1.8,
        top_p: float = 0.90,
        top_k: int = 45
    ) -> Dict[str, Any]:
        """
        Generate audio from dialogue text.
        
        Args:
            text: Input dialogue text (will be converted to Dia format)
            output_path: Path to save the generated audio file
            max_new_tokens: Maximum tokens to generate
            guidance_scale: CFG guidance scale
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            
        Returns:
            Dictionary with generation results and metadata
        """
        try:
            self._load_model()
            
            # Convert to Dia format
            dia_text = self.convert_to_dia_format(text)
            logger.info(f"Converted text to Dia format: {dia_text[:100]}...")
            
            # Prepare inputs
            inputs = self.processor(
                text=[dia_text], 
                padding=True, 
                return_tensors="pt"
            ).to(self.device)
            
            # Generate audio tokens
            logger.info("Generating audio tokens...")
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    guidance_scale=guidance_scale,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k
                )
            
            # Decode to audio
            logger.info("Decoding to audio...")
            audio_outputs = self.processor.batch_decode(outputs)
            
            # Save audio file
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.processor.save_audio(audio_outputs, str(output_path))
            
            logger.info(f"Audio saved to: {output_path}")
            
            return {
                "success": True,
                "output_path": str(output_path),
                "text_length": len(dia_text),
                "audio_duration_estimate": len(dia_text) // 86,  # ~1 second per 86 tokens
                "generation_params": {
                    "max_new_tokens": max_new_tokens,
                    "guidance_scale": guidance_scale,
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k
                }
            }
            
        except Exception as e:
            logger.error(f"Audio generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "output_path": None
            }
    
    def is_available(self) -> bool:
        """Check if TTS is available (dependencies installed, etc.)."""
        try:
            import transformers
            return torch.cuda.is_available() if self.device == "cuda" else True
        except ImportError:
            return False


def create_tts_engine() -> DiaTTS:
    """Factory function to create TTS engine with default settings."""
    return DiaTTS()
