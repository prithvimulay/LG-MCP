from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.tools import Tool

yt_url = "https://www.youtube.com/watch?v=rD1O3R9B0Sw"

loader = YoutubeLoader.from_youtube_url(
    yt_url,
    add_video_info=False,
    language=["en"]
)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(docs)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(chunks, embedding=embeddings, persist_directory="./chroma_db")

retriever = vectorstore.as_retriever()

def query_youtube_transcript(question: str) -> str:
    """
    Always queries the static video transcript already indexed in Chroma.
    """
    return retriever.invoke(question)

from langchain_core.tools import tool

@tool
def pickleball_youtube(question: str) -> str:
    """
    Answer questions from a fixed pickleball YouTube video transcript about the rules, scoring, and kitchen zone. Provide answers only from that video.
    """
    return retriever.invoke(question)
