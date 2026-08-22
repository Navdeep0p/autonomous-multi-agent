import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import GEMINI_API_KEY

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data/chroma_db")
os.makedirs(DATA_DIR, exist_ok=True)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=GEMINI_API_KEY
)

vector_store = Chroma(
    collection_name="local_knowledge_base",
    embedding_function=embeddings,
    persist_directory=DATA_DIR
)

def query_local_docs(query: str, k: int = 3) -> list[str]:
    """Retrieves top-k relevant chunks from the local vector database."""
    try:
        results = vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in results if doc.page_content.strip()]
    except Exception as e:
        return []

def add_document_to_db(text: str, metadata: dict = None):
    """Utility to index text documents into the local knowledge base."""
    vector_store.add_texts(texts=[text], metadatas=[metadata or {}])