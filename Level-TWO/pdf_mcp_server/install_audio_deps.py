#!/usr/bin/env python3
"""
Installation script for Nari Labs Dia TTS audio dependencies.
Run this to install the required packages for audio podcast generation.
"""

import subprocess
import sys
import platform
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command):
    """Run a command and return success status."""
    try:
        logger.info(f"Running: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logger.info(f"Success: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed: {e.stderr}")
        return False

def install_audio_dependencies():
    """Install audio generation dependencies."""
    logger.info("Installing Nari Labs Dia TTS dependencies...")
    
    # Core dependencies
    dependencies = [
        "torch>=2.0.0",
        "torchaudio>=2.0.0", 
        "transformers>=4.40.0",
        "descript-audio-codec>=1.0.0",
        "soundfile>=0.13.1",
        "huggingface-hub>=0.30.2",
        "safetensors>=0.5.3"
    ]
    
    # Platform-specific dependencies
    system = platform.system().lower()
    if system == "windows":
        dependencies.append("triton-windows==3.2.0.post18")
    elif system == "linux":
        dependencies.append("triton==3.2.0")
    
    # Install dependencies
    install_cmd = [sys.executable, "-m", "pip", "install"] + dependencies
    
    success = run_command(install_cmd)
    
    if success:
        logger.info("✅ Audio dependencies installed successfully!")
        logger.info("You can now use audio podcast generation with Nari Labs Dia TTS.")
        
        # Test installation
        try:
            import torch
            import transformers
            logger.info(f"✅ PyTorch version: {torch.__version__}")
            logger.info(f"✅ Transformers version: {transformers.__version__}")
            logger.info(f"✅ CUDA available: {torch.cuda.is_available()}")
            
            if torch.cuda.is_available():
                logger.info(f"✅ CUDA device: {torch.cuda.get_device_name(0)}")
            else:
                logger.info("ℹ️  CUDA not available - will use CPU (slower)")
                
        except ImportError as e:
            logger.warning(f"⚠️  Import test failed: {e}")
            
    else:
        logger.error("❌ Failed to install audio dependencies")
        logger.error("Please check the error messages above and try again")
        return False
    
    return True

def main():
    """Main installation function."""
    print("🎵 Nari Labs Dia TTS Audio Dependencies Installer")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 10):
        logger.error("❌ Python 3.10+ is required for Nari Labs Dia TTS")
        return False
    
    logger.info(f"✅ Python version: {sys.version}")
    
    # Install dependencies
    success = install_audio_dependencies()
    
    if success:
        print("\n🎉 Installation completed successfully!")
        print("You can now generate audio podcasts using the generate_audio_podcast_tool")
        print("\nExample usage:")
        print("- Use generate_audio_podcast_tool instead of generate_podcast_tool")
        print("- Audio files will be saved to src/data/audio/")
        print("- First run will download the Dia model (~3GB)")
    else:
        print("\n❌ Installation failed. Please check the error messages above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
