from pdf_mcp.pdf.processor import PDFProcessor
from pathlib import Path

processor = PDFProcessor()

def generate_podcast(query: str, pdf_filename: str) -> str:
    path = Path(pdf_filename)
    if not path.exists():
        return f"PDF not found: {pdf_filename}"
    
    text = processor.extract_text(pdf_filename)
    intro = f"Welcome to this AI-powered podcast about '{query}'.\n"
    body = "\n".join([f"A: {line.strip()}\nB: Interesting point about {query}!" for line in text.splitlines()[:5]])
    return f"{intro}{body}"
