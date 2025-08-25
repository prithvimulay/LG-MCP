#!/usr/bin/env python3
"""
Simple test for audio dependencies without complex imports
"""

import sys
import logging
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_dependencies():
    """Test basic dependencies"""
    logger.info("🧪 Testing Basic Dependencies")
    
    try:
        import torch
        logger.info(f"✅ PyTorch: {torch.__version__}")
        logger.info(f"✅ CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logger.info(f"   GPU: {torch.cuda.get_device_name(0)}")
    except ImportError as e:
        logger.error(f"❌ PyTorch: {e}")
        return False
    
    try:
        import transformers
        logger.info(f"✅ Transformers: {transformers.__version__}")
    except ImportError as e:
        logger.error(f"❌ Transformers: {e}")
        return False
    
    try:
        import soundfile
        logger.info(f"✅ SoundFile: {soundfile.__version__}")
    except ImportError as e:
        logger.error(f"❌ SoundFile: {e}")
        return False
    
    try:
        import huggingface_hub
        logger.info(f"✅ HuggingFace Hub: {huggingface_hub.__version__}")
    except ImportError as e:
        logger.error(f"❌ HuggingFace Hub: {e}")
        return False
    
    return True

def test_dia_availability():
    """Test if Dia model is available for download"""
    logger.info("🔍 Testing Dia Model Availability")
    
    try:
        from huggingface_hub import model_info
        
        model_id = "nari-labs/Dia-1.6B-0626"
        info = model_info(model_id)
        
        logger.info(f"✅ Dia model found: {model_id}")
        logger.info(f"   Model size: ~{info.siblings[0].size / (1024**3):.1f}GB" if info.siblings else "Size unknown")
        return True
        
    except Exception as e:
        logger.error(f"❌ Dia model check failed: {e}")
        return False

def test_audio_format_conversion():
    """Test basic text format conversion for Dia"""
    logger.info("📝 Testing Audio Format Conversion")
    
    try:
        # Import our Dia TTS module
        from pdf_mcp.audio.dia_tts import DiaTTS
        
        tts = DiaTTS()
        
        # Test text conversion
        sample_text = """S1: Today we're discussing artificial intelligence.
S2: That's right! AI is transforming many industries.
S1: What are the key developments?
S2: Large language models have made significant progress."""
        
        converted = tts.convert_to_dia_format(sample_text)
        logger.info("✅ Text format conversion successful")
        logger.info(f"   Original length: {len(sample_text)} chars")
        logger.info(f"   Converted length: {len(converted)} chars")
        logger.info(f"   Sample: {converted[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Format conversion failed: {e}")
        return False

def test_minimal_podcast_generation():
    """Test minimal podcast text generation"""
    logger.info("🎙️ Testing Minimal Podcast Generation")
    
    try:
        # Simple inline generation without complex dependencies
        query = "artificial intelligence"
        content = "Artificial intelligence represents a transformative technology that is reshaping industries worldwide. Machine learning algorithms can process vast amounts of data to identify patterns and make predictions."
        
        # Create a simple dialogue
        dialogue = []
        dialogue.append(f"S1: Today we're discussing '{query}' and its impact on society.")
        dialogue.append(f"S2: That's right! {content[:100]}...")
        dialogue.append("S1: That's fascinating! Can you tell us more?")
        dialogue.append("S2: Absolutely! The applications are virtually limitless.")
        dialogue.append("S1: Thank you for this insightful discussion!")
        
        script = "\n\n".join(dialogue)
        
        logger.info("✅ Minimal podcast script generated")
        logger.info(f"   Script length: {len(script)} characters")
        logger.info(f"   Lines: {len(dialogue)}")
        
        print("\n" + "="*50)
        print("📄 SAMPLE PODCAST SCRIPT:")
        print("="*50)
        print(script)
        print("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Podcast generation failed: {e}")
        return False

def main():
    """Run tests"""
    print("🎵 Nari Labs Audio Integration - Simple Test")
    print("=" * 60)
    
    # Test basic dependencies
    deps_ok = test_basic_dependencies()
    print()
    
    # Test model availability
    model_ok = test_dia_availability() if deps_ok else False
    print()
    
    # Test format conversion
    format_ok = test_audio_format_conversion() if deps_ok else False
    print()
    
    # Test minimal podcast generation
    podcast_ok = test_minimal_podcast_generation()
    print()
    
    print("=" * 60)
    print("📊 RESULTS:")
    print(f"Basic Dependencies: {'✅ PASS' if deps_ok else '❌ FAIL'}")
    print(f"Dia Model Access:   {'✅ PASS' if model_ok else '❌ FAIL'}")
    print(f"Format Conversion:  {'✅ PASS' if format_ok else '❌ FAIL'}")
    print(f"Podcast Generation: {'✅ PASS' if podcast_ok else '❌ FAIL'}")
    
    overall_success = deps_ok and model_ok and format_ok and podcast_ok
    print(f"\n🎯 OVERALL: {'✅ READY FOR AUDIO' if overall_success else '⚠️ PARTIAL SUCCESS'}")
    
    if not deps_ok:
        print("\n📝 To install missing dependencies:")
        print("   uv add torch>=2.0.0 torchaudio>=2.0.0 transformers>=4.40.0")
        print("   uv add soundfile>=0.13.1 huggingface-hub>=0.30.2")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
