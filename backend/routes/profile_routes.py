from fastapi import APIRouter, HTTPException
from models.schemas import ProfileGenerateRequest, ProfileResponse
from database.chromadb_setup import (
    get_web_db, get_product_db, get_job_db, get_news_db,
    query_collection, query_collection_with_query
)
from database.mongodb_setup import (
    insert_company_profile, get_company_profile,
    insert_industry_mapping, get_industry_mapping
)
from services.llm_service import (
    extract_with_tinyllama,
    extract_business_overview,
    extract_hiring_focus,
    extract_recent_events
)
from services.industry_matcher import get_industry_matcher
from datetime import datetime
from typing import Dict, List

router = APIRouter()

def calculate_confidence(field_sources: Dict[str, List[str]]) -> Dict[str, float]:
    """
    Calculate confidence scores based on number of sources contributing to each field.
    
    Formula: confidence = (number_of_sources_contributing) / (total_sources)
    Total sources = 4 (website, product, jobs, news)
    
    Args:
        field_sources: Dict mapping field names to list of contributing sources
        Example: {"business_summary": ["website", "product"], "hiring_focus": ["jobs"]}
    
    Returns:
        Dict mapping field names to confidence scores (0.0 to 1.0)
    """
    TOTAL_SOURCES = 4
    confidence_scores = {}
    
    for field, sources in field_sources.items():
        # Count unique sources
        unique_sources = len(set(sources))
        confidence = unique_sources / TOTAL_SOURCES
        confidence_scores[field] = round(confidence, 2)
    
    return confidence_scores

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
        company_domain = request.company_domain or ""
        company_domain = request.company_domain or ""
        
        # Step 1: Retrieve relevant documents from all collections
        web_db = get_web_db()
        product_db = get_product_db()
        job_db = get_job_db()
        news_db = get_news_db()
        
        # FIELD-SPECIFIC RETRIEVAL with semantic queries
        # Query ALL sources for each field type using targeted semantic queries
        
        # Business overview: website + product focused
        web_docs_business = query_collection_with_query(web_db, company_name, 
            f"{company_name} business overview products services industries markets", n_results=8)
        product_docs_business = query_collection_with_query(product_db, company_name,
            f"{company_name} products offerings solutions technology", n_results=5)
        job_docs_business = query_collection_with_query(job_db, company_name,
            f"{company_name} business company overview", n_results=2)
        news_docs_business = query_collection_with_query(news_db, company_name,
            f"{company_name} company business overview", n_results=2)
        
        # Hiring focus: ALL sources, hiring-focused query
        web_docs_hiring = query_collection_with_query(web_db, company_name,
            f"{company_name} hiring jobs careers team recruitment talent", n_results=3)
        product_docs_hiring = query_collection_with_query(product_db, company_name,
            f"{company_name} team careers hiring", n_results=2)
        job_docs_hiring = query_collection_with_query(job_db, company_name,
            f"{company_name} hiring jobs careers roles openings engineers positions", n_results=8)
        news_docs_hiring = query_collection_with_query(news_db, company_name,
            f"{company_name} hiring recruitment jobs expansion team", n_results=3)
        
        # Recent events: ALL sources, event-focused query
        web_docs_events = query_collection_with_query(web_db, company_name,
            f"{company_name} news announcements updates launches", n_results=3)
        product_docs_events = query_collection_with_query(product_db, company_name,
            f"{company_name} new launch release announcement", n_results=2)
        job_docs_events = query_collection_with_query(job_db, company_name,
            f"{company_name} expansion growth new office", n_results=2)
        news_docs_events = query_collection_with_query(news_db, company_name,
            f"{company_name} news announcements launches acquisitions updates events", n_results=8)
        
        # DEBUG: Log retrieval results
        print("\n" + "="*80)
        print("CHUNK RETRIEVAL RESULTS:")
        print("="*80)
        print(f"Business overview chunks: Web={len(web_docs_business)}, Product={len(product_docs_business)}, Job={len(job_docs_business)}, News={len(news_docs_business)}")
        print(f"Hiring chunks: Web={len(web_docs_hiring)}, Product={len(product_docs_hiring)}, Job={len(job_docs_hiring)}, News={len(news_docs_hiring)}")
        print(f"Events chunks: Web={len(web_docs_events)}, Product={len(product_docs_events)}, Job={len(job_docs_events)}, News={len(news_docs_events)}")
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
        
        # Deduplicate each category
        web_docs_business = deduplicate_chunks(web_docs_business)
        product_docs_business = deduplicate_chunks(product_docs_business)
        job_docs_business = deduplicate_chunks(job_docs_business)
        news_docs_business = deduplicate_chunks(news_docs_business)
        
        web_docs_hiring = deduplicate_chunks(web_docs_hiring)
        product_docs_hiring = deduplicate_chunks(product_docs_hiring)
        job_docs_hiring = deduplicate_chunks(job_docs_hiring)
        news_docs_hiring = deduplicate_chunks(news_docs_hiring)
        
        web_docs_events = deduplicate_chunks(web_docs_events)
        product_docs_events = deduplicate_chunks(product_docs_events)
        job_docs_events = deduplicate_chunks(job_docs_events)
        news_docs_events = deduplicate_chunks(news_docs_events)
        
        # Step 4: FIELD-SPECIFIC EXTRACTION (separate LLM calls)
        print("\n" + "="*80)
        print("FIELD-SPECIFIC EXTRACTION:")
        print("="*80)
        
        # Extract business overview fields (business_summary, product_lines, target_industries, regions)
        overview_context = f"""
=== WEBSITE INFORMATION ===
{' '.join(web_docs_business)}

=== PRODUCT INFORMATION ===
{' '.join(product_docs_business)}

=== JOB POSTINGS ===
{' '.join(job_docs_business)}

=== NEWS & EVENTS ===
{' '.join(news_docs_business)}
"""
        print(f"1. Extracting business overview from all sources: Web={len(web_docs_business)}, Product={len(product_docs_business)}, Job={len(job_docs_business)}, News={len(news_docs_business)}")
        overview_fields = extract_business_overview(overview_context)
        
        # Extract hiring_focus from ALL sources with hiring-focused context
        hiring_context = f"""
=== WEBSITE INFORMATION ===
{' '.join(web_docs_hiring)}

=== PRODUCT INFORMATION ===
{' '.join(product_docs_hiring)}

=== JOB POSTINGS ===
{' '.join(job_docs_hiring)}

=== NEWS & EVENTS ===
{' '.join(news_docs_hiring)}
"""
        print(f"2. Extracting hiring_focus from all sources: Web={len(web_docs_hiring)}, Product={len(product_docs_hiring)}, Job={len(job_docs_hiring)}, News={len(news_docs_hiring)}")
        hiring_focus = extract_hiring_focus(hiring_context) if any([web_docs_hiring, product_docs_hiring, job_docs_hiring, news_docs_hiring]) else []
        
        # Extract recent_events from ALL sources with event-focused context
        events_context = f"""
=== WEBSITE INFORMATION ===
{' '.join(web_docs_events)}

=== PRODUCT INFORMATION ===
{' '.join(product_docs_events)}

=== JOB POSTINGS ===
{' '.join(job_docs_events)}

=== NEWS & EVENTS ===
{' '.join(news_docs_events)}
"""
        print(f"3. Extracting recent_events from all sources: Web={len(web_docs_events)}, Product={len(product_docs_events)}, Job={len(job_docs_events)}, News={len(news_docs_events)}")
        recent_events = extract_recent_events(events_context) if any([web_docs_events, product_docs_events, job_docs_events, news_docs_events]) else []
        
        # Merge all extracted fields
        extracted_fields = {
            "business_summary": overview_fields.get("business_summary", ""),
            "product_lines": overview_fields.get("product_lines", []),
            "target_industries": overview_fields.get("target_industries", []),
            "regions": overview_fields.get("regions", []),
            "hiring_focus": hiring_focus,
            "key_recent_events": recent_events
        }
        
        # Track which sources contributed to each field (based on which sources had data)
        field_sources = {}
        
        # Business overview fields: track which sources provided chunks
        sources_for_overview = []
        if web_docs_business:
            sources_for_overview.append("website")
        if product_docs_business:
            sources_for_overview.append("product")
        if job_docs_business:
            sources_for_overview.append("jobs")
        if news_docs_business:
            sources_for_overview.append("news")
        
        field_sources["business_summary"] = sources_for_overview if extracted_fields["business_summary"] else []
        field_sources["product_lines"] = sources_for_overview if extracted_fields["product_lines"] else []
        field_sources["target_industries"] = sources_for_overview if extracted_fields["target_industries"] else []
        field_sources["regions"] = sources_for_overview if extracted_fields["regions"] else []
        
        # Hiring focus: track which sources provided chunks
        sources_for_hiring = []
        if web_docs_hiring:
            sources_for_hiring.append("website")
        if product_docs_hiring:
            sources_for_hiring.append("product")
        if job_docs_hiring:
            sources_for_hiring.append("jobs")
        if news_docs_hiring:
            sources_for_hiring.append("news")
        
        field_sources["hiring_focus"] = sources_for_hiring if extracted_fields["hiring_focus"] else []
        
        # Recent events: track which sources provided chunks
        sources_for_events = []
        if web_docs_events:
            sources_for_events.append("website")
        if product_docs_events:
            sources_for_events.append("product")
        if job_docs_events:
            sources_for_events.append("jobs")
        if news_docs_events:
            sources_for_events.append("news")
        
        field_sources["key_recent_events"] = sources_for_events if extracted_fields["key_recent_events"] else []
        
        # Calculate confidence scores
        confidence_scores = calculate_confidence(field_sources)
        
        print(f"✅ EXTRACTION COMPLETE:")
        print(f"   - Business summary: {len(extracted_fields['business_summary'])} chars (confidence: {confidence_scores.get('business_summary', 0)})")
        print(f"   - Product lines: {len(extracted_fields['product_lines'])} items (confidence: {confidence_scores.get('product_lines', 0)})")
        print(f"   - Industries: {len(extracted_fields['target_industries'])} items (confidence: {confidence_scores.get('target_industries', 0)})")
        print(f"   - Regions: {len(extracted_fields['regions'])} items (confidence: {confidence_scores.get('regions', 0)})")
        print(f"   - Hiring focus: {len(extracted_fields['hiring_focus'])} roles (confidence: {confidence_scores.get('hiring_focus', 0)})")
        print(f"   - Recent events: {len(extracted_fields['key_recent_events'])} events (confidence: {confidence_scores.get('key_recent_events', 0)})")
        print("="*80 + "\n")
        
        # Step 5: SEMANTIC INDUSTRY CLASSIFICATION MATCHING
        print("\n" + "="*80)
        print("INDUSTRY CLASSIFICATION MATCHING:")
        print("="*80)
        
        # Create combined company text for matching
        combined_company_text = f"""
{extracted_fields.get('business_summary', '')}
Products: {', '.join(extracted_fields.get('product_lines', []))}
Industries: {', '.join(extracted_fields.get('target_industries', []))}
"""
        
        # Match company to industry classification
        matcher = get_industry_matcher()
        industry_match = matcher.match_company(combined_company_text, company_name)
        
        if industry_match:
            print(f"✅ Industry Match Found:")
            print(f"   - Matched Level: {industry_match['matched_level']}")
            print(f"   - Sector: {industry_match['sector']}")
            print(f"   - Industry: {industry_match['industry']}")
            print(f"   - Sub-Industry: {industry_match['sub_industry']}")
            print(f"   - SIC Code: {industry_match['sic_code']}")
            print(f"   - Confidence: {industry_match['confidence']:.3f}")
            print("="*80 + "\n")
            
            # Store industry mapping in MongoDB
            insert_industry_mapping(
                company_name=company_name,
                company_domain=company_domain,  # Use actual domain from frontend
                matched_level=industry_match['matched_level'],
                sector=industry_match['sector'],
                industry=industry_match['industry'],
                sub_industry=industry_match['sub_industry'],
                sic_code=industry_match['sic_code'],
                sic_description=industry_match['sic_description'],
                confidence=industry_match['confidence']
            )
        else:
            print("⚠️ No industry classification match found")
            print("="*80 + "\n")
        
        # Step 6: Store in MongoDB with confidence scores
        profile_id = insert_company_profile(company_name, extracted_fields, confidence_scores)
        
        # Step 7: Return unified profile with confidence scores
        profile = get_company_profile(company_name)
        
        # Format response with confidence scores
        profile_with_confidence = {
            "business_summary": {
                "value": profile['extracted_fields'].get('business_summary', ''),
                "confidence": profile.get('confidence_scores', {}).get('business_summary', 0.0)
            },
            "product_lines": {
                "value": profile['extracted_fields'].get('product_lines', []),
                "confidence": profile.get('confidence_scores', {}).get('product_lines', 0.0)
            },
            "target_industries": {
                "value": profile['extracted_fields'].get('target_industries', []),
                "confidence": profile.get('confidence_scores', {}).get('target_industries', 0.0)
            },
            "regions": {
                "value": profile['extracted_fields'].get('regions', []),
                "confidence": profile.get('confidence_scores', {}).get('regions', 0.0)
            },
            "hiring_focus": {
                "value": profile['extracted_fields'].get('hiring_focus', []),
                "confidence": profile.get('confidence_scores', {}).get('hiring_focus', 0.0)
            },
            "key_recent_events": {
                "value": profile['extracted_fields'].get('key_recent_events', []),
                "confidence": profile.get('confidence_scores', {}).get('key_recent_events', 0.0)
            }
        }
        
        return ProfileResponse(
            company_name=profile['company_name'],
            profile=profile_with_confidence,
            created_at=profile['created_at'].isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{company_name}", response_model=ProfileResponse)
async def get_profile(company_name: str):
    """
    Retrieve existing company profile from MongoDB with confidence scores.
    """
    try:
        profile = get_company_profile(company_name)
        
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Profile not found for company: {company_name}"
            )
        
        # Format response with confidence scores
        profile_with_confidence = {
            "business_summary": {
                "value": profile['extracted_fields'].get('business_summary', ''),
                "confidence": profile.get('confidence_scores', {}).get('business_summary', 0.0)
            },
            "product_lines": {
                "value": profile['extracted_fields'].get('product_lines', []),
                "confidence": profile.get('confidence_scores', {}).get('product_lines', 0.0)
            },
            "target_industries": {
                "value": profile['extracted_fields'].get('target_industries', []),
                "confidence": profile.get('confidence_scores', {}).get('target_industries', 0.0)
            },
            "regions": {
                "value": profile['extracted_fields'].get('regions', []),
                "confidence": profile.get('confidence_scores', {}).get('regions', 0.0)
            },
            "hiring_focus": {
                "value": profile['extracted_fields'].get('hiring_focus', []),
                "confidence": profile.get('confidence_scores', {}).get('hiring_focus', 0.0)
            },
            "key_recent_events": {
                "value": profile['extracted_fields'].get('key_recent_events', []),
                "confidence": profile.get('confidence_scores', {}).get('key_recent_events', 0.0)
            }
        }
        
        return ProfileResponse(
            company_name=profile['company_name'],
            profile=profile_with_confidence,
            created_at=profile['created_at'].isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
