#!/usr/bin/env python3
"""
Test script to run a query through your PDF MCP system with LangSmith tracing
"""
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_query_with_tracing():
    """Run a test query to generate LangSmith traces"""
    print("🚀 Starting PDF MCP Query Test with LangSmith Tracing...")
    
    try:
        # Import your main function
        from pdf_mcp.langgraph.graph_builder import process_pdf_query_mcp
        from pdf_mcp.config.settings import settings
        
        print(f"📊 LangSmith Configuration:")
        print(f"   • Tracing: {settings.langsmith_tracing}")
        print(f"   • Project: {settings.langsmith_project}")
        print(f"   • Endpoint: {settings.langsmith_endpoint}")
        
        if not settings.langsmith_tracing:
            print("⚠️  Warning: LangSmith tracing is disabled!")
            return
        
        # Test query
        test_query = "List all PDFs"
        print(f"\n🔍 Running test query: '{test_query}'")
        print("=" * 50)
        
        # Run the query (this should generate traces)
        result = await process_pdf_query_mcp(test_query)
        
        print("=" * 50)
        print(f"✅ Query Result: {result}")
        
        print(f"\n📊 Check your traces at:")
        print(f"   🌐 URL: {settings.langsmith_endpoint}")
        print(f"   📁 Project: {settings.langsmith_project}")
        print(f"   🏷️  Look for traces with names:")
        print(f"      - pdf_mcp_main_entry")
        print(f"      - pdf_process_query")
        print(f"      - pdf_agent_node")
        print(f"      - mcp_tool_node (if tools were called)")
        
    except Exception as e:
        print(f"❌ Error during query test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_query_with_tracing())
