from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from models.schemas import UploadResponse
from utils.scraper import scrape_with_zenrows
from utils.html_parser import html_to_text, extract_keywords
from database.chromadb_setup import get_web_db, insert_into_collection
import uuid

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_website_data(
    company_name: str = Form(...),
    url: Optional[str] = Form(None),
    html_file: Optional[UploadFile] = File(None)
):
    """
    Endpoint 1: Website Data Upload
    
    User can provide:
    a) Website URL
    b) HTML file upload
    
    Processes and stores in web_db collection.
    """
    try:
        print(f"Received website upload request for company: {company_name}")
        text = ""
        
        # Process based on input type
        if html_file:
            print(f"Processing HTML file: {html_file.filename}")
            html_content = await html_file.read()
            html_text = html_content.decode('utf-8')
            text = html_to_text(html_text)
            print("HTML file parsed successfully")
        elif url:
            print(f"Processing URL: {url}")
            # Scrape using ZenRows API ONLY
            html = scrape_with_zenrows(url)
            text = html_to_text(html)
            print("URL scraped and parsed successfully")
        else:
            raise HTTPException(status_code=400, detail="Must provide URL or HTML file")
        
        print(f"Cleaned text length: {len(text)} characters")
        
        # IMMEDIATE CHUNKING - No truncation
        from utils.text_chunker import chunk_text
        
        chunks = chunk_text(text, chunk_size=400, overlap=50)
        print(f"Created {len(chunks)} chunks from cleaned content")
        
        # Store EACH chunk as a separate document in ChromaDB
        web_db = get_web_db()
        
        for idx, chunk in enumerate(chunks):
            doc_id = f"web_{company_name}_{idx}_{uuid.uuid4().hex[:8]}"
            
            print(f"Storing chunk {idx} in ChromaDB with doc_id: {doc_id}")
            insert_into_collection(
                collection=web_db,
                text=chunk,
                company_name=company_name,
                source="website",
                doc_id=doc_id,
                chunk_index=idx
            )
        print("Successfully stored in web_db")
        
        return UploadResponse(
            status="success",
            message="Website data stored in web_db",
            company_name=company_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in website upload: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
