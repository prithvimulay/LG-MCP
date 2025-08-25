#!/usr/bin/env python3
"""
Test script to verify LangSmith setup and configuration
"""
import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_langsmith_setup():
    """Test LangSmith configuration and setup"""
    print("🔧 Testing LangSmith Setup...")
    
    try:
        # Test settings import
        from pdf_mcp.config.settings import settings
        print("✅ Settings imported successfully")
        
        # Print LangSmith configuration
        print(f"\n📊 LangSmith Configuration:")
        print(f"  • Tracing Enabled: {settings.langsmith_tracing}")
        print(f"  • Project: {settings.langsmith_project}")
        print(f"  • Endpoint: {settings.langsmith_endpoint}")
        print(f"  • API Key Available: {bool(settings.langsmith_api_key)}")
        
        if settings.langsmith_api_key:
            print(f"  • API Key Preview: {settings.langsmith_api_key[:10]}...")
        
        # Test LangSmith import
        try:
            from langsmith import traceable
            print("✅ LangSmith library imported successfully")
            
            # Test environment variables setup
            if settings.langsmith_tracing and settings.langsmith_api_key:
                os.environ["LANGCHAIN_TRACING_V2"] = "true"
                os.environ["LANGCHAIN_ENDPOINT"] = settings.langsmith_endpoint
                os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
                os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
                print("✅ Environment variables set successfully")
                print("✅ LangSmith tracing configured and ready")
            else:
                print("ℹ️  LangSmith tracing is disabled or API key not provided")
        
        except ImportError as e:
            print(f"❌ LangSmith import failed: {e}")
        
        # Test graph builder import
        try:
            from pdf_mcp.langgraph.graph_builder import langsmith_client
            print("✅ Graph builder with LangSmith imported successfully")
            
            if langsmith_client:
                print("✅ LangSmith client is initialized in graph builder")
            else:
                print("ℹ️  LangSmith client is None (tracing disabled)")
                
        except Exception as e:
            print(f"❌ Graph builder import failed: {e}")
        
        print("\n🎉 LangSmith setup test completed!")
        
    except Exception as e:
        print(f"❌ Error during LangSmith setup test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_langsmith_setup())
