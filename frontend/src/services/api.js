import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadWebsiteData = async (data) => {
  const response = await api.post('/website/upload', data);
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

export const uploadJobData = async (data) => {
  const response = await api.post('/job/upload', data);
  return response.data;
};

export const uploadNewsData = async (data) => {
  const response = await api.post('/news/upload', data);
  return response.data;
};

export const generateProfile = async (companyName) => {
  const response = await api.post('/profile/generate', { company_name: companyName });
  return response.data;
};

export const getProfile = async (companyName) => {
  const response = await api.get(`/profile/${companyName}`);
  return response.data;
};
