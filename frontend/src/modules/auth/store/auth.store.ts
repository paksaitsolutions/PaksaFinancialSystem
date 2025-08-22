import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import router from '@/router'
import type { User, LoginCredentials } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token'))
  const error = ref<string | null>(null)
  const loading = ref(false)
  const isInitialized = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const currentUser = computed(() => user.value)

  // Helper function to set authentication data
  const setAuthData = (authData: { user: User; token: string; refreshToken?: string }, remember: boolean = false) => {
    user.value = authData.user
    token.value = authData.token
    refreshToken.value = authData.refreshToken || null
    
    // Set axios default authorization header
    axios.defaults.headers.common['Authorization'] = `Bearer ${authData.token}`
    
    // Store tokens in appropriate storage based on remember me
    const storage = remember ? localStorage : sessionStorage
    storage.setItem('auth_token', authData.token)
    if (authData.refreshToken) {
      storage.setItem('refresh_token', authData.refreshToken)
    }
    
    // Store user data
    storage.setItem('user', JSON.stringify(authData.user))
    
    // Clear the other storage to prevent conflicts
    const otherStorage = remember ? sessionStorage : localStorage
    otherStorage.removeItem('auth_token')
    otherStorage.removeItem('refresh_token')
    otherStorage.removeItem('user')
  }

  // Clear authentication data
  const clearAuthData = () => {
    user.value = null
    token.value = null
    refreshToken.value = null
    
    // Clear storage
    localStorage.removeItem('auth_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    sessionStorage.removeItem('auth_token')
    sessionStorage.removeItem('refresh_token')
    sessionStorage.removeItem('user')
    
    // Clear axios auth header
    delete axios.defaults.headers.common['Authorization']
  }

  // Actions
  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.post('/auth/token', 
        new URLSearchParams({
          username: credentials.email,
          password: credentials.password
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      )
      
      if (response.data?.access_token) {
        // Create user object from response
        const userData: User = {
          id: '1',
          email: credentials.email,
          name: credentials.email.split('@')[0],
          permissions: ['admin'],
          isActive: true
        }
        
        setAuthData({
          user: userData,
          token: response.data.access_token,
          refreshToken: response.data.refresh_token
        }, credentials.rememberMe || false)
        
        return true
      }
      
      throw new Error('Invalid response from server')
    } catch (err: any) {
      console.error('Login error:', err)
      if (err.response?.status === 401) {
        error.value = 'Invalid email or password'
      } else if (err.response?.data?.detail) {
        error.value = err.response.data.detail
      } else {
        error.value = 'Login failed. Please try again.'
      }
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = async (): Promise<void> => {
    try {
      loading.value = true
      
      // Try to call logout endpoint
      if (token.value) {
        await axios.post('/auth/logout')
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      clearAuthData()
      loading.value = false
      
      // Redirect to login
      if (router.currentRoute.value.path !== '/auth/login') {
        router.push('/auth/login')
      }
    }
  }

  const initialize = async (): Promise<boolean> => {
    try {
      loading.value = true
      
      // Check if we have stored auth data
      const storedToken = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
      const storedUser = localStorage.getItem('user') || sessionStorage.getItem('user')
      const storedRefreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token')
      
      if (storedToken && storedUser) {
        try {
          // Set the token in axios header
          axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
          
          // Verify token is still valid
          await axios.get('/auth/verify-token')
          
          // Token is valid, restore user data
          user.value = JSON.parse(storedUser)
          token.value = storedToken
          refreshToken.value = storedRefreshToken
          
          return true
        } catch (error) {
          console.error('Token validation failed:', error)
          clearAuthData()
        }
      }
      
      return false
    } catch (error) {
      console.error('Auth initialization error:', error)
      clearAuthData()
      return false
    } finally {
      isInitialized.value = true
      loading.value = false
    }
  }

  const refreshAccessToken = async (): Promise<boolean> => {
    try {
      if (!refreshToken.value) return false
      
      const response = await axios.post('/auth/refresh-token', {
        refresh_token: refreshToken.value
      })
      
      if (response.data?.access_token) {
        token.value = response.data.access_token
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`
        
        // Update stored token
        const storage = localStorage.getItem('auth_token') ? localStorage : sessionStorage
        storage.setItem('auth_token', response.data.access_token)
        
        return true
      }
      
      return false
    } catch (error) {
      console.error('Token refresh failed:', error)
      await logout()
      return false
    }
  }

  const register = async (userData: {
    fullName: string
    email: string
    company: string
    password: string
  }): Promise<boolean> => {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.post('/auth/register', userData)
      
      if (response.data?.success) {
        return true
      }
      
      throw new Error('Registration failed')
    } catch (err: any) {
      console.error('Registration error:', err)
      if (err.response?.data?.detail) {
        error.value = err.response.data.detail
      } else {
        error.value = 'Registration failed. Please try again.'
      }
      return false
    } finally {
      loading.value = false
    }
  }

  const forgotPassword = async (email: string): Promise<boolean> => {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.post('/auth/forgot-password', { email })
      
      if (response.data?.success) {
        return true
      }
      
      throw new Error('Failed to send reset email')
    } catch (err: any) {
      console.error('Forgot password error:', err)
      if (err.response?.data?.detail) {
        error.value = err.response.data.detail
      } else {
        error.value = 'Failed to send reset email. Please try again.'
      }
      return false
    } finally {
      loading.value = false
    }
  }

  const resetPassword = async (token: string, password: string): Promise<boolean> => {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.post('/auth/reset-password', {
        token,
        password
      })
      
      if (response.data?.success) {
        return true
      }
      
      throw new Error('Password reset failed')
    } catch (err: any) {
      console.error('Reset password error:', err)
      if (err.response?.data?.detail) {
        error.value = err.response.data.detail
      } else {
        error.value = 'Password reset failed. Please try again.'
      }
      return false
    } finally {
      loading.value = false
    }
  }

  // Initialize auth state on store creation
  if (!isInitialized.value) {
    initialize()
  }

  return {
    // State
    user,
    token,
    refreshToken,
    error,
    loading,
    isInitialized,
    
    // Getters
    isAuthenticated,
    currentUser,
    
    // Actions
    login,
    logout,
    initialize,
    refreshAccessToken,
    register,
    forgotPassword,
    resetPassword,
    setAuthData,
    clearAuthData
  }
})