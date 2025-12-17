from fastapi import APIRouter, HTTPException
from models.schemas import WebsiteUploadRequest, UploadResponse
from utils.scraper import scrape_with_zenrows
from utils.html_parser import html_to_text, extract_keywords
from database.chromadb_setup import get_web_db, insert_into_collection
import uuid

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_website_data(request: WebsiteUploadRequest):
    """
    Endpoint 1: Website Data Upload
    
    User can provide:
    a) Website URL
    b) Raw HTML content
    c) Plain text
    
    Processes and stores in web_db collection.
    """
    try:
        print(f"Received website upload request for company: {request.company_name}")
        text = ""
        
        # Process based on input type
        if request.url:
            print(f"Processing URL: {request.url}")
            # Scrape using ZenRows API ONLY
            html = scrape_with_zenrows(request.url)
            text = html_to_text(html)
            print("URL scraped and parsed successfully")
        elif request.html_content:
            print("Processing HTML content")
            # Parse HTML to text
            text = html_to_text(request.html_content)
        elif request.plain_text:
            print("Processing plain text")
            # Use plain text directly
            text = request.plain_text
        else:
            raise HTTPException(status_code=400, detail="Must provide URL, HTML content, or plain text")
        
        print(f"Cleaned text length: {len(text)} characters")
        
        # IMMEDIATE CHUNKING - No truncation
        from utils.text_chunker import chunk_text
        
        chunks = chunk_text(text, chunk_size=400, overlap=50)
        print(f"Created {len(chunks)} chunks from cleaned content")
        
        # Store EACH chunk as a separate document in ChromaDB
        web_db = get_web_db()
        
        for idx, chunk in enumerate(chunks):
            doc_id = f"web_{request.company_name}_{idx}_{uuid.uuid4().hex[:8]}"
            
            print(f"Storing chunk {idx} in ChromaDB with doc_id: {doc_id}")
            insert_into_collection(
                collection=web_db,
                text=chunk,
                company_name=request.company_name,
                source="website",
                doc_id=doc_id,
                chunk_index=idx
            )
        print("Successfully stored in web_db")
        
        return UploadResponse(
            status="success",
            message="Website data stored in web_db",
            company_name=request.company_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in website upload: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
