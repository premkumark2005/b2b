import chromadb
from chromadb.config import Settings
from config import CHROMADB_PATH, WEB_COLLECTION, PRODUCT_COLLECTION, JOB_COLLECTION, NEWS_COLLECTION

# Global ChromaDB client
chroma_client = None
web_db = None
product_db = None
job_db = None
news_db = None

# Custom embedding function using SentenceTransformer
class SentenceTransformerEmbedding:
    def __init__(self):
        print("Loading SentenceTransformer model: paraphrase-MiniLM-L3-v2...")
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
        print("✅ Model loaded successfully")
    
    def __call__(self, input):
        embeddings = self.model.encode(input)
        return embeddings.tolist()
    
    def embed_query(self, input):
        """Required by ChromaDB for query operations"""
        # ChromaDB passes 'input' parameter
        return self.model.encode(input).tolist()
    
    def name(self):
        return "paraphrase-MiniLM-L3-v2"

def init_chromadb():
    """
    Initialize ChromaDB with four separate collections:
    - web_db
    - product_db
    - job_db
    - news_db
    """
    global chroma_client, web_db, product_db, job_db, news_db
    
    try:
        # Initialize ChromaDB client (local, lightweight)
        print("Initializing ChromaDB client...")
        chroma_client = chromadb.PersistentClient(
            path=CHROMADB_PATH,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Create custom embedding function
        print("Initializing custom embedding function...")
        embedding_function = SentenceTransformerEmbedding()
        
        # Create or get collections with custom embedding
        print("Creating/getting collections...")
        web_db = chroma_client.get_or_create_collection(
            name=WEB_COLLECTION,
            embedding_function=embedding_function
        )
        product_db = chroma_client.get_or_create_collection(
            name=PRODUCT_COLLECTION,
            embedding_function=embedding_function
        )
        job_db = chroma_client.get_or_create_collection(
            name=JOB_COLLECTION,
            embedding_function=embedding_function
        )
        news_db = chroma_client.get_or_create_collection(
            name=NEWS_COLLECTION,
            embedding_function=embedding_function
        )
    except Exception as e:
        print(f"Error initializing ChromaDB: {e}")
        raise
    
    print(f"✅ ChromaDB collections initialized:")
    print(f"   - {WEB_COLLECTION}")
    print(f"   - {PRODUCT_COLLECTION}")
    print(f"   - {JOB_COLLECTION}")
    print(f"   - {NEWS_COLLECTION}")

def get_web_db():
    return web_db

def get_product_db():
    return product_db

def get_job_db():
    return job_db

def get_news_db():
    return news_db

def insert_into_collection(collection, text: str, company_name: str, source: str, doc_id: str, chunk_index: int = 0):
    """
    Insert text chunk into specified ChromaDB collection with embeddings.
    
    Args:
        collection: ChromaDB collection object
        text: Text content to embed and store
        company_name: Company name for metadata filtering
        source: Source type (website, product, jobs, news)
        doc_id: Unique document ID
        chunk_index: Index of the chunk (for multi-chunk documents)
    """
    try:
        print(f"Adding document to collection, length: {len(text)} chars, chunk {chunk_index}")
        collection.add(
            documents=[text],
            metadatas=[{
                "company_name": company_name,
                "source": source,
                "chunk_index": chunk_index
            }],
            ids=[doc_id]
        )
        print(f"Successfully added document: {doc_id}")
    except Exception as e:
        print(f"Error adding to collection: {e}")
        raise

def query_collection(collection, company_name: str, n_results: int = 15):
    """
    Retrieve relevant documents from collection using SEMANTIC SEARCH.
    Uses .query() instead of .get() for better relevance ranking.
    
    Args:
        collection: ChromaDB collection object
        company_name: Company name to search for
        n_results: Number of top results to retrieve (default 15)
    
    Returns:
        List of document texts ranked by semantic similarity
    """
    # Use semantic query with comprehensive search terms
    query_text = f"{company_name} business overview products services industries markets regions hiring news events"
    
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where={"company_name": company_name},  # Still filter by company
        include=["documents", "metadatas"]
    )
    
    # Extract documents from query results
    if results and results['documents'] and len(results['documents']) > 0:
        return results['documents'][0]  # First query result set
    return []

def query_collection_with_query(collection, company_name: str, custom_query: str, n_results: int = 5):
    """
    Retrieve documents using a CUSTOM semantic query.
    Used for field-specific retrieval (e.g., hiring, news).
    
    Args:
        collection: ChromaDB collection object
        company_name: Company name to filter by
        custom_query: Custom semantic query text
        n_results: Number of results (default 5)
    
    Returns:
        List of document texts ranked by semantic similarity
    """
    results = collection.query(
        query_texts=[custom_query],
        n_results=n_results,
        where={"company_name": company_name},
        include=["documents", "metadatas"]
    )
    
    if results and results['documents'] and len(results['documents']) > 0:
        return results['documents'][0]
    return []
