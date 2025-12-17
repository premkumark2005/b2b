from fastapi import APIRouter, HTTPException
from models.schemas import NewsUploadRequest, UploadResponse
from utils.scraper import scrape_with_zenrows
from utils.html_parser import html_to_text
from database.chromadb_setup import get_news_db, insert_into_collection
import uuid

router = APIRouter()

def extract_news_events(text: str) -> str:
    """
    Extract news content from text.
    Returns full text since HTML cleaning already filtered out noise.
    """
    # Return full text - HTML cleaning already removed navigation/footers
    return text.strip()

@router.post("/upload", response_model=UploadResponse)
async def upload_news_data(request: NewsUploadRequest):
    """
    Endpoint 4: News Upload
    
    User can provide:
    a) News text
    b) News URL (scrape using ZenRows)
    
    Processes and stores in news_db collection.
    """
    try:
        text = ""
        
        # Process based on input type
        if request.news_url:
            # Scrape using ZenRows API
            html = scrape_with_zenrows(request.news_url)
            text = html_to_text(html)
        elif request.news_text:
            # Use news text directly
            text = request.news_text
        else:
            raise HTTPException(status_code=400, detail="Must provide news text or news URL")
        
        # Extract key recent events
        news_events = extract_news_events(text)
        
        print(f"News text length: {len(news_events)} characters")
        
        # IMMEDIATE CHUNKING - No truncation
        from utils.text_chunker import chunk_text
        chunks = chunk_text(news_events, chunk_size=400, overlap=50)
        print(f"Created {len(chunks)} chunks")
        
        # Store EACH chunk as a separate document
        news_db = get_news_db()
        
        for idx, chunk in enumerate(chunks):
            doc_id = f"news_{request.company_name}_{idx}_{uuid.uuid4().hex[:8]}"
            
            insert_into_collection(
                collection=news_db,
                text=chunk,
                company_name=request.company_name,
                source="news",
                doc_id=doc_id,
                chunk_index=idx
            )
        
        return UploadResponse(
            status="success",
            message="News data stored in news_db",
            company_name=request.company_name
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
