from PyPDF2 import PdfReader
from langchain.docstore.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.tools.retriever import create_retriever_tool

# Path to your static Pickleball PDF
pdf_path = "data/Pickleball-Rulebook.pdf"

# Load with PyPDF2
def load_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return [Document(page_content=text)]

docs = load_pdf(pdf_path)

# Split
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(docs)

# Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Vector store
vectorstore = Chroma.from_documents(chunks, embedding=embeddings, persist_directory="./chroma_db")

# Retriever tool
pdf_retriever = vectorstore.as_retriever()
pdf_tool = create_retriever_tool(
    pdf_retriever,
    name="pickle_ball_rules_pdf",
    description="Answer questions about the Pickleball rules from the official PDF guide."
)
