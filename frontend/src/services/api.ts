/**
 * Paksa Financial System
 * ----------------------
 * Version: 1.0
 * Author: Paksa IT Solutions
 * Copyright © 2023 Paksa IT Solutions
 *
 * This file is part of the Paksa Financial System.
 * It is subject to the terms and conditions defined in
 * file 'LICENSE', which is part of this source code package.
 */

import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
    // 'Authorization': `Bearer ${localStorage.getItem('token')}` // Example for auth
  }
});

// Optional: Add a request interceptor for things like auth tokens
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// Optional: Add a response interceptor for global error handling
apiClient.interceptors.response.use(response => {
  return response;
}, error => {
  // Handle global errors (e.g., 401 Unauthorized, 500 Server Error)
  if (error.response && error.response.status === 401) {
    // e.g., redirect to login
    console.error('Unauthorized! Redirecting to login...');
  }
  return Promise.reject(error);
});

export default apiClient;
