import React, { useState } from 'react';
import './WebsiteUpload.css';
import { uploadJobData } from '../services/api';

const JobUpload = ({ companyName, onSuccess }) => {
  const [inputType, setInputType] = useState('text');
  const [jobUrl, setJobUrl] = useState('');
  const [jobText, setJobText] = useState('');
  const [htmlFile, setHtmlFile] = useState(null);
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
      const formData = new FormData();
      formData.append('company_name', companyName);
      
      if (inputType === 'url') {
        formData.append('job_url', jobUrl);
      } else if (inputType === 'html') {
        formData.append('html_file', htmlFile);
      } else {
        formData.append('job_text', jobText);
      }

      const response = await uploadJobData(formData);
      setMessage(`✅ ${response.message}`);
      
      // Clear form
      setJobUrl('');
      setJobText('');
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
      <h2>💼 3. Job Postings</h2>
      <form onSubmit={handleSubmit}>
        <div className="input-type-selector">
          <label>
            <input
              type="radio"
              value="text"
              checked={inputType === 'text'}
              onChange={(e) => setInputType(e.target.value)}
            />
            Job Text
          </label>
          <label>
            <input
              type="radio"
              value="html"
              checked={inputType === 'html'}
              onChange={(e) => setInputType(e.target.value)}
            />
            HTML File
          </label>
          <label>
            <input
              type="radio"
              value="url"
              checked={inputType === 'url'}
              onChange={(e) => setInputType(e.target.value)}
            />
            Job URL
          </label>
        </div>

        {inputType === 'text' && (
          <textarea
            placeholder="Paste job posting text here"
            value={jobText}
            onChange={(e) => setJobText(e.target.value)}
            rows="6"
            required
          />
        )}

        {inputType === 'html' && (
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

        {inputType === 'url' && (
          <input
            type="url"
            placeholder="Enter job posting URL"
            value={jobUrl}
            onChange={(e) => setJobUrl(e.target.value)}
            required
          />
        )}

        <button type="submit" disabled={loading}>
          {loading ? '⏳ Uploading...' : '📤 Upload Job Data'}
        </button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default JobUpload;
