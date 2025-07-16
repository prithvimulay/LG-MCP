from fastmcp import FastMCP
import mcp.types as types
from typing import Dict, List, Optional, Any
from pdf_mcp.tools.retrieval import retrieve_from_pdf
from pdf_mcp.tools.podcast import generate_podcast
from pdf_mcp.pdf.manager import PDFManager

# Define available prompts using types.Prompt
PROMPTS = {
    "summarize-pdf": types.Prompt(
        name="summarize-pdf",
        description="Generate a comprehensive summary of PDF content",
        arguments=[
            types.PromptArgument(
                name="pdf_path",
                description="Path to the PDF file or filename to summarize",
                required=True
            )
        ],
    ),
    "extract-key-points": types.Prompt(
        name="extract-key-points",
        description="Extract the most important key points from a PDF document",
        arguments=[
            types.PromptArgument(
                name="pdf_path",
                description="Path to the PDF file or filename to analyze",
                required=True
            ),
            types.PromptArgument(
                name="topic",
                description="Optional specific topic to focus on when extracting key points",
                required=False
            )
        ],
    ),
    "analyze-document-structure": types.Prompt(
        name="analyze-document-structure",
        description="Analyze a PDF document's structure and organization",
        arguments=[
            types.PromptArgument(
                name="pdf_path",
                description="Path to the PDF file or filename to analyze",
                required=True
            )
        ],
    ),
    "generate-podcast": types.Prompt(
        name="generate-podcast",
        description="Create a 2-person podcast script based on PDF content",
        arguments=[
            types.PromptArgument(
                name="pdf_path",
                description="Path to the PDF file or filename to use as source",
                required=True
            ),
            types.PromptArgument(
                name="topic",
                description="Topic or theme for the podcast discussion",
                required=True
            )
        ],
    )
}

def register_prompts(server: FastMCP):
    """Register all prompts with the MCP server"""
    
    @server.list_prompts()
    async def list_prompts() -> list[types.Prompt]:
        """Return the list of available prompts"""
        return list(PROMPTS.values())
    
    @server.get_prompt()
    async def get_prompt(
        name: str, arguments: dict[str, str] | None = None
    ) -> types.GetPromptResult:
        """Get prompt details and generated messages"""
        if name not in PROMPTS:
            raise ValueError(f"Prompt not found: {name}")
            
        # Handle different prompts
        if name == "summarize-pdf":
            pdf_path = arguments.get("pdf_path") if arguments else ""
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"Generate a comprehensive summary that captures the main points, "
                                 f"key findings, and important conclusions from the PDF: {pdf_path}. "
                                 f"Structure the summary with clear sections and bullet points where appropriate."
                        )
                    )
                ]
            )
            
        elif name == "extract-key-points":
            pdf_path = arguments.get("pdf_path") if arguments else ""
            topic = arguments.get("topic", "") if arguments else ""
            topic_focus = f" related to {topic}" if topic else ""
            
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"Extract the 5-7 most important key points from the PDF: {pdf_path}{topic_focus}. "
                                 f"Format the response as a bulleted list with brief explanations for each point."
                        )
                    )
                ]
            )
            
        elif name == "analyze-document-structure":
            pdf_path = arguments.get("pdf_path") if arguments else ""
            
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"Analyze the document structure of the PDF: {pdf_path} in detail. Identify: \n"
                                 f"1. The major sections and their hierarchy\n"
                                 f"2. How information is organized (chronologically, topically, etc.)\n"
                                 f"3. The document's formatting patterns and consistency\n"
                                 f"4. Key structural elements (abstracts, executive summaries, appendices, etc.)\n"
                                 f"5. Navigation aids present in the document (TOC, index, etc.)\n\n"
                                 f"Present your analysis in a structured format with clear headings and explanations."
                        )
                    )
                ]
            )
            
        elif name == "generate-podcast":
            pdf_path = arguments.get("pdf_path") if arguments else ""
            topic = arguments.get("topic", "the document") if arguments else "the document"
            
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"Create a natural, engaging 2-person podcast script about {topic} "
                                 f"based on content from the PDF: {pdf_path}.\n\n"
                                 f"Format it as a conversation between a Host and an Expert with:\n"
                                 f"1. A brief introduction by the Host\n"
                                 f"2. Discussion of 3-5 key points from the document\n"
                                 f"3. Expert explaining concepts in an accessible way\n" 
                                 f"4. Host asking thoughtful follow-up questions\n"
                                 f"5. A concise conclusion summarizing main takeaways\n\n"
                                 f"Make the conversation sound natural and engaging, not scripted."
                        )
                    )
                ]
            )
        
        # Default error case
        raise ValueError("Prompt implementation not found")
    
    # Legacy function-based prompts for backward compatibility
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
        return retrieve_from_pdf('Generate a comprehensive summary that captures the main points, key findings, and important conclusions of this document. Structure the summary with clear sections and bullet points where appropriate.', pdf_path)
    
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
        query = f"Extract the 5-7 most important key points from this document{' related to ' + topic if topic else ''}." \
               f"Format the response as a bulleted list with brief explanations for each point."
        return retrieve_from_pdf(query, pdf_path)
        
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
        return generate_podcast(topic, pdf_path)
