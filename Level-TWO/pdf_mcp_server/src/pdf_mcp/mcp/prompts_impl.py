from fastmcp import FastMCP
from typing import Optional
from pdf_mcp.tools.retrieval import retrieve_from_pdf
from pdf_mcp.tools.podcast import generate_podcast

def register_prompts(server: FastMCP):
    """Register all prompts with the MCP server using the decorator approach"""
    
    @server.prompt
    def summarize_pdf(pdf_path: str) -> str:
        """Generates a comprehensive summary of the PDF content.
        
        This prompt analyzes the entire PDF document and creates a structured summary
        that captures the main points, key findings, and important conclusions.
        The summary is concise yet thorough, making it ideal for quickly understanding
        the document's content without reading the full text.
        
        Args:
            pdf_path: Path to the PDF file or filename to summarize
            
        Returns:
            A well-structured summary of the PDF content with key points highlighted
        """
        try:
            query = 'Generate a comprehensive summary that captures the main points, key findings, and important conclusions of this document. Structure the summary with clear sections and bullet points where appropriate.'
            return retrieve_from_pdf(query, pdf_path)
        except Exception as e:
            return f"Error: {str(e)}"

    @server.prompt
    def extract_key_points(pdf_path: str, topic: Optional[str] = None) -> str:
        """Extracts the most important key points from a PDF document.
        
        This prompt identifies and extracts the most significant information from the PDF,
        focusing on actionable insights, critical data points, and essential takeaways.
        If a specific topic is provided, the extraction will focus on points related to that topic.
        
        Args:
            pdf_path: Path to the PDF file or filename to analyze
            topic: Optional specific topic to focus on when extracting key points
            
        Returns:
            A bulleted list of key points extracted from the document
        """
        try:
            query = f"Extract the 5-7 most important key points from this document{' related to ' + topic if topic else ''}." \
                   f"Format the response as a bulleted list with brief explanations for each point."
            return retrieve_from_pdf(query, pdf_path)
        except Exception as e:
            return f"Error: {str(e)}"
        
    @server.prompt
    def analyze_document_structure(pdf_path: str) -> str:
        """Performs an in-depth analysis of a PDF document's structure and organization.
        
        This advanced prompt examines the PDF's organization, sectioning, headings, 
        formatting patterns, and overall document architecture. It identifies the 
        document's structural components and provides insights into how information 
        is organized and presented throughout the document.
        
        The analysis is particularly useful for understanding complex technical documents,
        research papers, legal documents, or any PDF with sophisticated organization.
        
        Args:
            pdf_path: Path to the PDF file or filename to analyze
            
        Returns:
            A detailed analysis of the document's structure including sections, headings,
            information hierarchy, and organizational patterns
        """
        try:
            structured_analysis_query = (
                "Analyze this document's structure and organization in detail. Identify: \n"
                "1. The major sections and their hierarchy\n"
                "2. How information is organized (chronologically, topically, etc.)\n"
                "3. The document's formatting patterns and consistency\n"
                "4. Key structural elements (abstracts, executive summaries, appendices, etc.)\n"
                "5. Navigation aids present in the document (TOC, index, etc.)\n\n"
                "Present your analysis in a structured format with clear headings and explanations."
            )
            return retrieve_from_pdf(structured_analysis_query, pdf_path)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @server.prompt
    def generate_podcast_script(pdf_path: str, topic: str) -> str:
        """Creates a conversational 2-person podcast script based on PDF content.
        
        This prompt transforms content from a PDF into an engaging podcast script
        formatted as a discussion between a host and an expert. The script includes
        an introduction, structured discussion of key points, and a conclusion.
        
        The conversation is designed to sound natural while accurately conveying
        the important information from the document in an accessible format.
        
        Args:
            pdf_path: Path to the PDF file or filename to use as source material
            topic: Topic or theme for the podcast discussion
            
        Returns:
            A formatted podcast script with dialogue between a host and expert
        """
        try:
            return generate_podcast(topic, pdf_path)
        except Exception as e:
            return f"Error: {str(e)}"