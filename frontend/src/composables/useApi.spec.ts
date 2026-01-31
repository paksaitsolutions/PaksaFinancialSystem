import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useApi } from '@/composables/useApi'

vi.mock('@/utils/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

describe('useApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('handles successful GET request', async () => {
    const { apiClient } = await import('@/utils/apiClient')
    const mockData = { id: 1, name: 'Test' }
    vi.mocked(apiClient.get).mockResolvedValue({ data: mockData })

    const { data, error, loading, execute } = useApi()
    
    await execute(() => apiClient.get('/test'))

    expect(data.value).toEqual(mockData)
    expect(error.value).toBeNull()
    expect(loading.value).toBe(false)
  })

  it('handles API error', async () => {
    const { apiClient } = await import('@/utils/apiClient')
    const mockError = new Error('API Error')
    vi.mocked(apiClient.get).mockRejectedValue(mockError)

    const { data, error, loading, execute } = useApi()
    
    await execute(() => apiClient.get('/test'))

    expect(data.value).toBeNull()
    expect(error.value).toBe(mockError)
    expect(loading.value).toBe(false)
  })

  it('sets loading state correctly', async () => {
    const { apiClient } = await import('@/utils/apiClient')
    vi.mocked(apiClient.get).mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ data: {} }), 100))
    )

    const { loading, execute } = useApi()
    
    const promise = execute(() => apiClient.get('/test'))
    expect(loading.value).toBe(true)
    
    await promise
    expect(loading.value).toBe(false)
  })
})