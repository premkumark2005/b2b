import React, { useState } from 'react';
import './WebsiteUpload.css';
import { uploadWebsiteData } from '../services/api';

const WebsiteUpload = ({ companyName, onSuccess }) => {
  const [inputType, setInputType] = useState('url');
  const [url, setUrl] = useState('');
  const [htmlContent, setHtmlContent] = useState('');
  const [plainText, setPlainText] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!companyName) {
      setMessage('⚠️ Please enter company name first');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const data = { company_name: companyName };
      
      if (inputType === 'url') {
        data.url = url;
      } else if (inputType === 'html') {
        data.html_content = htmlContent;
      } else {
        data.plain_text = plainText;
      }

      const response = await uploadWebsiteData(data);
      setMessage(`✅ ${response.message}`);
      
      // Clear form
      setUrl('');
      setHtmlContent('');
      setPlainText('');
      
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
              value="html"
              checked={inputType === 'html'}
              onChange={(e) => setInputType(e.target.value)}
            />
            HTML Content
          </label>
          <label>
            <input
              type="radio"
              value="text"
              checked={inputType === 'text'}
              onChange={(e) => setInputType(e.target.value)}
            />
            Plain Text
          </label>
        </div>

        {inputType === 'url' && (
          <input
            type="url"
            placeholder="Enter website URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
          />
        )}

        {inputType === 'html' && (
          <textarea
            placeholder="Paste HTML content here"
            value={htmlContent}
            onChange={(e) => setHtmlContent(e.target.value)}
            rows="6"
            required
          />
        )}

        {inputType === 'text' && (
          <textarea
            placeholder="Paste plain text content here"
            value={plainText}
            onChange={(e) => setPlainText(e.target.value)}
            rows="6"
            required
          />
        )}

        <button type="submit" disabled={loading}>
          {loading ? 'Uploading...' : 'Upload Website Data'}
        </button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default WebsiteUpload;
