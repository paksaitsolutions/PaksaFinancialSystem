import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createVuetify } from 'vuetify'
import ExecutiveDashboard from '@/components/integration/ExecutiveDashboard.vue'
import WorkflowManager from '@/components/integration/WorkflowManager.vue'
import IntegratedReports from '@/components/integration/IntegratedReports.vue'
import { useIntegrationStore } from '@/stores/integration'

// Mock axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

const vuetify = createVuetify()

describe('Integration Components', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('ExecutiveDashboard', () => {
    it('renders executive dashboard correctly', async () => {
      const wrapper = mount(ExecutiveDashboard, {
        global: {
          plugins: [vuetify]
        }
      })

      expect(wrapper.find('h1').text()).toBe('Executive Dashboard')
      expect(wrapper.find('.executive-dashboard').exists()).toBe(true)
    })

    it('displays KPI cards', async () => {
      const mockData = {
        executive_summary: {
          net_cash_flow: 50000,
          total_cash_position: 250000,
          accounts_receivable_balance: 75000,
          accounts_payable_balance: 45000
        }
      }

      const integrationStore = useIntegrationStore()
      vi.spyOn(integrationStore, 'getExecutiveDashboard').mockResolvedValue(mockData)

      const wrapper = mount(ExecutiveDashboard, {
        global: {
          plugins: [vuetify]
        }
      })

      await wrapper.vm.$nextTick()
      
      // Should have 4 KPI cards
      const kpiCards = wrapper.findAll('.v-card')
      expect(kpiCards.length).toBeGreaterThanOrEqual(4)
    })

    it('handles API errors gracefully', async () => {
      const integrationStore = useIntegrationStore()
      vi.spyOn(integrationStore, 'getExecutiveDashboard').mockRejectedValue(new Error('API Error'))

      const wrapper = mount(ExecutiveDashboard, {
        global: {
          plugins: [vuetify]
        }
      })

      await wrapper.vm.$nextTick()
      
      // Component should still render without crashing
      expect(wrapper.find('.executive-dashboard').exists()).toBe(true)
    })
  })

  describe('WorkflowManager', () => {
    it('renders workflow manager correctly', () => {
      const wrapper = mount(WorkflowManager, {
        global: {
          plugins: [vuetify]
        }
      })

      expect(wrapper.find('h1').text()).toBe('Integrated Workflows')
      expect(wrapper.find('.workflow-manager').exists()).toBe(true)
    })

    it('displays workflow cards', () => {
      const wrapper = mount(WorkflowManager, {
        global: {
          plugins: [vuetify]
        }
      })

      const workflowCards = wrapper.findAll('.workflow-card')
      expect(workflowCards.length).toBe(3) // P2P, I2C, B2A workflows
    })

    it('opens workflow dialog when card is clicked', async () => {
      const wrapper = mount(WorkflowManager, {
        global: {
          plugins: [vuetify]
        }
      })

      const firstWorkflowCard = wrapper.find('.workflow-card')
      await firstWorkflowCard.trigger('click')

      expect(wrapper.vm.workflowDialog).toBe(true)
    })

    it('processes workflow correctly', async () => {
      const mockResult = {
        workflow_id: 'P2P-123',
        status: 'completed',
        workflow_results: [
          { step: 'vendor_created', vendor_id: 1 },
          { step: 'bill_created', bill_id: 1 }
        ]
      }

      const integrationStore = useIntegrationStore()
      vi.spyOn(integrationStore, 'processPurchaseToPayment').mockResolvedValue(mockResult)

      const wrapper = mount(WorkflowManager, {
        global: {
          plugins: [vuetify]
        }
      })

      // Set up workflow data
      wrapper.vm.selectedWorkflow = { id: 'purchase-to-payment', title: 'Purchase to Payment' }
      wrapper.vm.workflowData = {
        bill_number: 'TEST-001',
        total_amount: 1000,
        bill_date: '2024-01-15',
        due_date: '2024-02-15'
      }

      await wrapper.vm.processWorkflow()

      expect(wrapper.vm.workflowResults).toEqual(mockResult)
      expect(wrapper.vm.resultsDialog).toBe(true)
    })
  })

  describe('IntegratedReports', () => {
    it('renders integrated reports correctly', () => {
      const wrapper = mount(IntegratedReports, {
        global: {
          plugins: [vuetify]
        }
      })

      expect(wrapper.find('h1').text()).toBe('Integrated Reports')
      expect(wrapper.find('.integrated-reports').exists()).toBe(true)
    })

    it('displays available reports', () => {
      const wrapper = mount(IntegratedReports, {
        global: {
          plugins: [vuetify]
        }
      })

      const reportItems = wrapper.findAll('.v-list-item')
      expect(reportItems.length).toBe(3) // Executive dashboard, Cash flow, Financial summary
    })

    it('selects report when clicked', async () => {
      const wrapper = mount(IntegratedReports, {
        global: {
          plugins: [vuetify]
        }
      })

      const firstReportItem = wrapper.find('.v-list-item')
      await firstReportItem.trigger('click')

      expect(wrapper.vm.selectedReport).toBeTruthy()
    })

    it('generates report with correct data', async () => {
      const mockReportData = {
        executive_summary: {
          net_cash_flow: 25000,
          total_cash_position: 150000
        },
        key_metrics: {
          liquidity_ratio: 2.5,
          collection_efficiency: 85.0
        }
      }

      const integrationStore = useIntegrationStore()
      vi.spyOn(integrationStore, 'getExecutiveDashboard').mockResolvedValue(mockReportData)

      const wrapper = mount(IntegratedReports, {
        global: {
          plugins: [vuetify]
        }
      })

      wrapper.vm.selectedReport = { id: 'executive-dashboard', title: 'Executive Dashboard' }
      await wrapper.vm.generateReport()

      expect(wrapper.vm.reportData).toEqual(mockReportData)
    })
  })
})

describe('Integration Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('fetches executive dashboard data', async () => {
    const mockData = { executive_summary: { net_cash_flow: 10000 } }
    
    const axios = await import('axios')
    vi.mocked(axios.default.get).mockResolvedValue({ data: mockData })

    const store = useIntegrationStore()
    const result = await store.getExecutiveDashboard(1)

    expect(result).toEqual(mockData)
    expect(store.executiveDashboard).toEqual(mockData)
  })

  it('handles API errors correctly', async () => {
    const axios = await import('axios')
    vi.mocked(axios.default.get).mockRejectedValue(new Error('Network Error'))

    const store = useIntegrationStore()
    
    await expect(store.getExecutiveDashboard(1)).rejects.toThrow('Network Error')
    expect(store.error).toBe('Network Error')
  })

  it('processes workflows correctly', async () => {
    const mockResult = { workflow_id: 'P2P-123', status: 'completed' }
    
    const axios = await import('axios')
    vi.mocked(axios.default.post).mockResolvedValue({ data: mockResult })

    const store = useIntegrationStore()
    const result = await store.processPurchaseToPayment({ bill_number: 'TEST-001' })

    expect(result).toEqual(mockResult)
  })

  it('manages loading states correctly', async () => {
    const axios = await import('axios')
    vi.mocked(axios.default.get).mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ data: {} }), 100))
    )

    const store = useIntegrationStore()
    
    const promise = store.getExecutiveDashboard(1)
    expect(store.loading).toBe(true)
    
    await promise
    expect(store.loading).toBe(false)
  })
})