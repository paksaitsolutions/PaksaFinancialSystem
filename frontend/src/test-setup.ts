import { config } from '@vue/test-utils';
import { createPinia } from 'pinia';
import { vi } from 'vitest';

// Mock global components and plugins
const pinia = createPinia();

// Configure Vue Test Utils
config.global.plugins = [pinia];

// Mock window.URL.createObjectURL
if (typeof window !== 'undefined') {
  window.URL.createObjectURL = vi.fn();
}

// Mock global components
config.global.components = {
  // Add any global components used in tests
  'router-link': {
    template: '<a :href="to"><slot/></a>',
    props: ['to']
  },
  'router-view': {
    template: '<div><slot/></div>'
  }
};

// Mock global directives
config.global.directives = {
  // Add any global directives used in tests
  tooltip: {},
  ripple: {}
};

// Mock global properties
config.global.mocks = {
  $t: (key: string) => key, // i18n mock
  $route: {
    path: '/',
    query: {},
    params: {}
  },
  $router: {
    push: vi.fn(),
    replace: vi.fn(),
    go: vi.fn(),
    back: vi.fn(),
    forward: vi.fn()
  }
};

// Mock global provide
config.global.provide = {
  // Add any global provides used in tests
};

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
