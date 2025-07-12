"""
LangGraph-powered PDF query and podcast generation system
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import the ConversationState from models
from src.pdf_mcp.models.session import ConversationState

async def run_graph(query: str, pdf_path: Optional[str] = None) -> str:
    """
    Run the LangGraph with the given query and optional PDF path.
    """
    
    # For now, let's create a simplified version that just calls the tools directly
    # without the full MCP server setup
    
    # Import the tools directly
    from src.pdf_mcp.tools_server import retrieve_from_pdf, generate_podcast, select_relevant_pdf, list_pdfs
    
    try:
        # Simple logic to determine which tool to use based on query
        query_lower = query.lower()
        
        if "list" in query_lower and "pdf" in query_lower:
            # List PDFs
            response = list_pdfs()
        elif "podcast" in query_lower or "generate" in query_lower:
            # Generate podcast
            if not pdf_path:
                # Try to select a relevant PDF first
                pdf_path = select_relevant_pdf(query)
                if pdf_path.startswith("❌"):
                    return pdf_path
            response = generate_podcast(pdf_path)
        elif "select" in query_lower:
            # Select relevant PDF
            response = select_relevant_pdf(query)
        else:
            # Default to retrieve from PDF
            if not pdf_path:
                # Try to select a relevant PDF first
                pdf_path = select_relevant_pdf(query)
                if pdf_path.startswith("❌"):
                    return pdf_path
            response = retrieve_from_pdf(query, pdf_path)
        
        return response
        
    except Exception as e:
        return f"Error running graph: {str(e)}"

def main():
    """Simple synchronous main function for testing"""
    
    # Simple hardcoded test or interactive input
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter your query: ")
    
    print(f"🔍 Processing query: {query}")
    
    # Check if PDFs directory exists and list files
    pdf_dir = Path("data/pdfs")
    if pdf_dir.exists():
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if pdf_files:
            print(f"📚 Found {len(pdf_files)} PDF(s):")
            for pdf in pdf_files:
                print(f"  - {pdf.name}")
            
            # For simplicity, use the first PDF if available
            pdf_path = str(pdf_files[0]) if pdf_files else None
        else:
            print("⚠️ No PDFs found in data/pdfs directory")
            pdf_path = None
    else:
        print("⚠️ data/pdfs directory not found")
        pdf_path = None
    
    try:
        # Run the async function
        result = asyncio.run(run_graph(query, pdf_path))
        print("\n📝 Result:")
        print(result)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
