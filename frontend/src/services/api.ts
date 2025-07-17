import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Request interceptor for API calls
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for API calls
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 Unauthorized errors (token expired)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // In a real app, you would refresh the token here
        // const refreshToken = localStorage.getItem('refreshToken');
        // const response = await axios.post('/api/auth/refresh', { refreshToken });
        // const { token } = response.data;
        // localStorage.setItem('token', token);
        // originalRequest.headers['Authorization'] = `Bearer ${token}`;
        // return api(originalRequest);
        
        // For now, just redirect to login
        localStorage.removeItem('token');
        window.location.href = '/auth/login';
        return Promise.reject(error);
      } catch (refreshError) {
        // If refresh token fails, redirect to login
        localStorage.removeItem('token');
        window.location.href = '/auth/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;