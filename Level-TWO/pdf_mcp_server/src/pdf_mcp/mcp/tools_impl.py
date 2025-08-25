from fastmcp import FastMCP
from typing import Annotated
from pydantic import Field
from pdf_mcp.tools.retrieval import retrieve_from_pdf
from pdf_mcp.tools.podcast import generate_podcast
from pdf_mcp.tools.selection import select_relevant_pdf
from pdf_mcp.pdf.manager import PDFManager
from pdf_mcp.vector.store import VectorStore
import logging

logger = logging.getLogger(__name__)

def register_tools(server: FastMCP):
    """Register all tools with the MCP server - ASCII safe version"""

    @server.tool()
    def list_pdfs_tool() -> str:
        """Lists all available PDF documents in the system."""
        try:
            manager = PDFManager()
            pdfs = manager.list_pdfs()
            
            if not pdfs:
                result = "=== No PDF documents found in the storage directory ==="
            else:
                result = f"=== Available PDF Documents ({len(pdfs)} total) ===\n\n"
                for i, pdf in enumerate(pdfs, 1):
                    result += f"   {i}. {pdf.name}\n"
                
                result += f"\n=== Available Operations ===\n"
                result += f"- Search content in any PDF\n"
                result += f"- Generate podcast from PDF content\n"
                result += f"- Check vector database status\n"
            
            logger.info(f"Tool returning: {result}")
            return result
        except Exception as e:
            error_msg = f"Failed to list PDFs: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    @server.tool()
    def db_status_tool() -> str:
        """Provides detailed status of the vector database indexing."""
        try:
            vector_store = VectorStore()
            count = vector_store.collection.count()
            
            if count == 0:
                return "=== Vector Database Status ===\nEmpty - No PDFs have been indexed yet."

            items = vector_store.collection.get()
            pdf_counts = {}
            
            if items and 'metadatas' in items and items['metadatas']:
                for metadata in items['metadatas']:
                    if metadata and 'source' in metadata:
                        source = metadata['source']
                        pdf_counts[source] = pdf_counts.get(source, 0) + 1

            status = f"=== Vector Database Status ===\n\n"
            status += f"Total indexed chunks: {count:,}\n"
            status += f"Indexed documents: {len(pdf_counts)}\n\n"
            
            if pdf_counts:
                status += "=== Document Details ===\n"
                for pdf, chunk_count in sorted(pdf_counts.items()):
                    status += f"- {pdf}: {chunk_count:,} chunks\n"
            
            return status
        except Exception as e:
            logger.error(f"Database status check failed: {e}")
            raise RuntimeError(f"Database status check failed: {str(e)}")

    @server.tool()
    def retrieve_from_pdf_tool(
        query: Annotated[str, Field(description="Search query for PDF content")],
        pdf_filename: Annotated[str, Field(description="PDF filename to search")]
    ) -> str:
        """Retrieves specific information from a PDF document using semantic search."""
        try:
            result = retrieve_from_pdf(query, pdf_filename)
            if not result or result.strip() == "":
                return f"No relevant content found for query '{query}' in {pdf_filename}"
            return result
        except Exception as e:
            logger.error(f"PDF retrieval failed for {pdf_filename}: {e}")
            raise RuntimeError(f"PDF retrieval failed: {str(e)}")

    @server.tool()
    def generate_podcast_tool(
        query: Annotated[str, Field(description="Topic for podcast generation")],
        pdf_filename: Annotated[str, Field(description="PDF file to base content on")]
    ) -> str:
        """Generates a podcast-style dialogue based on PDF content (text only)."""
        try:
            result = generate_podcast(query, pdf_filename, generate_audio=False)
            if not result.get("success") or not result.get("script"):
                error_msg = result.get("error", "Unknown error")
                return f"Unable to generate podcast content for '{query}' from {pdf_filename}: {error_msg}"
            
            # Format response with metadata
            response = f"=== Podcast Script: {query} ===\n\n"
            response += f"Source: {pdf_filename}\n"
            response += f"Format: {result.get('speaker_format', 'S1 (Host), S2 (Expert)')}\n"
            response += f"Generated: {result.get('generated_at', 'Unknown')}\n\n"
            response += result['script']
            
            return response
        except Exception as e:
            logger.error(f"Podcast generation failed: {e}")
            raise RuntimeError(f"Podcast generation failed: {str(e)}")

    @server.tool()
    def generate_audio_podcast_tool(
        query: Annotated[str, Field(description="Topic for audio podcast generation")],
        pdf_filename: Annotated[str, Field(description="PDF file to base content on")]
    ) -> str:
        """Generates a podcast-style dialogue with audio using Nari Labs Dia TTS."""
        try:
            result = generate_podcast(query, pdf_filename, generate_audio=True)
            
            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                return f"Unable to generate podcast for '{query}' from {pdf_filename}: {error_msg}"
            
            # Format response with complete information
            response = f"=== Audio Podcast Generated: {query} ===\n\n"
            response += f"Source PDF: {pdf_filename}\n"
            response += f"Speaker Format: {result.get('speaker_format', 'S1 (Host), S2 (Expert)')}\n"
            response += f"Generated: {result.get('generated_at', 'Unknown')}\n\n"
            
            # Audio generation results
            if result.get("audio_generated"):
                response += f"🎵 AUDIO GENERATED SUCCESSFULLY\n"
                response += f"Audio File: {result.get('audio_path', 'Unknown')}\n"
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
                audio_error = result.get('audio_error', 'Unknown error')
                response += f"Error: {audio_error}\n"
                response += f"Text script was generated successfully (see below)\n"
            
            response += f"\n=== PODCAST SCRIPT ===\n"
            response += result.get('script', 'Script not available')
            
            return response
            
        except Exception as e:
            logger.error(f"Audio podcast generation failed: {e}")
            raise RuntimeError(f"Audio podcast generation failed: {str(e)}")

    @server.tool()
    def select_relevant_pdf_tool(
        query: Annotated[str, Field(description="Query to identify relevant PDF")]
    ) -> str:
        """Identifies the most relevant PDF document based on the query."""
        try:
            result = select_relevant_pdf(query)
            if not result or result == "No PDFs found.":
                return "No PDF documents available for selection"
            return result
        except Exception as e:
            logger.error(f"PDF selection failed: {e}")
            raise RuntimeError(f"PDF selection failed: {str(e)}")

    logger.info("Successfully registered all tools with FastMCP server")
