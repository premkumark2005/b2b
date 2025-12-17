"""
Script to view contents of ChromaDB vector databases.
Run this to inspect what's stored in your 4 collections.
"""

import chromadb
from chromadb.config import Settings
from config import CHROMADB_PATH

# Custom embedding function (must match the one used in chromadb_setup.py)
class SentenceTransformerEmbedding:
    def __init__(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
    
    def __call__(self, input):
        embeddings = self.model.encode(input)
        return embeddings.tolist()
    
    def name(self):
        return "paraphrase-MiniLM-L3-v2"

def get_collections():
    """Get all ChromaDB collections."""
    client = chromadb.PersistentClient(
        path=CHROMADB_PATH,
        settings=Settings(anonymized_telemetry=False)
    )
    
    embedding_function = SentenceTransformerEmbedding()
    
    return {
        'web_db': client.get_collection('web_db', embedding_function=embedding_function),
        'product_db': client.get_collection('product_db', embedding_function=embedding_function),
        'job_db': client.get_collection('job_db', embedding_function=embedding_function),
        'news_db': client.get_collection('news_db', embedding_function=embedding_function)
    }

def view_all_collections():
    """Display all data stored in ChromaDB collections."""
    
    print("Loading ChromaDB...")
    collections = get_collections()
    
    print('=' * 80)
    print('CHROMADB VECTOR DATABASE CONTENTS')
    print('=' * 80)
    
    for name, collection in collections.items():
        print(f'\n📊 Collection: {name}')
        print('-' * 80)
        
        # Get count
        count = collection.count()
        print(f'Total documents: {count}')
        
        if count > 0:
            # Get all data (documents, metadata, embeddings)
            results = collection.get(
                include=['documents', 'metadatas', 'embeddings']
            )
            
            print(f'\nDocuments:')
            for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas']), 1):
                print(f'\n  📄 Document {i}:')
                print(f'    ID: {results["ids"][i-1]}')
                print(f'    Metadata: {meta}')
                print(f'    Content length: {len(doc)} characters')
                print(f'    Content preview (first 300 chars):')
                print(f'    {doc[:300]}...')
                
                if results.get('embeddings') is not None and len(results['embeddings']) > 0:
                    embedding_dims = len(results['embeddings'][i-1])
                    print(f'    Embedding: {embedding_dims} dimensions')
                    print(f'    Embedding preview (first 5 values): {results["embeddings"][i-1][:5]}')
        else:
            print('  ⚠️  No documents stored in this collection')
        
        print()
    
    print('=' * 80)

def search_collection(collection_name: str, query: str, n_results: int = 3):
    """
    Search a specific collection with a query.
    
    Args:
        collection_name: Name of collection (web_db, product_db, job_db, news_db)
        query: Search query text
        n_results: Number of results to return
    """
    collections = get_collections()
    
    if collection_name not in collections:
        print(f"❌ Collection '{collection_name}' not found!")
        print(f"Available collections: {list(collections.keys())}")
        return
    
    collection = collections[collection_name]
    
    print(f'\n🔍 Searching "{collection_name}" for: "{query}"')
    print('-' * 80)
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=['documents', 'metadatas', 'distances']
    )
    
    if results['documents'][0]:
        for i, (doc, meta, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            print(f'\n📌 Result {i} (similarity score: {1 - distance:.4f}):')
            print(f'   Metadata: {meta}')
            print(f'   Content: {doc[:400]}...')
    else:
        print('No results found')

if __name__ == "__main__":
    # View all collections
    view_all_collections()
    
    # Example: Search specific collection
    # Uncomment to test searching:
    # search_collection('web_db', 'NVIDIA graphics cards', n_results=2)
