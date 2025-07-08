#!/usr/bin/env python3
"""
Verify that MCP tools are properly registered
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def verify_server_setup():
    """Verify the server and tools are properly set up"""
    
    print("🔍 Verifying MCP Server Setup")
    print("=" * 40)
    
    try:
        # Import the server
        from pdf_mcp.server import mcp
        print("✅ Server imported successfully")
        
        # Check if tools are registered
        if hasattr(mcp, '_tools') and mcp._tools:
            print(f"✅ Found {len(mcp._tools)} registered tools:")
            for tool_name in mcp._tools.keys():
                print(f"   📝 {tool_name}")
        else:
            print("⚠️ No tools found - checking registration...")
            
        # Test direct tool import
        from pdf_mcp.tools.pdf_tools import register_tools
        print("✅ Tool registration function imported")
        
        # Check PDF manager
        from pdf_mcp.pdf.manager import PDFManager
        pdf_manager = PDFManager()
        print("✅ PDF Manager initialized")
        
        # Check data directory
        from pdf_mcp.config.settings import settings
        print(f"📁 PDF Storage Path: {settings.pdf_storage_path}")
        print(f"   Exists: {settings.pdf_storage_path.exists()}")
        
        if settings.pdf_storage_path.exists():
            pdf_files = list(settings.pdf_storage_path.glob("*.pdf"))
            print(f"   PDF files found: {len(pdf_files)}")
            for pdf_file in pdf_files:
                print(f"     📄 {pdf_file.name}")
        
        print("\n🎯 Next Steps:")
        print("1. Open Claude Desktop (not web version)")
        print("2. Restart Claude Desktop completely")
        print("3. Ask: 'What tools do you have available?'")
        print("4. Try: 'Please upload PDFs' or 'upload_pdfs()'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verify_server_setup()
