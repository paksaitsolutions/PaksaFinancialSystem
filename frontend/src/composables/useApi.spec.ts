import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useApi } from '@/composables/useApi'
import axios from 'axios'

vi.mock('axios')

describe('useApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('handles successful GET request', async () => {
    const mockData = { id: 1, name: 'Test' }
    vi.mocked(axios.create).mockReturnValue({
      get: vi.fn().mockResolvedValue({ data: mockData }),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    } as any)

    const { get } = useApi()
    const result = await get('/test')

    expect(result).toEqual(mockData)
  })

  it('handles API error', async () => {
    const mockError = new Error('API Error')
    vi.mocked(axios.create).mockReturnValue({
      get: vi.fn().mockRejectedValue(mockError),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    } as any)

    const { get, error } = useApi()

    try {
      await get('/test')
    } catch (e) {
      expect(error.value).toBeTruthy()
    }
  })

  it('sets loading state correctly', async () => {
    vi.mocked(axios.create).mockReturnValue({
      get: vi.fn().mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ data: {} }), 100))
      ),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    } as any)

    const { get, loading } = useApi()
    
    const promise = get('/test')
    expect(loading.value).toBe(true)
    
    await promise
    expect(loading.value).toBe(false)
  })
})