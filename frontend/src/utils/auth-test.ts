/**
 * Simple authentication test utility
 */
import { useAuthStore } from '@/stores/auth'

export const testAuth = async () => {
  const authStore = useAuthStore()
  
  try {
    console.log('Testing authentication...')
    
    // Test login with demo credentials
    const result = await authStore.login({
      email: 'admin@paksa.com',
      password: 'admin123',
      remember_me: true
    })
    
    console.log('Login successful:', result)
    console.log('User:', authStore.user)
    console.log('Token:', authStore.token)
    console.log('Is authenticated:', authStore.isAuthenticated)
    
    return true
  } catch (error) {
    console.error('Authentication test failed:', error)
    return false
  }
}

// Auto-run test in development
if (import.meta.env.DEV) {
  console.log('Auth test utility loaded')
}