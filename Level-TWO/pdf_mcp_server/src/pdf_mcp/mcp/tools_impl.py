from fastmcp.tools import tool
from pdf_mcp.tools.retrieval import retrieve_from_pdf
from pdf_mcp.tools.podcast import generate_podcast
from pdf_mcp.tools.selection import select_relevant_pdf
from pdf_mcp.pdf.manager import PDFManager

def list_pdfs() -> str:
    manager = PDFManager()
    pdfs = manager.list_pdfs()
    if not pdfs:
        return "No PDFs found."
    return "\n".join(f"- {pdf.name}" for pdf in pdfs)

def register_tools(server):
    @server.tool
    def retrieve_from_pdf_tool(query: str, pdf_filename: str) -> str:
        return retrieve_from_pdf(query, pdf_filename)
    
    @server.tool
    def generate_podcast_tool(query: str, pdf_filename: str) -> str:
        return generate_podcast(query, pdf_filename)
    
    @server.tool
    def select_relevant_pdf_tool(query: str) -> str:
        return select_relevant_pdf(query)
    
    @server.tool
    def list_pdfs_tool() -> str:
        return list_pdfs()
