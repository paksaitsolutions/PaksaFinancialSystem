import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

vi.mock('@/utils/api', () => ({
  api: {
    post: vi.fn(),
    get: vi.fn()
  }
}))

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
  })

  it('initializes with default state', () => {
    const authStore = useAuthStore()
    
    expect(authStore.user).toBeNull()
    expect(authStore.token).toBeNull()
    expect(authStore.isAuthenticated).toBe(false)
  })

  it('sets user and token on login', async () => {
    const authStore = useAuthStore()
    const mockUser = { id: '1', email: 'test@example.com', full_name: 'Test User' }
    const mockToken = 'mock-jwt-token'

    const { api } = await import('@/utils/api')
    vi.mocked(api.post).mockResolvedValue({
      access_token: mockToken,
      user: mockUser
    })
    vi.mocked(api.get).mockResolvedValue({ data: [] })

    await authStore.login({ email: 'test@example.com', password: 'password' })

    expect(authStore.user).toEqual(mockUser)
    expect(authStore.token).toBe(mockToken)
    expect(authStore.isAuthenticated).toBe(true)
  })

  it('clears state on logout', () => {
    const authStore = useAuthStore()
    
    authStore.user = { id: '1', email: 'test@example.com', full_name: 'Test User', is_active: true, is_superuser: false, created_at: '2024-01-01' }
    authStore.token = 'mock-token'

    authStore.logout()

    expect(authStore.user).toBeNull()
    expect(authStore.token).toBeNull()
    expect(authStore.isAuthenticated).toBe(false)
  })

  it('handles login error', async () => {
    const authStore = useAuthStore()

    const { api } = await import('@/utils/api')
    vi.mocked(api.post).mockRejectedValue({ response: { status: 401 } })

    await expect(authStore.login({ email: 'test@example.com', password: 'wrong' }))
      .rejects.toThrow('Invalid email or password')

    expect(authStore.isAuthenticated).toBe(false)
  })
})