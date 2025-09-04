import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/utils/apiClient'

interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  role: string
  is_admin: boolean
  permissions: string[]
}

interface LoginRequest {
  email: string
  password: string
  remember_me?: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_admin || false)
  const userRole = computed(() => user.value?.role || 'viewer')

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
  }

  const setUser = (newUser: User) => {
    user.value = newUser
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  const login = async (credentials: LoginRequest) => {
    loading.value = true
    try {
      const response = await apiClient.post('/auth/login', credentials)
      
      if (response.data.requiresMFA) {
        return { requiresMFA: true }
      }

      setToken(response.data.access_token)
      setUser(response.data.user)
      
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed')
    } finally {
      loading.value = false
    }
  }

  const verifyMFA = async (code: string) => {
    try {
      const response = await apiClient.post('/auth/verify-mfa', { code })
      setToken(response.data.access_token)
      setUser(response.data.user)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'MFA verification failed')
    }
  }

  const logout = async () => {
    try {
      await apiClient.post('/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete apiClient.defaults.headers.common['Authorization']
    }
  }

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) throw new Error('No refresh token')

      const response = await apiClient.post('/auth/refresh-token', { refresh_token: refreshToken })
      setToken(response.data.access_token)
      return response.data
    } catch (error) {
      logout()
      throw error
    }
  }

  const getCurrentUser = async () => {
    try {
      const response = await apiClient.get('/auth/me')
      setUser(response.data)
      return response.data
    } catch (error) {
      logout()
      throw error
    }
  }

  const hasPermission = (permission: string): boolean => {
    if (!user.value) return false
    if (user.value.role === 'super_admin') return true
    return user.value.permissions.includes(permission) || user.value.permissions.includes('*')
  }

  const hasRole = (role: string): boolean => {
    if (!user.value) return false
    return user.value.role === role || user.value.role === 'super_admin'
  }

  // Initialize auth state
  const initializeAuth = () => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      token.value = storedToken
      user.value = JSON.parse(storedUser)
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
    }
  }

  return {
    token,
    user,
    loading,
    isAuthenticated,
    isAdmin,
    userRole,
    login,
    verifyMFA,
    logout,
    refreshToken,
    getCurrentUser,
    hasPermission,
    hasRole,
    setToken,
    setUser,
    initializeAuth
  }
})