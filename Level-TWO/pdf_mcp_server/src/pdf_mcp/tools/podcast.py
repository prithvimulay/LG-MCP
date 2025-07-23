from pdf_mcp.pdf.processor import PDFProcessor
from pdf_mcp.config.settings import settings
from pathlib import Path

processor = PDFProcessor()

def generate_podcast(query: str, pdf_filename: str) -> str:
    pdf_path = settings.pdf_storage_path / pdf_filename
    
    if not pdf_path.exists():
        return f"PDF not found: {pdf_filename}. Available PDFs are in {settings.pdf_storage_path}"
    
    try:
        text = processor.extract_text(str(pdf_path))
        
        intro = f"🎙️ Welcome to this AI-powered podcast about '{query}'!\n\n"
        
        lines = [line.strip() for line in text.splitlines() if line.strip() and len(line.strip()) > 20]
        
        dialogue = []
        dialogue.append(f"Host: Today we're discussing '{query}' based on insights from {pdf_filename}.")
        dialogue.append(f"Expert: That's right! Let me share some key points from this document.")
        
        for i, line in enumerate(lines[:10]):  
            if i % 2 == 0:
                dialogue.append(f"Expert: {line[:200]}...")
            else:
                dialogue.append(f"Host: That's fascinating! Can you elaborate on that?")
        
        dialogue.append(f"Host: Thank you for this insightful discussion about '{query}'!")
        dialogue.append(f"Expert: My pleasure! This topic from {pdf_filename} really highlights important concepts.")
        
        podcast_script = intro + "\n\n".join(dialogue)
        return podcast_script
        
    except Exception as e:
        return f"Error generating podcast: {str(e)}"
