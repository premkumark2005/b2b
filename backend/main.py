from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from pathlib import Path

from routes import website_routes, product_routes, job_routes, news_routes, profile_routes
from database.chromadb_setup import init_chromadb, get_embedding_model
from database.mongodb_setup import init_mongodb
from services.industry_matcher import init_industry_matcher

app = FastAPI(title="B2B Data Fusion Engine")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize databases on startup
@app.on_event("startup")
async def startup_event():
    init_chromadb()
    init_mongodb()
    
    # Initialize industry matcher with CSV path and embedding model
    csv_path = Path(__file__).parent.parent / "sub_Industry_Classification(in).csv"
    embedding_model = get_embedding_model()
    init_industry_matcher(str(csv_path), embedding_model)
    
    print("✅ ChromaDB, MongoDB, and Industry Matcher initialized")

# Health check
@app.get("/")
def health_check():
    return {"status": "B2B Data Fusion Engine is running"}

# Include routers
app.include_router(website_routes.router, prefix="/api/website", tags=["Website"])
app.include_router(product_routes.router, prefix="/api/product", tags=["Product"])
app.include_router(job_routes.router, prefix="/api/job", tags=["Job"])
app.include_router(news_routes.router, prefix="/api/news", tags=["News"])
app.include_router(profile_routes.router, prefix="/api/profile", tags=["Profile"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
