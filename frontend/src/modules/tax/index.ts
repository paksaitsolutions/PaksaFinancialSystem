// Tax Module Exports
export { default as TaxDashboard } from './views/TaxDashboard.vue'
export { default as TaxCodes } from './views/TaxCodes.vue'
export { default as TaxRates } from './views/TaxRates.vue'
export { default as TaxJurisdictions } from './views/TaxJurisdictions.vue'
export { default as TaxExemptions } from './views/TaxExemptionsView.vue'
export { default as TaxReturns } from './views/TaxReturns.vue'
export { default as TaxCompliance } from './views/TaxComplianceDashboard.vue'
export { default as TaxReports } from './views/TaxReports.vue'

// Tax Components
export { default as TaxCalculator } from './components/TaxCalculator.vue'
export { default as TaxManagement } from './components/TaxManagement.vue'

// Tax Services
export * from './services/taxApiService'
export * from './services/taxCalculationService'

// Tax Types
export * from './types/tax'
export * from './types/filing'

// Tax Store
export * from './store'