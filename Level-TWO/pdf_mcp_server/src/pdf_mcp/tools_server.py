"""
MCP Tool Server for PDF querying and podcast generation
"""

import os
from pathlib import Path
from .pdf.manager import PDFManager
from .pdf.processor import PDFProcessor
from .vector.store import VectorStore
from .podcast.processor import PodcastProcessor

# Initialize components
pdf_manager = PDFManager()
pdf_processor = PDFProcessor()
vector_store = VectorStore()
podcast_processor = PodcastProcessor()

# Simple function decorator since we're not using full MCP server for now
def tool(func):
    return func

@tool
def retrieve_from_pdf(query: str, pdf_path: str) -> str:
    """
    Answer questions about a specific PDF using retrieval-augmented generation.
    
    Args:
        query: The question to ask about the PDF content
        pdf_path: Path to the PDF file to query
    """
    try:
        # Check if PDF exists
        if not os.path.exists(pdf_path):
            return f"❌ PDF not found at {pdf_path}"
        
        # Process PDF to extract text chunks
        pdf_text = pdf_processor.extract_text(pdf_path)
        if not pdf_text:
            return f"❌ Could not extract text from PDF: {pdf_path}"
        
        # Create text chunks
        chunks = pdf_processor.create_chunks(pdf_text)
        
        # Get relevant chunks using vector search
        relevant_chunks = vector_store.similarity_search(query, chunks, k=3)
        
        if not relevant_chunks:
            return "🔍 No relevant information found in the PDF for your question."
        
        # Format the response
        response_parts = [
            f"🎯 **Query Results** (from {Path(pdf_path).name}):\n"
        ]
        
        for i, chunk in enumerate(relevant_chunks, 1):
            response_parts.append(f"**{i}.**")
            response_parts.append(chunk.strip())
            response_parts.append("")  # Empty line
        
        return "\n".join(response_parts)
    
    except Exception as e:
        return f"❌ Error retrieving from PDF: {str(e)}"

@tool
def generate_podcast(pdf_path: str) -> str:
    """
    Generate a 2-person podcast-style conversation based on the PDF content.
    
    Args:
        pdf_path: Path to the PDF file to use as source material
    """
    try:
        # Check if PDF exists
        if not os.path.exists(pdf_path):
            return f"❌ PDF not found at {pdf_path}"
        
        # Process PDF to extract text
        pdf_text = pdf_processor.extract_text(pdf_path)
        if not pdf_text:
            return f"❌ Could not extract text from PDF: {pdf_path}"
        
        # Generate podcast script
        podcast_script = podcast_processor.generate_podcast_script(pdf_text)
        
        # Format response
        response_parts = [
            f"🎙️ **Podcast Generated Successfully!**\n",
            f"📚 **Source:** {Path(pdf_path).name}",
            f"\n📜 **Script:**\n{podcast_script}"
        ]
        
        return "\n".join(response_parts)
    
    except Exception as e:
        return f"❌ Error generating podcast: {str(e)}"

@tool
def select_relevant_pdf(query: str) -> str:
    """
    Select the most relevant PDF for a given query from the available PDFs.
    
    Args:
        query: The query to match against available PDFs
    """
    try:
        # Get all PDFs from the pdfs directory
        pdf_files = pdf_manager.list_pdfs()
        
        if not pdf_files:
            return "📂 No PDFs available. Place PDF files in data/pdfs/ directory."
        
        # Simple implementation - keyword matching on filenames
        keywords = query.lower().split()
        scored_pdfs = []
        
        for pdf_file in pdf_files:
            score = 0
            filename_lower = pdf_file.name.lower()
            
            # Simple keyword matching
            for keyword in keywords:
                if keyword in filename_lower:
                    score += 1
            
            # Add to list with score
            scored_pdfs.append((pdf_file, score))
        
        # Sort by score (highest first)
        scored_pdfs.sort(key=lambda x: x[1], reverse=True)
        
        # Select the highest scoring PDF or default to first if all scores are 0
        if scored_pdfs[0][1] > 0:
            selected_pdf = scored_pdfs[0][0]
        else:
            # If no matches, just use the first PDF
            selected_pdf = pdf_files[0]
        
        # Return the path to the selected PDF
        return str(selected_pdf)
    
    except Exception as e:
        return f"❌ Error selecting relevant PDF: {str(e)}"

@tool
def list_pdfs() -> str:
    """
    List all available PDF files in the data/pdfs directory.
    
    Returns:
        A formatted list of all PDF files
    """
    try:
        pdf_files = pdf_manager.list_pdfs()
        
        if not pdf_files:
            return "📂 No PDFs available. Place PDF files in data/pdfs/ directory."
        
        # Format the response
        response_parts = ["📚 **Available PDFs:**\n"]
        
        for i, pdf_file in enumerate(pdf_files, 1):
            file_info = pdf_manager.get_pdf_info(pdf_file)
            size_mb = file_info["file_size"] / (1024 * 1024)
            response_parts.append(f"**{i}.** {pdf_file.name} ({size_mb:.2f} MB)")
        
        return "\n".join(response_parts)
    
    except Exception as e:
        return f"❌ Error listing PDFs: {str(e)}"

if __name__ == "__main__":
    print("Starting MCP Tool Server...")
    print("Available tools: retrieve_from_pdf, generate_podcast, select_relevant_pdf, list_pdfs")
