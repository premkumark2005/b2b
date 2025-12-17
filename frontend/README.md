# Multi-Source B2B Data Fusion Engine - Frontend

React.js frontend for the B2B Data Fusion hackathon project.

## Project Structure

```
frontend/
├── public/
│   └── index.html              # HTML template
│
├── src/
│   ├── components/
│   │   ├── WebsiteUpload.js    # Website data upload component
│   │   ├── ProductUpload.js    # Product brochure upload component
│   │   ├── JobUpload.js        # Job posting upload component
│   │   ├── NewsUpload.js       # News upload component
│   │   ├── ProfileDisplay.js   # Unified profile display
│   │   └── WebsiteUpload.css   # Shared styles for upload components
│   │   └── ProfileDisplay.css  # Profile display styles
│   │
│   ├── services/
│   │   └── api.js              # API service for backend communication
│   │
│   ├── App.js                  # Main application component
│   ├── App.css                 # Main application styles
│   ├── index.js                # React entry point
│   └── index.css               # Global styles
│
└── package.json                # Dependencies
```

## Tech Stack

- **Framework**: React.js 18
- **HTTP Client**: Axios
- **Styling**: Pure CSS (no framework)
- **Build Tool**: React Scripts (Create React App)

## Features

### Four Upload Sections

1. **📌 Website Data**
   - URL scraping (via ZenRows)
   - Raw HTML content
   - Plain text

2. **📦 Product Brochure**
   - PDF file upload
   - Plain text

3. **💼 Job Postings**
   - Job post URL
   - Job post text

4. **📰 News & Events**
   - News URL
   - News text

### Unified Profile Display

Displays extracted company information:
- Business Summary (highlighted card)
- Product Lines
- Target Industries
- Regions
- Hiring Focus
- Key Recent Events

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm start
```

Frontend runs at: `http://localhost:3000`

### 3. Ensure Backend is Running

Make sure the FastAPI backend is running at `http://localhost:8000` before using the frontend.

## User Workflow

### Step 1: Enter Company Name
Enter the company name in the input field at the top.

### Step 2: Upload Data from Multiple Sources
Use any or all of the four upload sections:
- **Website**: Provide URL, HTML, or text
- **Product**: Upload PDF or paste text
- **Jobs**: Provide job URL or text
- **News**: Provide news URL or text

Each upload is independent - you can use all four or just one.

### Step 3: Generate Unified Profile
Click the **"✨ Generate Unified Profile"** button.

The system will:
1. Retrieve data from all 4 ChromaDB collections
2. Combine context and send to tinyllama
3. Extract structured fields
4. Display the unified profile

### Step 4: View Results
The unified profile appears below with:
- Business summary card
- Structured fields in grid layout
- Clear, readable information

## API Integration

All API calls use the `services/api.js` module:

```javascript
// Upload functions
uploadWebsiteData(data)
uploadProductData(formData)
uploadJobData(data)
uploadNewsData(data)

// Profile generation
generateProfile(companyName)
getProfile(companyName)
```

Backend URL is configured in `api.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

## Component Architecture

### App.js
- Main application container
- Manages company name state
- Coordinates upload components
- Handles profile generation
- Displays results

### Upload Components
Each upload component:
- Accepts company name as prop
- Provides input type selection
- Handles form submission
- Shows success/error messages
- Calls `onSuccess` callback

### ProfileDisplay
- Receives profile data as prop
- Renders summary card
- Displays structured fields in grid
- Handles missing data gracefully

## Styling

### Design System
- **Primary Gradient**: Purple to violet (#667eea → #764ba2)
- **Accent Gradient**: Pink to red (#f093fb → #f5576c)
- **Background**: Gradient background
- **Cards**: White with rounded corners and shadows
- **Interactive**: Hover effects and smooth transitions

### Responsive Design
- Mobile-friendly grid layouts
- Adapts to different screen sizes
- Touch-friendly buttons and inputs

## Testing the Frontend

### 1. Test Website Upload
```
Company Name: TechCorp
Input Type: Plain Text
Content: "TechCorp is a leading AI solutions provider..."
```

### 2. Test Product Upload
```
Company Name: TechCorp
Input Type: Plain Text
Content: "Our flagship product is an AI-powered analytics platform..."
```

### 3. Test Job Upload
```
Company Name: TechCorp
Input Type: Job Text
Content: "Hiring Senior Software Engineers with Python and AI experience..."
```

### 4. Test News Upload
```
Company Name: TechCorp
Input Type: News Text
Content: "TechCorp announced Series B funding of $50M..."
```

### 5. Generate Profile
Click "Generate Unified Profile" button and view the results.

## Build for Production

```bash
npm run build
```

Creates optimized production build in `build/` directory.

## Environment Configuration

To change the backend URL, edit `src/services/api.js`:

```javascript
const API_BASE_URL = 'http://your-backend-url/api';
```

## Key Features

✅ Four upload sections on a single page
✅ Multiple input types per section (URL/File/Text)
✅ Real-time upload status tracking
✅ Clean, modern UI with gradient design
✅ Responsive grid layout
✅ Error handling and user feedback
✅ Structured profile display
✅ Summary card highlighting
✅ List rendering for arrays
✅ Mobile-friendly design

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Notes

- Frontend expects backend at `http://localhost:8000`
- CORS is configured in backend for `http://localhost:3000`
- All data processing happens on backend
- Frontend is purely presentation and data collection
- No authentication required (hackathon build)

## Next Steps

For production deployment:
1. Configure production API URL
2. Add environment variables
3. Implement authentication
4. Add loading states
5. Improve error handling
6. Add data validation
7. Implement file size limits
8. Add progress indicators for uploads
