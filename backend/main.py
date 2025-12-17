from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from routes import website_routes, product_routes, job_routes, news_routes, profile_routes
from database.chromadb_setup import init_chromadb
from database.mongodb_setup import init_mongodb

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
    print("✅ ChromaDB and MongoDB initialized")

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
