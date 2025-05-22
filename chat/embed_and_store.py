__import__('pysqlite3')
import sys, os
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

vector_store = Chroma(
    collection_name = "knotebooklm",
    embedding_function=embeddings,
    persist_directory = "./chroma_langchain_db",
)

def add_documents(documents):
    return vector_store.add_documents(documents=documents)