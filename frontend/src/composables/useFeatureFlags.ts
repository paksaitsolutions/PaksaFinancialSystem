import { computed } from 'vue'
import { useTenantStore } from '@/stores/tenant'

export function useFeatureFlags() {
  const tenantStore = useTenantStore()
  
  const hasFeature = (feature: string) => {
    return computed(() => tenantStore.hasFeature(feature))
  }
  
  const features = computed(() => tenantStore.currentCompany?.features || [])
  
  // Common feature flags
  const canAccessBudgets = hasFeature('budgets')
  const canAccessFixedAssets = hasFeature('fixed_assets')
  const canAccessTax = hasFeature('tax_management')
  const canAccessInventory = hasFeature('inventory')
  const canAccessPayroll = hasFeature('payroll')
  const canAccessReports = hasFeature('reports')
  const canAccessAI = hasFeature('ai_features')
  
  return {
    hasFeature,
    features,
    canAccessBudgets,
    canAccessFixedAssets,
    canAccessTax,
    canAccessInventory,
    canAccessPayroll,
    canAccessReports,
    canAccessAI
  }
}