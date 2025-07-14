from mcp.types import Prompt
from mcp.server import Server
from typing import Dict
from pdf_mcp.tools.retrieval import retrieve_from_pdf
from pdf_mcp.pdf.manager import PDFManager
from langchain_core.messages import HumanMessage
from pdf_mcp.langgraph.graph_runner import run_pipeline

# In-memory prompt registry
PROMPTS: Dict[str, Prompt] = {}

def register_prompts(server):
    @server.prompt
    def summarize_pdf(pdf_path: str) -> str:
        """Summarize the content of a PDF file."""
        return retrieve_from_pdf('summarize', pdf_path)
    
    @server.prompt
    def answer_question(query: str) -> str:
        """Answer a question using the LangGraph pipeline.
        
        This will dynamically select relevant PDFs and retrieve information as needed.
        """
        return run_pipeline(query)
