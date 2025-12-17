import React, { useState } from 'react';
import './App.css';
import WebsiteUpload from './components/WebsiteUpload';
import ProductUpload from './components/ProductUpload';
import JobUpload from './components/JobUpload';
import NewsUpload from './components/NewsUpload';
import ProfileDisplay from './components/ProfileDisplay';
import { generateProfile } from './services/api';

function App() {
  const [companyName, setCompanyName] = useState('');
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [uploadCount, setUploadCount] = useState(0);

  const handleUploadSuccess = () => {
    setUploadCount(prev => prev + 1);
  };

  const handleGenerateProfile = async () => {
    if (!companyName) {
      setMessage('⚠️ Please enter a company name');
      return;
    }

    setLoading(true);
    setMessage('');
    setProfile(null);

    try {
      const result = await generateProfile(companyName);
      setProfile(result);
      setMessage('✅ Unified profile generated successfully!');
    } catch (error) {
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🚀 Multi-Source B2B Data Fusion Engine</h1>
        <p>Web + PDFs + Jobs + News → Unified Company Profile</p>
      </header>

      <div className="container">
        {/* Company Name Input */}
        <div className="company-input-section">
          <label htmlFor="companyName">Company Name:</label>
          <input
            id="companyName"
            type="text"
            placeholder="Enter company name (e.g., TechCorp)"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            className="company-input"
          />
          <p className="upload-status">
            {uploadCount > 0 ? `${uploadCount} data source(s) uploaded` : 'No data uploaded yet'}
          </p>
        </div>

        {/* Four Upload Sections */}
        <div className="upload-grid">
          <WebsiteUpload companyName={companyName} onSuccess={handleUploadSuccess} />
          <ProductUpload companyName={companyName} onSuccess={handleUploadSuccess} />
          <JobUpload companyName={companyName} onSuccess={handleUploadSuccess} />
          <NewsUpload companyName={companyName} onSuccess={handleUploadSuccess} />
        </div>

        {/* Generate Profile Button */}
        <div className="generate-section">
          <button
            className="generate-button"
            onClick={handleGenerateProfile}
            disabled={loading || !companyName}
          >
            {loading ? '🔄 Generating Profile...' : '✨ Generate Unified Profile'}
          </button>
          {message && <p className="generate-message">{message}</p>}
        </div>

        {/* Profile Display */}
        {profile && <ProfileDisplay profile={profile} />}
      </div>

      <footer className="app-footer">
        <p>Powered by ZenRows • ChromaDB • Tinyllama • MongoDB</p>
      </footer>
    </div>
  );
}

export default App;
