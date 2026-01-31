import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

vi.mock('@/utils/apiClient', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn()
  }
}))

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with default state', () => {
    const authStore = useAuthStore()
    
    expect(authStore.user).toBeNull()
    expect(authStore.token).toBeNull()
    expect(authStore.isAuthenticated).toBe(false)
  })

  it('sets user and token on login', async () => {
    const authStore = useAuthStore()
    const mockUser = { id: 1, email: 'test@example.com', name: 'Test User' }
    const mockToken = 'mock-jwt-token'

    const { apiClient } = await import('@/utils/apiClient')
    vi.mocked(apiClient.post).mockResolvedValue({
      data: { user: mockUser, token: mockToken }
    })

    await authStore.login('test@example.com', 'password')

    expect(authStore.user).toEqual(mockUser)
    expect(authStore.token).toBe(mockToken)
    expect(authStore.isAuthenticated).toBe(true)
  })

  it('clears state on logout', () => {
    const authStore = useAuthStore()
    
    // Set initial state
    authStore.user = { id: 1, email: 'test@example.com', name: 'Test User' }
    authStore.token = 'mock-token'

    authStore.logout()

    expect(authStore.user).toBeNull()
    expect(authStore.token).toBeNull()
    expect(authStore.isAuthenticated).toBe(false)
  })

  it('handles login error', async () => {
    const authStore = useAuthStore()

    const { apiClient } = await import('@/utils/apiClient')
    vi.mocked(apiClient.post).mockRejectedValue(new Error('Invalid credentials'))

    await expect(authStore.login('test@example.com', 'wrong-password'))
      .rejects.toThrow('Invalid credentials')

    expect(authStore.isAuthenticated).toBe(false)
  })
})