from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from models.schemas import ProductUploadRequest, UploadResponse
from utils.pdf_parser import extract_text_from_pdf, extract_product_content
from database.chromadb_setup import get_product_db, insert_into_collection
import uuid

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_product_data(
    company_name: str = Form(...),
    plain_text: str = Form(None),
    pdf_file: UploadFile = File(None)
):
    """
    Endpoint 2: Product Brochure Upload
    
    User can upload:
    a) PDF brochure
    b) Plain text
    
    Processes and stores in product_db collection.
    """
    try:
        text = ""
        
        # Process based on input type
        if pdf_file:
            # Extract text from PDF using PyPDF2
            text = extract_text_from_pdf(pdf_file.file)
        elif plain_text:
            # Use plain text directly
            text = plain_text
        else:
            raise HTTPException(status_code=400, detail="Must provide PDF file or plain text")
        
        # Extract product-related content
        product_text = extract_product_content(text)
        
        print(f"Product text length: {len(product_text)} characters")
        
        # IMMEDIATE CHUNKING - No truncation
        from utils.text_chunker import chunk_text
        chunks = chunk_text(product_text, chunk_size=400, overlap=50)
        print(f"Created {len(chunks)} chunks")
        
        # Store EACH chunk as a separate document
        product_db = get_product_db()
        
        for idx, chunk in enumerate(chunks):
            doc_id = f"product_{company_name}_{idx}_{uuid.uuid4().hex[:8]}"
            
            insert_into_collection(
                collection=product_db,
                text=chunk,
                company_name=company_name,
                source="product",
                doc_id=doc_id,
                chunk_index=idx
            )
        
        return UploadResponse(
            status="success",
            message="Product data stored in product_db",
            company_name=company_name
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
