import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadWebsiteData = async (formData) => {
  const response = await axios.post(`${API_BASE_URL}/website/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const uploadProductData = async (formData) => {
  const response = await axios.post(`${API_BASE_URL}/product/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const uploadJobData = async (formData) => {
  const response = await axios.post(`${API_BASE_URL}/job/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const uploadNewsData = async (formData) => {
  const response = await axios.post(`${API_BASE_URL}/news/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const generateProfile = async (companyName, companyDomain = '') => {
  const response = await api.post('/profile/generate', { 
    company_name: companyName,
    company_domain: companyDomain 
  });
  return response.data;
};

export const getProfile = async (companyName) => {
  const response = await api.get(`/profile/${companyName}`);
  return response.data;
};
