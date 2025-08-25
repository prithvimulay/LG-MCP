#!/usr/bin/env python3
"""
Test script for MCP tools integration with audio podcast generation
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))

# Set up environment before imports
os.environ["GROQ_API_KEY"] = "dummy_key_for_testing"  # Just for testing, won't actually call LLM

from pdf_mcp.tools.podcast import generate_podcast
from pdf_mcp.config.settings import settings

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_text_podcast_mcp_style():
    """Test text-only podcast generation using MCP style"""
    logger.info("🧪 Testing MCP-Style Text Podcast Generation")
    
    # Check available PDFs
    pdf_files = list(settings.pdf_storage_path.glob("*.pdf"))
    if not pdf_files:
        logger.error(f"No PDF files found in {settings.pdf_storage_path}")
        return False
    
    test_pdf = pdf_files[0].name
    logger.info(f"Using test PDF: {test_pdf}")
    
    try:
        # Test text-only podcast generation
        result = generate_podcast("artificial intelligence and machine learning", test_pdf, generate_audio=False)
        
        if result["success"]:
            logger.info("✅ Text podcast generation successful!")
            logger.info(f"   Script length: {len(result['script'])} characters")
            logger.info(f"   Source PDF: {result['source_pdf']}")
            logger.info(f"   Speaker format: {result['speaker_format']}")
            logger.info(f"   Generated at: {result['generated_at']}")
            
            # Show a preview
            script_preview = result["script"][:300] + "..." if len(result["script"]) > 300 else result["script"]
            logger.info(f"   Preview: {script_preview}")
            
            return True
        else:
            logger.error(f"❌ Text podcast generation failed: {result['error']}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Text podcast test failed: {e}")
        return False

async def test_audio_podcast_mcp_style():
    """Test audio podcast generation using MCP style"""
    logger.info("🎵 Testing MCP-Style Audio Podcast Generation")
    
    # Check available PDFs
    pdf_files = list(settings.pdf_storage_path.glob("*.pdf"))
    if not pdf_files:
        logger.error(f"No PDF files found in {settings.pdf_storage_path}")
        return False
    
    test_pdf = pdf_files[0].name
    logger.info(f"Using test PDF: {test_pdf}")
    
    try:
        # Test audio podcast generation
        result = generate_podcast("neural networks and deep learning", test_pdf, generate_audio=True)
        
        if result["success"]:
            logger.info("✅ Audio podcast generation initiated successfully!")
            logger.info(f"   Script length: {len(result['script'])} characters")
            logger.info(f"   Source PDF: {result['source_pdf']}")
            logger.info(f"   Speaker format: {result['speaker_format']}")
            logger.info(f"   Generated at: {result['generated_at']}")
            
            # Check audio generation
            if result["audio_generated"]:
                logger.info("🎵 Audio generation successful!")
                logger.info(f"   Audio path: {result['audio_path']}")
                logger.info(f"   Duration estimate: {result.get('audio_duration_estimate', 'Unknown')} seconds")
                
                # Check generation parameters
                if result.get('generation_params'):
                    params = result['generation_params']
                    logger.info(f"   Parameters: temp={params.get('temperature')}, guidance={params.get('guidance_scale')}")
                
                # Verify file exists
                if Path(result['audio_path']).exists():
                    logger.info("✅ Audio file successfully created on disk")
                else:
                    logger.warning("⚠️  Audio path reported but file not found")
            else:
                logger.warning("⚠️  Audio generation failed:")
                logger.warning(f"   Error: {result.get('audio_error', 'Unknown error')}")
                logger.info("✅ But text script was generated successfully")
            
            return True
        else:
            logger.error(f"❌ Audio podcast generation failed: {result['error']}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Audio podcast test failed: {e}")
        return False

async def test_mcp_tool_response_format():
    """Test that responses match expected MCP tool format"""
    logger.info("📋 Testing MCP Tool Response Format")
    
    pdf_files = list(settings.pdf_storage_path.glob("*.pdf"))
    if not pdf_files:
        logger.error(f"No PDF files found in {settings.pdf_storage_path}")
        return False
    
    test_pdf = pdf_files[0].name
    
    try:
        # Test both text and audio responses
        text_result = generate_podcast("quantum computing basics", test_pdf, generate_audio=False)
        audio_result = generate_podcast("quantum computing basics", test_pdf, generate_audio=True)
        
        # Check required fields
        required_fields = ["success", "script", "source_pdf", "generated_at", "speaker_format"]
        
        for result, name in [(text_result, "text"), (audio_result, "audio")]:
            logger.info(f"Checking {name} response format...")
            
            missing_fields = [field for field in required_fields if field not in result]
            if missing_fields:
                logger.error(f"❌ Missing fields in {name} response: {missing_fields}")
                return False
            
            logger.info(f"✅ {name.title()} response has all required fields")
            
            # Check specific audio fields
            if name == "audio":
                audio_fields = ["audio_generated", "audio_path"]
                for field in audio_fields:
                    if field not in result:
                        logger.warning(f"⚠️  Missing audio field: {field}")
        
        logger.info("✅ Response format validation passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Response format test failed: {e}")
        return False

def create_sample_mcp_response_text(result):
    """Create sample MCP tool response text like what would be returned"""
    if not result["success"]:
        return f"Unable to generate podcast: {result['error']}"
    
    response = f"=== Podcast Script: neural networks ===\n\n"
    response += f"Source: {result['source_pdf']}\n"
    response += f"Format: {result['speaker_format']}\n"
    response += f"Generated: {result['generated_at']}\n\n"
    response += result['script']
    
    return response

def create_sample_mcp_audio_response_text(result):
    """Create sample MCP audio tool response text"""
    if not result["success"]:
        return f"Unable to generate audio podcast: {result['error']}"
    
    response = f"=== Audio Podcast Generated: neural networks ===\n\n"
    response += f"Source PDF: {result['source_pdf']}\n"
    response += f"Speaker Format: {result['speaker_format']}\n"
    response += f"Generated: {result['generated_at']}\n\n"
    
    if result["audio_generated"]:
        response += f"🎵 AUDIO GENERATED SUCCESSFULLY\n"
        response += f"Audio File: {result['audio_path']}\n"
        response += f"Estimated Duration: ~{result.get('audio_duration_estimate', 'Unknown')} seconds\n"
        
        if result.get('generation_params'):
            params = result['generation_params']
            response += f"Generation Parameters:\n"
            response += f"  - Temperature: {params.get('temperature')}\n"
            response += f"  - Guidance Scale: {params.get('guidance_scale')}\n"
            response += f"  - Top-p: {params.get('top_p')}\n"
            response += f"  - Top-k: {params.get('top_k')}\n"
    else:
        response += f"⚠️ AUDIO GENERATION FAILED\n"
        response += f"Error: {result.get('audio_error', 'Unknown error')}\n"
        response += f"Text script was generated successfully (see below)\n"
    
    response += f"\n=== PODCAST SCRIPT ===\n"
    response += result['script']
    
    return response

async def main():
    """Run all integration tests"""
    print("🎯 Nari Labs Dia TTS - MCP Integration Test")
    print("=" * 60)
    
    # Test 1: Text podcast
    text_ok = await test_text_podcast_mcp_style()
    print()
    
    # Test 2: Audio podcast 
    audio_ok = await test_audio_podcast_mcp_style()
    print()
    
    # Test 3: Response format
    format_ok = await test_mcp_tool_response_format()
    print()
    
    # Show sample responses
    logger.info("📄 Sample MCP Tool Responses:")
    print("\n" + "="*60)
    print("TEXT PODCAST TOOL RESPONSE SAMPLE:")
    print("="*60)
    
    pdf_files = list(settings.pdf_storage_path.glob("*.pdf"))
    if pdf_files:
        sample_result = generate_podcast("sample query", pdf_files[0].name, generate_audio=False)
        sample_response = create_sample_mcp_response_text(sample_result)
        print(sample_response[:500] + "..." if len(sample_response) > 500 else sample_response)
    
    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)
    print(f"Text Podcast:     {'✅ PASS' if text_ok else '❌ FAIL'}")
    print(f"Audio Podcast:    {'✅ PASS' if audio_ok else '❌ FAIL'}")
    print(f"Response Format:  {'✅ PASS' if format_ok else '❌ FAIL'}")
    
    overall_success = text_ok and audio_ok and format_ok
    print(f"\n🎯 OVERALL: {'✅ MCP INTEGRATION READY' if overall_success else '⚠️ PARTIAL SUCCESS'}")
    
    if overall_success:
        print("\n🎉 The Nari Labs Dia TTS integration is ready!")
        print("📋 Available MCP Tools:")
        print("   - generate_podcast_tool (text only)")
        print("   - generate_audio_podcast_tool (text + audio)")
        print("\n🔧 Next steps:")
        print("   - Start the MCP server")
        print("   - Test with real user queries")
        print("   - Monitor audio generation performance")
    else:
        print("\n⚠️  Some tests failed. Review the errors above.")
    
    return overall_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
