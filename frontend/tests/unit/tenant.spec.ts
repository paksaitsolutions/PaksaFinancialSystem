import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTenantStore } from '@/stores/tenant'

describe('Tenant Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should select a company and set tenant context', async () => {
    const mockCompany = {
      id: 1,
      tenant_id: 'tenant1',
      name: 'Test Company',
      email: 'test@company.com',
      features: ['budgets', 'fixed_assets'],
      subscription_plan: 'premium',
      status: 'active'
    }

    const store = useTenantStore()
    store.availableCompanies = [mockCompany]

    await store.selectCompany(1)

    expect(store.currentCompany).toEqual(mockCompany)
    expect(store.tenantId).toBe('tenant1')
  })

  it('should check feature availability', () => {
    const store = useTenantStore()
    store.currentCompany = {
      id: 1,
      tenant_id: 'tenant1',
      name: 'Test Company',
      email: 'test@company.com',
      features: ['budgets', 'fixed_assets'],
      subscription_plan: 'premium',
      status: 'active'
    }

    expect(store.hasFeature('budgets')).toBe(true)
    expect(store.hasFeature('payroll')).toBe(false)
  })
})