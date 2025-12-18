# Industry Classification Matching System

## Overview
Semantic industry classification matching system that maps companies to standard industry classifications using embeddings and cosine similarity.

## How It Works

### 1. **Data Loading**
- Loads `sub_Industry_Classification(in).csv` with 3682 industry classifications
- Contains: sector, industry, sub_industry, sic_code, sic_description
- Example row: "Cloud Infrastructure" → "Information Technology" → "Software Development"

### 2. **Embedding Generation**
- Uses the **same SentenceTransformer model** (paraphrase-MiniLM-L3-v2) as ChromaDB
- Generates embeddings for:
  - All unique sectors (broad categories)
  - All unique industries (general categories)
  - All unique sub-industries (specific categories)
- Stored in dictionaries for fast lookup

### 3. **Matching Priority**
When a company profile is generated:
1. **Try SECTOR first** (threshold: 0.65)
   - Broadest match (e.g., "Healthcare", "Technology")
2. **Try SUB_INDUSTRY** (threshold: 0.70)
   - Most specific match (e.g., "Cloud Infrastructure", "Pharmacy")
3. **Fall back to INDUSTRY** (threshold: 0.65)
   - General match (e.g., "Software Development", "Health Care Providers")

### 4. **Semantic Matching**
- Creates company text from: business_summary + products + industries
- Generates embedding for company text
- Calculates **cosine similarity** with all candidates
- Returns best match if above threshold

### 5. **MongoDB Storage**
Matched classification stored in `company_industry_mapping` collection:
```javascript
{
  company_name: "Zoho Corporation",
  company_domain: "zohocorporation",
  matched_level: "sector",  // Which level matched
  sector: "Information Technology",
  industry: "Software Development & Services",
  sub_industry: "Accounting Software",
  sic_code: "62012",
  sic_description: "Business and domestic software development",
  confidence: 0.78,  // Similarity score (0-1)
  created_at: ISODate("2025-12-18T...")
}
```

## Example Matching

### Company Input:
```
Business: "Zoho builds software for sales, marketing, support, finance, HR"
Products: ["Zoho CRM", "Zoho Books", "Zoho Invoice"]
Industries: ["Technology", "SMEs"]
```

### Matching Process:
1. Generate embedding for combined text
2. Compare with sector embeddings
3. **Match found**: "Information Technology" (confidence: 0.78)
4. Retrieve full classification row from dataset
5. Store in MongoDB

## Integration

### Backend Flow:
```
1. User uploads company data (website, product, jobs, news)
2. Profile generation extracts fields
3. **NEW**: Industry matcher runs automatically
4. Matched classification stored in MongoDB
5. Profile returned with industry info
```

### Files Modified:
- ✅ `services/industry_matcher.py` - Core matching logic
- ✅ `database/mongodb_setup.py` - New collection + functions
- ✅ `database/chromadb_setup.py` - Expose embedding model
- ✅ `routes/profile_routes.py` - Integration in profile generation
- ✅ `main.py` - Initialize matcher on startup
- ✅ `requirements.txt` - Add pandas, scikit-learn, numpy

## Usage

### Automatic (Recommended):
Industry matching happens automatically when generating a profile:
```python
POST /api/profile/generate
{
  "company_name": "Zoho Corporation"
}
```

### Retrieve Mapping:
```python
from database.mongodb_setup import get_industry_mapping

mapping = get_industry_mapping("Zoho Corporation")
print(f"Sector: {mapping['sector']}")
print(f"SIC Code: {mapping['sic_code']}")
print(f"Confidence: {mapping['confidence']}")
```

## Key Features

✅ **Semantic Matching**: Meaning-based, not keyword matching
✅ **Hierarchical Fallback**: sector → sub_industry → industry
✅ **Confidence Scoring**: Returns similarity score (0-1)
✅ **Reuses Existing Model**: Same embedding model as ChromaDB
✅ **MongoDB Storage**: Persistent industry mappings
✅ **Automatic Integration**: Runs during profile generation

## Example Matches

| Company Description | Matched Sector | Sub-Industry | Confidence |
|---------------------|----------------|--------------|-----------|
| "pharmacy software" | Healthcare | Pharmacy Software | 0.82 |
| "cloud infrastructure" | Information Technology | Cloud Services | 0.79 |
| "manufacturing robots" | Manufacturing & Industrials | Robotics | 0.75 |
| "legal consulting" | Professional Services | Legal Services | 0.77 |

## Thresholds

- **Sector**: 0.65 (lower threshold for broad categories)
- **Sub-Industry**: 0.70 (higher threshold for specific matches)
- **Industry**: 0.65 (medium threshold for general categories)

Adjust in `services/industry_matcher.py` → `THRESHOLDS` dict.
