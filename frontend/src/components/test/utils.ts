import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { vi } from 'vitest'

export const createTestWrapper = (component: any, options = {}) => {
  const pinia = createPinia()
  
  return mount(component, {
    global: {
      plugins: [pinia],
      mocks: {
        $router: {
          push: vi.fn(),
          replace: vi.fn()
        },
        $route: {
          path: '/',
          query: {},
          params: {}
        }
      }
    },
    ...options
  })
}

export const mockApiResponse = (data: any, status = 200) => ({
  data,
  status,
  statusText: 'OK',
  headers: {},
  config: {}
})

export const mockApiError = (message = 'API Error', status = 500) => ({
  response: {
    data: { message },
    status,
    statusText: 'Internal Server Error'
  }
})

export const waitForNextTick = () => new Promise(resolve => setTimeout(resolve, 0))