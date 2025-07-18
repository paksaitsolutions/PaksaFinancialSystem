import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { createVuetify } from 'vuetify'
import LeftSidebar from '@/components/layout/LeftSidebar.vue'
import Home from '@/views/Home.vue'
import { useMenuStore } from '@/stores/menu'

// Mock router
const routes = [
  { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
  { path: '/gl', name: 'gl', component: { template: '<div>GL</div>' } },
  { path: '/gl/chart-of-accounts', name: 'gl-coa', component: { template: '<div>COA</div>' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Mock vuetify
const vuetify = createVuetify()

describe('Navigation System', () => {
  beforeEach(() => {
    // Setup Pinia
    setActivePinia(createPinia())
    
    // Mock localStorage
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation((key) => {
      if (key === 'token') return 'mock-token'
      return null
    })
  })
  
  describe('LeftSidebar', () => {
    it('renders all visible modules', async () => {
      const wrapper = mount(LeftSidebar, {
        global: {
          plugins: [router, vuetify, createPinia()]
        }
      })
      
      const menuStore = useMenuStore()
      const visibleModules = menuStore.visibleModules
      
      // Check if all modules are rendered
      for (const module of visibleModules) {
        expect(wrapper.text()).toContain(module.title)
      }
    })
    
    it('toggles sidebar expansion', async () => {
      const wrapper = mount(LeftSidebar, {
        global: {
          plugins: [router, vuetify, createPinia()]
        }
      })
      
      const menuStore = useMenuStore()
      const initialState = menuStore.isExpanded
      
      // Find and click the toggle button
      const toggleButton = wrapper.find('button')
      await toggleButton.trigger('click')
      
      // Check if state is toggled
      expect(menuStore.isExpanded).toBe(!initialState)
    })
  })
  
  describe('HomePage', () => {
    it('renders all module cards', async () => {
      const wrapper = mount(Home, {
        global: {
          plugins: [router, vuetify, createPinia()],
          stubs: {
            ModuleCard: true // Stub the ModuleCard component
          }
        }
      })
      
      const menuStore = useMenuStore()
      const visibleModules = menuStore.visibleModules
      
      // Check if all module cards are rendered
      const moduleCards = wrapper.findAllComponents({ name: 'ModuleCard' })
      expect(moduleCards.length).toBe(visibleModules.length)
    })
  })
})