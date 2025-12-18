from pydantic import BaseModel
from typing import Optional

# Website Input Models
class WebsiteUploadRequest(BaseModel):
    company_name: str
    url: Optional[str] = None
    html_content: Optional[str] = None
    plain_text: Optional[str] = None

# Product Input Models
class ProductUploadRequest(BaseModel):
    company_name: str
    plain_text: Optional[str] = None
    # PDF file will be handled via form data

# Job Post Input Models
class JobUploadRequest(BaseModel):
    company_name: str
    job_text: Optional[str] = None
    job_url: Optional[str] = None

# News Input Models
class NewsUploadRequest(BaseModel):
    company_name: str
    news_text: Optional[str] = None
    news_url: Optional[str] = None

# Profile Generation Request
class ProfileGenerateRequest(BaseModel):
    company_name: str
    company_domain: Optional[str] = ""

# Response Models
class UploadResponse(BaseModel):
    status: str
    message: str
    company_name: str

class ProfileResponse(BaseModel):
    company_name: str
    profile: dict  # Contains fields with {"value": ..., "confidence": ...} structure
    created_at: str
