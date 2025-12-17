# Multi-Source B2B Data Fusion Engine - Backend

Complete backend implementation for the B2B Data Fusion hackathon project.

## Project Structure

```
backend/
├── main.py                      # FastAPI application entry point
├── config.py                    # Configuration and environment variables
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
│
├── models/
│   └── schemas.py              # Pydantic request/response models
│
├── routes/
│   ├── website_routes.py       # Website data upload endpoint
│   ├── product_routes.py       # Product brochure upload endpoint
│   ├── job_routes.py           # Job post upload endpoint
│   ├── news_routes.py          # News upload endpoint
│   └── profile_routes.py       # Unified profile generation endpoint
│
├── utils/
│   ├── scraper.py              # ZenRows API scraping utility
│   ├── html_parser.py          # BeautifulSoup HTML parsing & text cleaning
│   └── pdf_parser.py           # PyPDF2 PDF text extraction
│
├── database/
│   ├── chromadb_setup.py       # ChromaDB initialization (4 collections)
│   └── mongodb_setup.py        # MongoDB connection & operations
│
└── services/
    └── llm_service.py          # Ollama/tinyllama integration
```

## Tech Stack

- **Backend**: FastAPI
- **Scraping**: ZenRows API
- **HTML Parsing**: BeautifulSoup
- **PDF Parsing**: PyPDF2
- **Vector DB**: ChromaDB (4 collections: web_db, product_db, job_db, news_db)
- **Embeddings**: ChromaDB default embeddings
- **LLM**: tinyllama via Ollama
- **Database**: MongoDB

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
ZENROWS_API_KEY=your_actual_zenrows_api_key
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=b2b_fusion
CHROMADB_PATH=./chroma_data
OLLAMA_MODEL=tinyllama
```

### 3. Install & Start MongoDB

Make sure MongoDB is running locally:
```bash
# Install MongoDB: https://www.mongodb.com/docs/manual/installation/
# Start MongoDB
mongod
```

### 4. Install & Start Ollama with tinyllama

```bash
# Install Ollama: https://ollama.ai/
# Pull tinyllama model
ollama pull tinyllama

# Ollama server should auto-start
```

### 5. Run the Backend

```bash
python main.py
```

Server runs at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## API Endpoints

### 1. Website Data Upload
**POST** `/api/website/upload`

Request body:
```json
{
  "company_name": "TechCorp",
  "url": "https://example.com",           // Option A
  "html_content": "<html>...</html>",      // Option B
  "plain_text": "Company description..."   // Option C
}
```

### 2. Product Brochure Upload
**POST** `/api/product/upload`

Form data:
- `company_name`: string (required)
- `pdf_file`: file (PDF brochure)
- `plain_text`: string (alternative to PDF)

### 3. Job Post Upload
**POST** `/api/job/upload`

Request body:
```json
{
  "company_name": "TechCorp",
  "job_text": "Software Engineer role...",  // Option A
  "job_url": "https://jobs.example.com"     // Option B
}
```

### 4. News Upload
**POST** `/api/news/upload`

Request body:
```json
{
  "company_name": "TechCorp",
  "news_text": "Company announced...",      // Option A
  "news_url": "https://news.example.com"    // Option B
}
```

### 5. Generate Unified Profile
**POST** `/api/profile/generate`

Request body:
```json
{
  "company_name": "TechCorp"
}
```

Response:
```json
{
  "company_name": "TechCorp",
  "extracted_fields": {
    "business_summary": "...",
    "product_lines": ["Product A", "Product B"],
    "target_industries": ["Tech", "Finance"],
    "regions": ["North America", "Europe"],
    "hiring_focus": "...",
    "key_recent_events": ["Event 1", "Event 2"]
  },
  "created_at": "2025-12-17T10:30:00"
}
```

### 6. Get Existing Profile
**GET** `/api/profile/{company_name}`

## How It Works

### Data Flow

1. **Upload Phase** (Endpoints 1-4):
   - User provides data via 4 different upload endpoints
   - Data is scraped (if URL), parsed, and cleaned
   - Text chunks are embedded and stored in respective ChromaDB collections
   - Metadata includes `company_name` and `source` for filtering

2. **Processing Phase** (Endpoint 5):
   - Retrieve all documents for the company from 4 collections
   - Combine into a structured context string
   - Send to tinyllama via Ollama
   - LLM extracts structured JSON with required fields
   - Store unified profile in MongoDB

3. **Output Phase**:
   - Return structured company profile to frontend
   - Profile includes: business summary, products, industries, regions, hiring focus, recent events

## ChromaDB Collections

- **web_db**: Website content and company overview
- **product_db**: Product brochures and descriptions
- **job_db**: Job postings and hiring information
- **news_db**: News articles and recent events

Each document stores:
- Text chunk
- Automatic embedding (ChromaDB default)
- Metadata: `{ company_name, source }`

## MongoDB Schema

Collection: `company_profiles`

```json
{
  "company_name": "string",
  "extracted_fields": {
    "business_summary": "string",
    "product_lines": ["array"],
    "target_industries": ["array"],
    "regions": ["array"],
    "hiring_focus": "string",
    "key_recent_events": ["array"]
  },
  "created_at": "datetime"
}
```

## Testing the API

Use the interactive docs at `http://localhost:8000/docs` or test with curl:

```bash
# 1. Upload website data
curl -X POST http://localhost:8000/api/website/upload \
  -H "Content-Type: application/json" \
  -d '{"company_name": "TechCorp", "plain_text": "TechCorp builds AI solutions..."}'

# 2. Upload product data
curl -X POST http://localhost:8000/api/product/upload \
  -F "company_name=TechCorp" \
  -F "plain_text=Our flagship product is..."

# 3. Upload job data
curl -X POST http://localhost:8000/api/job/upload \
  -H "Content-Type: application/json" \
  -d '{"company_name": "TechCorp", "job_text": "Hiring Senior Engineers..."}'

# 4. Upload news data
curl -X POST http://localhost:8000/api/news/upload \
  -H "Content-Type: application/json" \
  -d '{"company_name": "TechCorp", "news_text": "TechCorp announced Series B..."}'

# 5. Generate unified profile
curl -X POST http://localhost:8000/api/profile/generate \
  -H "Content-Type: application/json" \
  -d '{"company_name": "TechCorp"}'
```

## Notes

- All processing runs locally (no cloud services)
- ZenRows API requires valid API key for URL scraping
- Ollama must be running with tinyllama model pulled
- MongoDB must be running locally
- ChromaDB data persists in `./chroma_data` directory
- Hackathon-friendly: simple, modular, readable code

## Next Steps (Frontend Integration)

The frontend should:
1. Provide 4 upload sections (Website, Product, Jobs, News)
2. Allow users to input data via URL, file upload, or text
3. Display unified profile as structured cards
4. Show: Summary, Products, Industries, Regions, Hiring Focus, Recent Events
