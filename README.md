# Multi-Source B2B Data Fusion Engine

Complete hackathon project: Backend + Frontend for intelligent company profile generation from multiple data sources.

## 🎯 Project Overview

This system aggregates data from multiple sources (websites, product brochures, job postings, news articles) and uses AI to generate a unified, structured company profile.

**Tech Stack:**
- Backend: Python + FastAPI
- Frontend: React.js
- Scraping: ZenRows API
- Vector DB: ChromaDB (4 collections)
- LLM: Tinyllama via Ollama
- Database: MongoDB
- Parsing: BeautifulSoup + PyPDF2

## 📁 Project Structure

```
B@B/
├── backend/                    # Python FastAPI backend
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── utils/
│   ├── database/
│   └── services/
│
└── frontend/                   # React.js frontend
    ├── public/
    ├── src/
    │   ├── components/
    │   ├── services/
    │   ├── App.js
    │   └── index.js
    └── package.json
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+**
2. **Node.js 16+**
3. **MongoDB** - Running locally
4. **Ollama** - With tinyllama model
5. **ZenRows API Key**

### Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ZenRows API key

# Start MongoDB
mongod

# Pull tinyllama model
ollama pull tinyllama

# Run backend
python main.py
```

Backend runs at: **http://localhost:8000**

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start frontend
npm start
```

Frontend runs at: **http://localhost:3000**

## 💡 How to Use

### 1. Enter Company Name
Start by entering the company name at the top of the page.

### 2. Upload Data (Use Any or All Sources)

**📌 Website Data**
- Option A: Paste website URL (scraped via ZenRows)
- Option B: Paste raw HTML
- Option C: Paste plain text

**📦 Product Brochure**
- Option A: Upload PDF file
- Option B: Paste product text

**💼 Job Postings**
- Option A: Paste job post URL
- Option B: Paste job post text

**📰 News & Events**
- Option A: Paste news URL
- Option B: Paste news text

### 3. Generate Unified Profile
Click **"Generate Unified Profile"** button.

### 4. View Results
See the AI-generated company profile with:
- Business summary
- Product lines
- Target industries
- Regions
- Hiring focus
- Key recent events

## 🔄 System Flow

```
User Uploads → FastAPI Endpoints → Parse/Clean → ChromaDB Storage
                                                        ↓
MongoDB ← Extract JSON ← Tinyllama LLM ← Retrieve & Combine Context
              ↓
        Display Profile
```

### Data Processing

1. **Upload Phase**: Data is scraped, parsed, cleaned, and embedded in ChromaDB
2. **Storage**: Text chunks stored in 4 separate collections (web_db, product_db, job_db, news_db)
3. **Retrieval**: All company data retrieved using metadata filters
4. **AI Processing**: Combined context sent to tinyllama for structured extraction
5. **Storage**: Final profile saved to MongoDB
6. **Display**: Structured profile shown in React frontend

## 📊 ChromaDB Collections

| Collection | Purpose | Source Types |
|------------|---------|--------------|
| `web_db` | Website content | URL, HTML, Text |
| `product_db` | Product information | PDF, Text |
| `job_db` | Job postings | URL, Text |
| `news_db` | News & events | URL, Text |

## 🔌 API Endpoints

### Upload Endpoints
- `POST /api/website/upload` - Upload website data
- `POST /api/product/upload` - Upload product brochure
- `POST /api/job/upload` - Upload job posting
- `POST /api/news/upload` - Upload news article

### Profile Endpoints
- `POST /api/profile/generate` - Generate unified profile
- `GET /api/profile/{company_name}` - Retrieve existing profile

## 🎨 Frontend Features

✅ **Four Upload Sections** - All on one page
✅ **Multiple Input Types** - URL, File, HTML, Text
✅ **Upload Status Tracking** - See how many sources uploaded
✅ **Profile Display** - Beautiful cards with structured data
✅ **Responsive Design** - Works on all devices
✅ **Real-time Feedback** - Success/error messages
✅ **Modern UI** - Gradient backgrounds, smooth animations

## 🛠️ Technology Details

### ZenRows Integration
```python
params = {"url": user_url, "apikey": ZENROWS_API_KEY}
response = requests.get("https://api.zenrows.com/v1/", params=params)
```

### Ollama/Tinyllama Integration
```python
response = ollama.chat(
    model="tinyllama",
    messages=[{"role": "user", "content": prompt}]
)
```

### ChromaDB Vector Storage
- Automatic embeddings (default ChromaDB model)
- Metadata filtering by company_name
- Four separate collections for organized storage

### MongoDB Schema
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

## 📝 Example Usage

```bash
# Upload website data
curl -X POST http://localhost:8000/api/website/upload \
  -H "Content-Type: application/json" \
  -d '{"company_name": "TechCorp", "plain_text": "TechCorp builds AI solutions..."}'

# Generate profile
curl -X POST http://localhost:8000/api/profile/generate \
  -H "Content-Type: application/json" \
  -d '{"company_name": "TechCorp"}'
```

## 🐛 Troubleshooting

**Backend won't start:**
- Check if MongoDB is running: `mongod`
- Check if Ollama is running: `ollama list`
- Verify all dependencies installed: `pip install -r requirements.txt`

**Frontend can't connect:**
- Ensure backend is running on port 8000
- Check CORS settings in backend `main.py`

**Profile generation fails:**
- Verify tinyllama model is pulled: `ollama pull tinyllama`
- Check if data was uploaded for the company
- Ensure MongoDB is accessible

## 📚 Documentation

- [Backend README](backend/README.md) - Detailed backend documentation
- [Frontend README](frontend/README.md) - Detailed frontend documentation

## 🎯 Hackathon-Ready

- ✅ No cloud services required
- ✅ Runs completely locally
- ✅ Simple setup process
- ✅ Clean, modular code
- ✅ No overengineering
- ✅ Clear documentation
- ✅ Ready to demo

## 📄 License

MIT License - Free for hackathon use

## 🤝 Contributing

This is a hackathon project. Feel free to fork and modify!

---

**Built with ❤️ for hackathons**
