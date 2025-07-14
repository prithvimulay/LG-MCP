from pdf_mcp.pdf.processor import PDFProcessor
from pathlib import Path

processor = PDFProcessor()

def generate_podcast(pdf_path: str) -> str:
    path = Path(pdf_path)
    if not path.exists():
        return f"PDF not found: {pdf_path}"
    
    text = processor.extract_text(pdf_path)
    intro = "Welcome to this AI-powered podcast.\n"
    body = "\n".join([f"A: {line.strip()}\nB: Interesting!" for line in text.splitlines()[:5]])
    return f"{intro}{body}"
