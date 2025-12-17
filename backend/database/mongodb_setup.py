from pymongo import MongoClient
from config import MONGODB_URI, MONGODB_DB
from datetime import datetime

# Global MongoDB client
mongo_client = None
db = None
profiles_collection = None

def init_mongodb():
    """
    Initialize MongoDB connection and create profiles collection.
    """
    global mongo_client, db, profiles_collection
    
    mongo_client = MongoClient(MONGODB_URI)
    db = mongo_client[MONGODB_DB]
    profiles_collection = db['company_profiles']
    
    print(f"✅ MongoDB connected: {MONGODB_DB}")

def get_profiles_collection():
    return profiles_collection

def insert_company_profile(company_name: str, extracted_fields: dict):
    """
    Store/update final unified profile in MongoDB.
    Uses replace_one with upsert=True to replace old profile with new one.
    
    Schema:
    {
        company_name: str,
        extracted_fields: {
            business_summary: str,
            product_lines: list,
            target_industries: list,
            regions: list,
            hiring_focus: str,
            key_recent_events: list
        },
        created_at: datetime,
        updated_at: datetime
    }
    """
    profile = {
        "company_name": company_name,
        "extracted_fields": extracted_fields,
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
        return str(existing['_id'])

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
