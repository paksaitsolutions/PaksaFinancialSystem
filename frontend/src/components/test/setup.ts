import { vi } from 'vitest'
import { config } from '@vue/test-utils'
import { createPinia } from 'pinia'

// Mock PrimeVue components
vi.mock('primevue/config', () => ({
  default: {}
}))

vi.mock('primevue/button', () => ({
  default: { name: 'Button', template: '<button><slot /></button>' }
}))

vi.mock('primevue/inputtext', () => ({
  default: { name: 'InputText', template: '<input />' }
}))

vi.mock('primevue/datatable', () => ({
  default: { name: 'DataTable', template: '<div><slot /></div>' }
}))

vi.mock('primevue/dialog', () => ({
  default: { name: 'Dialog', template: '<div><slot /></div>' }
}))

// Global test configuration
config.global.plugins = [createPinia()]

// Mock router
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  currentRoute: { value: { path: '/', query: {}, params: {} } }
}

config.global.mocks = {
  $router: mockRouter,
  $route: mockRouter.currentRoute.value
}

// Mock API client
vi.mock('@/utils/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

// Mock notifications
vi.mock('@/composables/useNotifications', () => ({
  useNotifications: () => ({
    showSuccess: vi.fn(),
    showError: vi.fn(),
    showWarning: vi.fn(),
    showInfo: vi.fn()
  })
}))