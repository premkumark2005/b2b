import React, { useState } from 'react';
import './WebsiteUpload.css';
import { uploadWebsiteData } from '../services/api';

const WebsiteUpload = ({ companyName, onSuccess }) => {
  const [inputType, setInputType] = useState('url');
  const [url, setUrl] = useState('');
  const [htmlFile, setHtmlFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!companyName) {
      setMessage('⚠️ Please enter company name first');
      return;
    }

    if (inputType === 'url' && !url) {
      setMessage('⚠️ Please enter website URL');
      return;
    }

    if (inputType === 'file' && !htmlFile) {
      setMessage('⚠️ Please select an HTML file');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const formData = new FormData();
      formData.append('company_name', companyName);
      
      if (inputType === 'url') {
        formData.append('url', url);
      } else {
        formData.append('html_file', htmlFile);
      }

      const response = await uploadWebsiteData(formData);
      setMessage(`✅ ${response.message}`);
      
      // Clear form
      setUrl('');
      setHtmlFile(null);
      
      if (onSuccess) onSuccess();
    } catch (error) {
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-section">
      <h2>📌 1. Website Data</h2>
      <form onSubmit={handleSubmit}>
        <div className="input-type-selector">
          <label>
            <input
              type="radio"
              value="url"
              checked={inputType === 'url'}
              onChange={(e) => setInputType(e.target.value)}
            />
            URL
          </label>
          <label>
            <input
              type="radio"
              value="file"
              checked={inputType === 'file'}
              onChange={(e) => setInputType(e.target.value)}
            />
            HTML File
          </label>
        </div>

        {inputType === 'url' && (
          <input
            type="url"
            placeholder="Enter website URL (e.g., https://nvidia.com)"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
          />
        )}

        {inputType === 'file' && (
          <div>
            <input
              type="file"
              accept=".html,.htm"
              onChange={(e) => setHtmlFile(e.target.files[0])}
              required
            />
            {htmlFile && <p className="file-name">📄 {htmlFile.name}</p>}
          </div>
        )}

        <button type="submit" disabled={loading}>
          {loading ? '⏳ Processing...' : '🚀 Upload Website Data'}
        </button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default WebsiteUpload;
