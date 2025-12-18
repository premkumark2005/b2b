from fastapi import APIRouter, HTTPException
from models.schemas import ProfileGenerateRequest, ProfileResponse
from database.chromadb_setup import (
    get_web_db, get_product_db, get_job_db, get_news_db,
    query_collection, query_collection_with_query
)
from database.mongodb_setup import insert_company_profile, get_company_profile
from services.llm_service import (
    extract_with_tinyllama,
    extract_business_overview,
    extract_hiring_focus,
    extract_recent_events
)
from datetime import datetime

router = APIRouter()

@router.post("/generate", response_model=ProfileResponse)
async def generate_unified_profile(request: ProfileGenerateRequest):
    """
    Endpoint 5: Generate Unified Company Profile
    
    Process:
    1) Retrieve documents from all 4 ChromaDB collections
    2) Combine into one context string
    3) Send to tinyllama via Ollama
    4) Extract structured JSON
    5) Store in MongoDB
    6) Return unified profile
    """
    try:
        company_name = request.company_name
        
        # Step 1: Retrieve relevant documents from all collections
        web_db = get_web_db()
        product_db = get_product_db()
        job_db = get_job_db()
        news_db = get_news_db()
        
        # FIELD-SPECIFIC RETRIEVAL with semantic queries
        # Business overview fields: website + product data
        web_docs = query_collection_with_query(web_db, company_name, 
            f"{company_name} business overview products services industries markets", n_results=8)
        product_docs = query_collection_with_query(product_db, company_name,
            f"{company_name} products offerings solutions technology", n_results=5)
        
        # Hiring focus: job postings ONLY
        job_docs = query_collection_with_query(job_db, company_name,
            f"{company_name} hiring jobs careers roles openings engineers positions", n_results=5)
        
        # Recent events: news ONLY
        news_docs = query_collection_with_query(news_db, company_name,
            f"{company_name} news announcements launches acquisitions updates events", n_results=5)
        
        # DEBUG: Log retrieval results
        print("\n" + "="*80)
        print("CHUNK RETRIEVAL RESULTS:")
        print("="*80)
        print(f"Website chunks: {len(web_docs)}")
        print(f"Product chunks: {len(product_docs)}")
        print(f"Job chunks: {len(job_docs)}")
        print(f"News chunks: {len(news_docs)}")
        print("="*80)
        
        # Step 2: Deduplicate chunks (remove exact duplicates and very similar ones)
        def deduplicate_chunks(chunks: list) -> list:
            """Remove duplicate chunks to reduce redundancy"""
            seen = set()
            unique = []
            for chunk in chunks:
                # Normalize: strip whitespace and lowercase for comparison
                normalized = chunk.strip().lower()
                if normalized not in seen and len(normalized) > 50:  # Skip tiny chunks
                    seen.add(normalized)
                    unique.append(chunk)
            return unique
        
        web_docs = deduplicate_chunks(web_docs)
        product_docs = deduplicate_chunks(product_docs)
        job_docs = deduplicate_chunks(job_docs)
        news_docs = deduplicate_chunks(news_docs)
        
        print(f"After deduplication: Web={len(web_docs)}, Product={len(product_docs)}, Job={len(job_docs)}, News={len(news_docs)}")
        
        # Step 3: Combine retrieved documents into ONE structured context
        combined_context = f"""
=== WEBSITE INFORMATION ===
{' '.join(web_docs)}

=== PRODUCT INFORMATION ===
{' '.join(product_docs)}

=== JOB POSTINGS ===
{' '.join(job_docs)}

=== NEWS & EVENTS ===
{' '.join(news_docs)}
"""
        
        # DEBUG: Log context being sent to LLM
        print("\n" + "="*80)
        print("CONTEXT SENT TO LLM:")
        print("="*80)
        print(combined_context[:1500])  # First 1500 chars
        print("...")
        print("="*80)
        print(f"Total context length: {len(combined_context)} characters")
        print("="*80 + "\n")
        
        if not any([web_docs, product_docs, job_docs, news_docs]):
            raise HTTPException(
                status_code=404,
                detail=f"No data found for company: {company_name}"
            )
        
        # Step 4: FIELD-SPECIFIC EXTRACTION (separate LLM calls)
        print("\n" + "="*80)
        print("FIELD-SPECIFIC EXTRACTION:")
        print("="*80)
        
        # Extract business overview fields (business_summary, product_lines, target_industries, regions)
        overview_context = f"""
=== WEBSITE INFORMATION ===
{' '.join(web_docs)}

=== PRODUCT INFORMATION ===
{' '.join(product_docs)}
"""
        print(f"1. Extracting business overview from {len(web_docs)} web + {len(product_docs)} product chunks")
        overview_fields = extract_business_overview(overview_context)
        
        # Extract hiring_focus from job postings ONLY
        job_context = ' '.join(job_docs)
        print(f"2. Extracting hiring_focus from {len(job_docs)} job chunks")
        hiring_focus = extract_hiring_focus(job_context) if job_docs else []
        
        # Extract recent_events from news ONLY
        news_context = ' '.join(news_docs)
        print(f"3. Extracting recent_events from {len(news_docs)} news chunks")
        recent_events = extract_recent_events(news_context) if news_docs else []
        
        # Merge all extracted fields
        extracted_fields = {
            "business_summary": overview_fields.get("business_summary", ""),
            "product_lines": overview_fields.get("product_lines", []),
            "target_industries": overview_fields.get("target_industries", []),
            "regions": overview_fields.get("regions", []),
            "hiring_focus": hiring_focus,
            "key_recent_events": recent_events
        }
        
        print(f"✅ EXTRACTION COMPLETE:")
        print(f"   - Business summary: {len(extracted_fields['business_summary'])} chars")
        print(f"   - Product lines: {len(extracted_fields['product_lines'])} items")
        print(f"   - Industries: {len(extracted_fields['target_industries'])} items")
        print(f"   - Regions: {len(extracted_fields['regions'])} items")
        print(f"   - Hiring focus: {len(extracted_fields['hiring_focus'])} roles")
        print(f"   - Recent events: {len(extracted_fields['key_recent_events'])} events")
        print("="*80 + "\n")
        
        # Step 6: Store in MongoDB
        profile_id = insert_company_profile(company_name, extracted_fields)
        
        # Step 6: Return unified profile
        profile = get_company_profile(company_name)
        
        return ProfileResponse(
            company_name=profile['company_name'],
            extracted_fields=profile['extracted_fields'],
            created_at=profile['created_at'].isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{company_name}", response_model=ProfileResponse)
async def get_profile(company_name: str):
    """
    Retrieve existing company profile from MongoDB.
    """
    try:
        profile = get_company_profile(company_name)
        
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Profile not found for company: {company_name}"
            )
        
        return ProfileResponse(
            company_name=profile['company_name'],
            extracted_fields=profile['extracted_fields'],
            created_at=profile['created_at'].isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
