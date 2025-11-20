import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const auth = {
  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    const response = await axios.post(`${API_BASE_URL}/token`, formData);
    return response.data;
  },
  signup: async (email, password, name) => {
    const response = await axios.post(`${API_BASE_URL}/users/`, { email, password, name });
    return response.data;
  },
  getMe: async () => {
    const response = await api.get('/users/me/');
    return response.data;
  },
};

export const opportunities = {
  getAll: async () => {
    const response = await api.get('/opportunities/');
    return response.data;
  },
  create: async (data) => {
    const response = await api.post('/opportunities/', data);
    return response.data;
  },
  update: async (id, data) => {
    const response = await api.put(`/opportunities/${id}`, data);
    return response.data;
  },
};

export default api;
