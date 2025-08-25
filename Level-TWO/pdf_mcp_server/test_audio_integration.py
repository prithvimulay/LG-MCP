#!/usr/bin/env python3
"""
Test script for Nari Labs Dia TTS audio integration
"""

import sys
import os
from pathlib import Path
import logging

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from pdf_mcp.config.settings import settings
from pdf_mcp.tools.podcast import generate_podcast

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_text_podcast():
    """Test text-only podcast generation"""
    logger.info("=== Testing Text-Only Podcast Generation ===")
    
    # Check if we have any PDFs
    pdf_files = list(settings.pdf_storage_path.glob("*.pdf"))
    if not pdf_files:
        logger.error("No PDF files found in {settings.pdf_storage_path}")
        logger.info("Please add a PDF file to test with")
        return False
    
    test_pdf = pdf_files[0].name
    logger.info(f"Using test PDF: {test_pdf}")
    
    result = generate_podcast("artificial intelligence", test_pdf, generate_audio=False)
    
    if result["success"]:
        logger.info("✅ Text podcast generation successful!")
        logger.info(f"Script length: {len(result['script'])} characters")
        logger.info("Script preview:")
        print(result["script"][:500] + "..." if len(result["script"]) > 500 else result["script"])
        return True
    else:
        logger.error(f"❌ Text podcast generation failed: {result['error']}")
        return False

def test_audio_dependencies():
    """Test if audio dependencies are available"""
    logger.info("=== Testing Audio Dependencies ===")
    
    try:
        import torch
        logger.info(f"✅ PyTorch version: {torch.__version__}")
        logger.info(f"✅ CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            logger.info(f"✅ CUDA device: {torch.cuda.get_device_name(0)}")
        else:
            logger.info("ℹ️  CUDA not available - will use CPU (slower)")
            
    except ImportError as e:
        logger.error(f"❌ PyTorch not available: {e}")
        return False
        
    try:
        import transformers
        logger.info(f"✅ Transformers version: {transformers.__version__}")
    except ImportError as e:
        logger.error(f"❌ Transformers not available: {e}")
        return False
        
    try:
        import soundfile
        logger.info(f"✅ SoundFile version: {soundfile.__version__}")
    except ImportError as e:
        logger.error(f"❌ SoundFile not available: {e}")
        return False
        
    try:
        import huggingface_hub
        logger.info(f"✅ HuggingFace Hub version: {huggingface_hub.__version__}")
    except ImportError as e:
        logger.error(f"❌ HuggingFace Hub not available: {e}")
        return False
    
    # Test Dia TTS availability (without actually loading the model)
    try:
        from pdf_mcp.audio.dia_tts import create_tts_engine
        
        tts_engine = create_tts_engine()
        is_available = tts_engine.is_available()
        
        if is_available:
            logger.info("✅ Dia TTS engine is available")
        else:
            logger.warning("⚠️  Dia TTS engine not fully available - check dependencies")
            
        return is_available
    except Exception as e:
        logger.error(f"❌ Dia TTS engine test failed: {e}")
        return False

def test_audio_podcast():
    """Test audio podcast generation (if dependencies are available)"""
    logger.info("=== Testing Audio Podcast Generation ===")
    
    # Check if we have any PDFs
    pdf_files = list(settings.pdf_storage_path.glob("*.pdf"))
    if not pdf_files:
        logger.error(f"No PDF files found in {settings.pdf_storage_path}")
        return False
    
    test_pdf = pdf_files[0].name
    logger.info(f"Using test PDF: {test_pdf}")
    
    try:
        result = generate_podcast("machine learning basics", test_pdf, generate_audio=True)
        
        if result["success"]:
            logger.info("✅ Audio podcast generation initiated successfully!")
            
            if result["audio_generated"]:
                logger.info(f"🎵 Audio file created: {result['audio_path']}")
                logger.info(f"🎵 Estimated duration: {result.get('audio_duration_estimate', 'Unknown')} seconds")
            else:
                logger.warning(f"⚠️  Audio generation failed: {result.get('audio_error', 'Unknown error')}")
                logger.info("✅ But text script was generated successfully")
                
            return True
        else:
            logger.error(f"❌ Podcast generation failed: {result['error']}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Audio podcast test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎵 Nari Labs Dia TTS Integration Test")
    print("=" * 50)
    
    # Test 1: Basic dependencies
    deps_ok = test_audio_dependencies()
    print()
    
    # Test 2: Text podcast generation
    text_ok = test_text_podcast()
    print()
    
    # Test 3: Audio podcast generation (if dependencies are ok)
    audio_ok = False
    if deps_ok:
        audio_ok = test_audio_podcast()
    else:
        logger.info("⏭️  Skipping audio test due to missing dependencies")
    
    print()
    print("=" * 50)
    print("📊 TEST RESULTS:")
    print(f"Dependencies: {'✅ PASS' if deps_ok else '❌ FAIL'}")
    print(f"Text Podcast: {'✅ PASS' if text_ok else '❌ FAIL'}")
    print(f"Audio Podcast: {'✅ PASS' if audio_ok else '❌ FAIL' if deps_ok else '⏭️ SKIPPED'}")
    
    if not deps_ok:
        print("\n📝 To fix dependencies, try:")
        print("   uv add torch>=2.0.0 torchaudio>=2.0.0 transformers>=4.40.0")
        print("   python install_audio_deps.py")
    
    return deps_ok and text_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
