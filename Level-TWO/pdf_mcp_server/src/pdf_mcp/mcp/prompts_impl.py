from mcp.types import Prompt
from mcp.server import Server
from typing import Dict
from pdf_mcp.tools.retrieval import retrieve_from_pdf
from pdf_mcp.pdf.manager import PDFManager
from langchain_core.messages import HumanMessage


# In-memory prompt registry
PROMPTS: Dict[str, Prompt] = {}

def register_prompts(server):
    @server.prompt
    def summarize_pdf(pdf_path: str) -> str:
        """Summarize the content of a PDF file."""
        return retrieve_from_pdf('summarize', pdf_path)
