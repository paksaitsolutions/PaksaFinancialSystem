# Dropdown Components Analysis

## Issues Found:

### 1. **Import Errors** (Critical)
- `ReportExportDialog.vue`: Wrong imports
  - `import Dropdown from 'pvue/dropdown';` ❌ Should be `'primevue/dropdown'`
  - `import Dialog from 'evue/dialog';` ❌ Should be `'primevue/dialog'`

### 2. **Missing Components** (Critical)
- Many files import `Dropdown` but it's not globally registered in some cases
- Some files use `v-select` (Vuetify) mixed with PrimeVue `Dropdown`

### 3. **Inconsistent Usage**
- Mix of PrimeVue `Dropdown` and Vuetify `v-select`
- Different prop naming conventions

## Working Dropdowns:
✅ `LanguageSwitcher.vue` - Properly configured
✅ `ChartOfAccounts.vue` - PrimeVue dropdowns working
✅ Most components in `/modules/` directories

## Broken Dropdowns:
❌ `ReportExportDialog.vue` - Import errors
❌ Components using `v-select` without Vuetify
❌ Some report components with wrong imports

## Recommendations:
1. Fix import paths
2. Standardize on PrimeVue Dropdown
3. Update PrimeVue plugin registration
4. Remove Vuetify dependencies