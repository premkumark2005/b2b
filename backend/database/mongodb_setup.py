from pymongo import MongoClient
from config import MONGODB_URI, MONGODB_DB
from datetime import datetime
from typing import Optional, Dict

# Global MongoDB client
mongo_client = None
db = None
profiles_collection = None
industry_mapping_collection = None

def init_mongodb():
    """
    Initialize MongoDB connection and create collections.
    """
    global mongo_client, db, profiles_collection, industry_mapping_collection
    
    mongo_client = MongoClient(MONGODB_URI)
    db = mongo_client[MONGODB_DB]
    profiles_collection = db['company_profiles']
    industry_mapping_collection = db['company_industry_mapping']
    
    print(f"✅ MongoDB connected: {MONGODB_DB}")

def get_profiles_collection():
    return profiles_collection

def get_industry_mapping_collection():
    return industry_mapping_collection

def insert_company_profile(company_name: str, extracted_fields: dict, confidence_scores: dict = None):
    """
    Store/update final unified profile in MongoDB with confidence scores.
    Uses replace_one with upsert=True to replace old profile with new one.
    
    Schema:
    {
        company_name: str,
        extracted_fields: {
            business_summary: str,
            product_lines: list,
            target_industries: list,
            regions: list,
            hiring_focus: list,
            key_recent_events: list
        },
        confidence_scores: {
            business_summary: float,
            product_lines: float,
            target_industries: float,
            regions: float,
            hiring_focus: float,
            key_recent_events: float
        },
        created_at: datetime,
        updated_at: datetime
    }
    """
    profile = {
        "company_name": company_name,
        "extracted_fields": extracted_fields,
        "confidence_scores": confidence_scores or {},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Replace existing profile or insert new one (upsert)
    result = profiles_collection.replace_one(
        {"company_name": company_name},
        profile,
        upsert=True
    )
    
    if result.upserted_id:
        return str(result.upserted_id)
    else:
        # If updated existing, get the _id
        existing = profiles_collection.find_one({"company_name": company_name})
        if existing and '_id' in existing:
            return str(existing['_id'])
        else:
            raise Exception(f"Failed to retrieve profile ID for company: {company_name}")

def get_company_profile(company_name: str):
    """
    Retrieve company profile from MongoDB.
    """
    profile = profiles_collection.find_one(
        {"company_name": company_name},
        sort=[("created_at", -1)]
    )
    
    if profile:
        profile['_id'] = str(profile['_id'])
    
    return profile

def insert_industry_mapping(
    company_name: str,
    company_domain: str,
    matched_level: str,
    sector: str,
    industry: str,
    sub_industry: str,
    sic_code: str,
    sic_description: str,
    confidence: float
) -> str:
    """
    Store industry classification mapping for a company.
    
    Args:
        company_name: Name of the company
        company_domain: Company website domain
        matched_level: Level at which match occurred (sector/Industry/sub_industry)
        sector: Matched sector
        industry: Matched industry
        sub_industry: Matched sub-industry
        sic_code: SIC code
        sic_description: SIC description
        confidence: Similarity confidence score (0-1)
        
    Returns:
        str: ID of inserted/updated document
    """
    mapping = {
        "company_name": company_name,
        "company_domain": company_domain,
        "matched_level": matched_level,
        "sector": sector,
        "industry": industry,
        "sub_industry": sub_industry,
        "sic_code": sic_code,
        "sic_description": sic_description,
        "confidence": confidence,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Replace existing mapping or insert new one (upsert)
    result = industry_mapping_collection.replace_one(
        {"company_name": company_name},
        mapping,
        upsert=True
    )
    
    if result.upserted_id:
        return str(result.upserted_id)
    else:
        # If updated existing, get the _id
        existing = industry_mapping_collection.find_one({"company_name": company_name})
        if existing and '_id' in existing:
            return str(existing['_id'])
        else:
            raise Exception(f"Failed to retrieve industry mapping ID for company: {company_name}")

def get_industry_mapping(company_name: str) -> Optional[Dict]:
    """
    Retrieve industry classification mapping for a company.
    
    Args:
        company_name: Name of the company
        
    Returns:
        Dict with mapping data or None if not found
    """
    mapping = industry_mapping_collection.find_one(
        {"company_name": company_name},
        sort=[("created_at", -1)]
    )
    
    if mapping:
        mapping['_id'] = str(mapping['_id'])
    
    return mapping
