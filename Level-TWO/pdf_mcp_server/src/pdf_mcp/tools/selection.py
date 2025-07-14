from pdf_mcp.pdf.manager import PDFManager

manager = PDFManager()

def select_relevant_pdf(query: str) -> str:
    query = query.lower()
    pdfs = manager.list_pdfs()
    if not pdfs:
        return "No PDFs found."

    scored = sorted(pdfs, key=lambda f: sum(word in f.name.lower() for word in query.split()), reverse=True)
    return str(scored[0])  # return path
