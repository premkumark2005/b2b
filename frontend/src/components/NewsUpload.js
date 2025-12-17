import React, { useState } from 'react';
import './WebsiteUpload.css';
import { uploadNewsData } from '../services/api';

const NewsUpload = ({ companyName, onSuccess }) => {
  const [inputType, setInputType] = useState('text');
  const [newsUrl, setNewsUrl] = useState('');
  const [newsText, setNewsText] = useState('');
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
        data.news_url = newsUrl;
      } else {
        data.news_text = newsText;
      }

      const response = await uploadNewsData(data);
      setMessage(`✅ ${response.message}`);
      
      // Clear form
      setNewsUrl('');
      setNewsText('');
      
      if (onSuccess) onSuccess();
    } catch (error) {
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-section">
      <h2>📰 4. News & Events</h2>
      <form onSubmit={handleSubmit}>
        <div className="input-type-selector">
          <label>
            <input
              type="radio"
              value="text"
              checked={inputType === 'text'}
              onChange={(e) => setInputType(e.target.value)}
            />
            News Text
          </label>
          <label>
            <input
              type="radio"
              value="url"
              checked={inputType === 'url'}
              onChange={(e) => setInputType(e.target.value)}
            />
            News URL
          </label>
        </div>

        {inputType === 'url' && (
          <input
            type="url"
            placeholder="Enter news article URL"
            value={newsUrl}
            onChange={(e) => setNewsUrl(e.target.value)}
            required
          />
        )}

        {inputType === 'text' && (
          <textarea
            placeholder="Paste news article text here"
            value={newsText}
            onChange={(e) => setNewsText(e.target.value)}
            rows="6"
            required
          />
        )}

        <button type="submit" disabled={loading}>
          {loading ? 'Uploading...' : 'Upload News Data'}
        </button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default NewsUpload;
