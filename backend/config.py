import os
from dotenv import load_dotenv

load_dotenv()

# ZenRows Configuration
ZENROWS_API_KEY = os.getenv("ZENROWS_API_KEY", "")

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DB", "b2b_fusion")

# ChromaDB Configuration
CHROMADB_PATH = os.getenv("CHROMADB_PATH", "./chroma_data")

# Ollama Configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "tinyllama")

# ChromaDB Collection Names
WEB_COLLECTION = "web_db"
PRODUCT_COLLECTION = "product_db"
JOB_COLLECTION = "job_db"
NEWS_COLLECTION = "news_db"
