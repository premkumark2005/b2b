import React, { useState } from 'react';
import './WebsiteUpload.css';
import { uploadProductData } from '../services/api';

const ProductUpload = ({ companyName, onSuccess }) => {
  const [inputType, setInputType] = useState('text');
  const [pdfFile, setPdfFile] = useState(null);
  const [htmlFile, setHtmlFile] = useState(null);
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
      const formData = new FormData();
      formData.append('company_name', companyName);
      
      if (inputType === 'pdf' && pdfFile) {
        formData.append('pdf_file', pdfFile);
      } else if (inputType === 'html' && htmlFile) {
        formData.append('html_file', htmlFile);
      } else if (inputType === 'text') {
        formData.append('plain_text', plainText);
      }

      const response = await uploadProductData(formData);
      setMessage(`✅ ${response.message}`);
      
      // Clear form
      setPdfFile(null);
      setHtmlFile(null);
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
      <h2>📦 2. Product Brochure</h2>
      <form onSubmit={handleSubmit}>
        <div className="input-type-selector">
          <label>
            <input
              type="radio"
              value="text"
              checked={inputType === 'text'}
              onChange={(e) => setInputType(e.target.value)}
            />
            Text Input
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
              value="pdf"
              checked={inputType === 'pdf'}
              onChange={(e) => setInputType(e.target.value)}
            />
            PDF File
          </label>
        </div>

        {inputType === 'text' && (
          <textarea
            placeholder="Paste product descriptions, brochures, datasheets..."
            value={plainText}
            onChange={(e) => setPlainText(e.target.value)}
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

        {inputType === 'pdf' && (
          <div>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setPdfFile(e.target.files[0])}
              required
            />
            {pdfFile && <p className="file-name">📄 {pdfFile.name}</p>}
          </div>
        )}

        <button type="submit" disabled={loading}>
          {loading ? '⏳ Uploading...' : '📤 Upload Product Data'}
        </button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default ProductUpload;
