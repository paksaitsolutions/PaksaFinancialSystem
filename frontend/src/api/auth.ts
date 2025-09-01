import api from '@/plugins/axios'
import type { User } from '@/stores/auth'

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  user: User
}

export interface RegisterRequest {
  fullName: string
  email: string
  company: string
  password: string
}

export const authApi = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await api.post('/api/v1/auth/login', credentials)
    return response.data
  },

  async register(data: RegisterRequest) {
    const response = await api.post('/api/v1/auth/register', data)
    return response.data
  },

  async logout() {
    const response = await api.post('/api/v1/auth/logout')
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/api/v1/auth/me')
    return response.data
  },

  async verifyToken() {
    const response = await api.get('/api/v1/auth/verify-token')
    return response.data
  },

  async forgotPassword(email: string) {
    const response = await api.post('/api/v1/auth/forgot-password', { email })
    return response.data
  },

  async resetPassword(token: string, password: string) {
    const response = await api.post('/api/v1/auth/reset-password', { token, password })
    return response.data
  },

  async refreshToken(refreshToken: string) {
    const response = await api.post('/api/v1/auth/refresh-token', { refresh_token: refreshToken })
    return response.data
  }
}