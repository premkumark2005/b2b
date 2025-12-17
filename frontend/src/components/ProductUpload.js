import React, { useState } from 'react';
import './WebsiteUpload.css';
import { uploadProductData } from '../services/api';

const ProductUpload = ({ companyName, onSuccess }) => {
  const [inputType, setInputType] = useState('pdf');
  const [pdfFile, setPdfFile] = useState(null);
  const [plainText, setPlainText] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    setPdfFile(e.target.files[0]);
  };

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
      } else if (inputType === 'text') {
        formData.append('plain_text', plainText);
      }

      const response = await uploadProductData(formData);
      setMessage(`✅ ${response.message}`);
      
      // Clear form
      setPdfFile(null);
      setPlainText('');
      if (e.target.pdf_file) e.target.pdf_file.value = '';
      
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
              value="pdf"
              checked={inputType === 'pdf'}
              onChange={(e) => setInputType(e.target.value)}
            />
            PDF Upload
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

        {inputType === 'pdf' && (
          <div className="file-input-wrapper">
            <label>Upload PDF Brochure:</label>
            <input
              type="file"
              name="pdf_file"
              accept=".pdf"
              onChange={handleFileChange}
              required
            />
          </div>
        )}

        {inputType === 'text' && (
          <textarea
            placeholder="Paste product information here"
            value={plainText}
            onChange={(e) => setPlainText(e.target.value)}
            rows="6"
            required
          />
        )}

        <button type="submit" disabled={loading}>
          {loading ? 'Uploading...' : 'Upload Product Data'}
        </button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default ProductUpload;
