import axios from 'axios'

// Get the correct API URL for the environment
const getApiUrl = () => {
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname
    if (hostname.includes('app.github.dev')) {
      // GitHub Codespaces environment
      return `https://${hostname.replace('-3000', '-8000')}`
    }
  }
  // Local development fallback
  return 'http://localhost:8000'
}

// Create axios instance with base configuration
const apiUrl = getApiUrl()
console.log('API URL:', apiUrl)

const api = axios.create({
  baseURL: apiUrl,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/auth/login'
    }
    return Promise.reject(error)
  }
)

// API service objects for different modules
export const accountsApi = {
  getAll: () => api.get('/api/v1/gl/accounts'),
  create: (data: any) => api.post('/api/v1/gl/accounts', data),
  update: (id: string, data: any) => api.put(`/api/v1/gl/accounts/${id}`, data),
  delete: (id: string) => api.delete(`/api/v1/gl/accounts/${id}`)
}

export const journalEntriesApi = {
  getAll: (params?: any) => api.get('/api/v1/gl/journal-entries', { params }),
  create: (data: any) => api.post('/api/v1/gl/journal-entries', data),
  update: (id: string, data: any) => api.put(`/api/v1/gl/journal-entries/${id}`, data),
  delete: (id: string) => api.delete(`/api/v1/gl/journal-entries/${id}`)
}

export default api