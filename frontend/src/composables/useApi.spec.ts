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
    const { get } = useApi()
    const mockData = { id: 1, name: 'Test' }
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => mockData
    } as Response)

    const result = await get('/test')

    expect(result).toEqual(mockData)
  })

  it('handles API error', async () => {
    const { get, error } = useApi()
    vi.spyOn(global, 'fetch').mockRejectedValue(new Error('API Error'))

    try {
      await get('/test')
    } catch (e) {
      expect(error.value).toBeTruthy()
    }
  })

  it('sets loading state correctly', async () => {
    const { get, loading } = useApi()
    vi.spyOn(global, 'fetch').mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        json: async () => ({})
      } as Response), 100))
    )

    const promise = get('/test')
    expect(loading.value).toBe(true)
    
    await promise
    expect(loading.value).toBe(false)
  })
})