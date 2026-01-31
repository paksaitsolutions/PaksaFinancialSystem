import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createTestWrapper, mockApiResponse } from '../../components/test/utils'
import AccountsReceivableView from '@/modules/accounts-receivable/views/AccountsReceivableView.vue'

vi.mock('@/api/arService', () => ({
  getARAnalytics: vi.fn(),
  getCustomersPaginated: vi.fn(),
  getInvoicesPaginated: vi.fn()
}))

describe('AccountsReceivableView', () => {
  let wrapper: any

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders AR dashboard', () => {
    wrapper = createTestWrapper(AccountsReceivableView)
    expect(wrapper.find('[data-testid="ar-dashboard"]').exists()).toBe(true)
  })

  it('loads analytics data on mount', async () => {
    const mockAnalytics = {
      totalReceivables: 75000,
      overdueAmount: 8000,
      totalCustomers: 45,
      averageDaysToPayment: 28
    }

    const { getARAnalytics } = await import('@/api/arService')
    vi.mocked(getARAnalytics).mockResolvedValue(mockApiResponse(mockAnalytics))

    wrapper = createTestWrapper(AccountsReceivableView)
    await wrapper.vm.$nextTick()

    expect(getARAnalytics).toHaveBeenCalled()
  })

  it('filters invoices by status', async () => {
    wrapper = createTestWrapper(AccountsReceivableView)
    
    const statusFilter = wrapper.find('[data-testid="status-filter"]')
    await statusFilter.setValue('overdue')
    
    expect(wrapper.vm.filters.status).toBe('overdue')
  })
})