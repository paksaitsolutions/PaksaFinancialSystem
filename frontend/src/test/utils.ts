/**
 * Test utilities for component testing
 * 
 * Author: Paksa IT Solutions
 * Copyright (c) 2024 Paksa IT Solutions. All rights reserved.
 */
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { vi } from 'vitest'
import PrimeVue from 'primevue/config'

export function createTestWrapper(component: any, options = {}) {
  const pinia = createPinia()
  
  return mount(component, {
    global: {
      plugins: [pinia, PrimeVue],
      mocks: {
        $router: {
          push: vi.fn(),
          replace: vi.fn()
        },
        $route: {
          params: {},
          query: {}
        }
      }
    },
    ...options
  })
}

export function mockApiResponse<T>(data: T) {
  return { data }
}
