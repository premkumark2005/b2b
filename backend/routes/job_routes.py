from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from models.schemas import UploadResponse
from utils.scraper import scrape_with_zenrows
from utils.html_parser import html_to_text
from database.chromadb_setup import get_job_db, insert_into_collection
import uuid
import re

router = APIRouter()

def extract_job_info(text: str) -> str:
    """
    Extract job-related information from text.
    Returns full text since HTML cleaning already filtered out noise.
    """
    # Return full text - HTML cleaning already removed navigation/footers
    return text.strip()

@router.post("/upload", response_model=UploadResponse)
async def upload_job_data(
    company_name: str = Form(...),
    job_text: Optional[str] = Form(None),
    job_url: Optional[str] = Form(None),
    html_file: Optional[UploadFile] = File(None)
):
    """
    Endpoint 3: Job Post Upload
    
    User can provide:
    a) Job post text
    b) Job post URL (scrape using ZenRows)
    c) HTML file
    
    Processes and stores in job_db collection.
    """
    try:
        text = ""
        
        # Process based on input type
        if html_file:
            print(f"Processing HTML file: {html_file.filename}")
            html_content = await html_file.read()
            html_text = html_content.decode('utf-8')
            text = html_to_text(html_text)
        elif job_url:
            # Scrape using ZenRows API
            html = scrape_with_zenrows(job_url)
            text = html_to_text(html)
        elif job_text:
            # Use job text directly
            text = job_text
        else:
            raise HTTPException(status_code=400, detail="Must provide HTML file, job text, or job URL")
        
        # Extract job-specific content
        job_text = extract_job_info(text)
        
        print(f"Job text length: {len(job_text)} characters")
        
        # IMMEDIATE CHUNKING - No truncation
        from utils.text_chunker import chunk_text
        chunks = chunk_text(job_text, chunk_size=400, overlap=50)
        print(f"Created {len(chunks)} chunks")
        
        # Store EACH chunk as a separate document
        job_db = get_job_db()
        
        for idx, chunk in enumerate(chunks):
            doc_id = f"job_{company_name}_{idx}_{uuid.uuid4().hex[:8]}"
            
            insert_into_collection(
                collection=job_db,
                text=chunk,
                company_name=company_name,
                source="jobs",
                doc_id=doc_id,
                chunk_index=idx
            )
        
        return UploadResponse(
            status="success",
            message="Job data stored in job_db",
            company_name=request.company_name
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
