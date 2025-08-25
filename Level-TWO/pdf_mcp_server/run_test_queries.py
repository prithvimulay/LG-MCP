#!/usr/bin/env python3
"""
Run multiple test queries to generate different trace patterns
"""
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def run_multiple_test_queries():
    """Run multiple test queries to generate various traces"""
    print("🧪 Running Multiple Test Queries with LangSmith Tracing...")
    
    try:
        from pdf_mcp.langgraph.graph_builder import process_pdf_query_mcp
        from pdf_mcp.config.settings import settings
        
        if not settings.langsmith_tracing:
            print("⚠️  Warning: LangSmith tracing is disabled!")
            return
        
        test_queries = [
            "List all PDFs",
            "What is the database status?", 
            "Find a PDF about machine learning",
            "Generate a podcast from a research paper",
            "Search for content about AI in documents"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test {i}/5: '{query}'")
            print("-" * 60)
            
            try:
                result = await process_pdf_query_mcp(query)
                print(f"✅ Result: {result[:100]}{'...' if len(result) > 100 else ''}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Small delay between queries
            await asyncio.sleep(1)
        
        print(f"\n🎉 All tests completed! Check traces at:")
        print(f"   🌐 {settings.langsmith_endpoint}")
        print(f"   📁 Project: {settings.langsmith_project}")
        
    except Exception as e:
        print(f"❌ Error during tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_multiple_test_queries())
