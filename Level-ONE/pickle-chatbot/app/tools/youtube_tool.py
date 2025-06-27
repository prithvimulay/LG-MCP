from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.tools.retriever import create_retriever_tool

# static video
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
youtube_tool = create_retriever_tool(
    retriever,
    name="pickleball_youtube",
    description="Answer questions from the static Pickleball tutorial video"
)
