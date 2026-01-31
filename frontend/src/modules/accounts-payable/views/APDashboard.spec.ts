import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createTestWrapper, mockApiResponse } from '../test/utils'
import APDashboard from '@/modules/accounts-payable/views/APDashboard.vue'

vi.mock('@/api/apService', () => ({
  getAPDashboardStats: vi.fn(),
  getRecentBills: vi.fn(),
  getVendorsPaginated: vi.fn()
}))

describe('APDashboard', () => {
  let wrapper: any

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders dashboard title', () => {
    wrapper = createTestWrapper(APDashboard)
    expect(wrapper.find('h1').text()).toContain('Accounts Payable')
  })

  it('loads dashboard stats on mount', async () => {
    const mockStats = {
      totalOutstanding: 50000,
      overdueAmount: 5000,
      totalVendors: 25,
      pendingApprovals: 3
    }

    const { getAPDashboardStats } = await import('@/api/apService')
    vi.mocked(getAPDashboardStats).mockResolvedValue(mockApiResponse(mockStats))

    wrapper = createTestWrapper(APDashboard)
    await wrapper.vm.$nextTick()

    expect(getAPDashboardStats).toHaveBeenCalled()
  })

  it('displays error message when API fails', async () => {
    const { getAPDashboardStats } = await import('@/api/apService')
    vi.mocked(getAPDashboardStats).mockRejectedValue(new Error('API Error'))

    wrapper = createTestWrapper(APDashboard)
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.error-message').exists()).toBe(true)
  })

  it('navigates to bills when view all clicked', async () => {
    wrapper = createTestWrapper(APDashboard)
    
    await wrapper.find('[data-testid="view-all-bills"]').trigger('click')
    
    expect(wrapper.vm.$router.push).toHaveBeenCalledWith('/ap/bills')
  })
})