# State Management Patterns

## Overview
This document defines the standardized state management patterns for the Paksa Financial System frontend.

## Principles

### 1. **Use Pinia for Global State**
- ✅ **DO**: Use Pinia stores for data that needs to be shared across multiple components
- ❌ **DON'T**: Use local component state for data that multiple components need

### 2. **Use Local State for Component-Specific Data**
- ✅ **DO**: Use `ref()` or `reactive()` for UI state (modals, tabs, form inputs)
- ❌ **DON'T**: Put UI-only state in Pinia stores

### 3. **Single Source of Truth**
- ✅ **DO**: Keep one authoritative source for each piece of data
- ❌ **DON'T**: Duplicate data across multiple stores or components

## When to Use Pinia Stores

Use Pinia stores for:
- **API Data**: Data fetched from backend (accounts, invoices, customers, etc.)
- **User Authentication**: Current user, permissions, session data
- **Global Settings**: Application configuration, preferences
- **Shared UI State**: Sidebar state, theme, language
- **Cross-Module Data**: Data accessed by multiple modules

## When to Use Local State

Use local component state for:
- **Form Inputs**: Before submission to API
- **Modal/Dialog State**: Open/close state
- **Tab/Accordion State**: Active tab index
- **Loading States**: Component-specific loading indicators
- **Validation Errors**: Form-specific validation messages

## Store Structure

### Standard Store Pattern

```typescript
// stores/exampleStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Example } from '@/types/api-responses'
import { apiClient } from '@/utils/apiClient'
import { handleApiError } from '@/utils/api-error-handler'

export const useExampleStore = defineStore('example', () => {
  // State
  const items = ref<Example[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Getters
  const activeItems = computed(() => 
    items.value.filter(item => item.isActive)
  )
  
  const itemCount = computed(() => items.value.length)
  
  // Actions
  async function fetchItems() {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get<Example[]>('/examples')
      items.value = response.data
    } catch (err) {
      const parsed = handleApiError(err)
      error.value = parsed.userMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function createItem(data: Partial<Example>) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.post<Example>('/examples', data)
      items.value.push(response.data)
      return response.data
    } catch (err) {
      const parsed = handleApiError(err)
      error.value = parsed.userMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function updateItem(id: string, data: Partial<Example>) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.put<Example>(`/examples/${id}`, data)
      const index = items.value.findIndex(item => item.id === id)
      if (index !== -1) {
        items.value[index] = response.data
      }
      return response.data
    } catch (err) {
      const parsed = handleApiError(err)
      error.value = parsed.userMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function deleteItem(id: string) {
    loading.value = true
    error.value = null
    
    try {
      await apiClient.delete(`/examples/${id}`)
      items.value = items.value.filter(item => item.id !== id)
    } catch (err) {
      const parsed = handleApiError(err)
      error.value = parsed.userMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  function clearError() {
    error.value = null
  }
  
  function reset() {
    items.value = []
    loading.value = false
    error.value = null
  }
  
  return {
    // State
    items,
    loading,
    error,
    // Getters
    activeItems,
    itemCount,
    // Actions
    fetchItems,
    createItem,
    updateItem,
    deleteItem,
    clearError,
    reset
  }
})
```

### Using the Store in Components

```vue
<script setup lang="ts">
import { onMounted } from 'vue'
import { useExampleStore } from '@/stores/exampleStore'
import { storeToRefs } from 'pinia'

const exampleStore = useExampleStore()

// Use storeToRefs to maintain reactivity
const { items, loading, error, activeItems } = storeToRefs(exampleStore)

// Actions can be destructured directly
const { fetchItems, createItem, deleteItem } = exampleStore

onMounted(async () => {
  await fetchItems()
})

async function handleCreate(data: any) {
  try {
    await createItem(data)
    // Show success message
  } catch (err) {
    // Error already handled in store
    // Optionally show notification
  }
}
</script>

<template>
  <div>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <div v-for="item in activeItems" :key="item.id">
        {{ item.name }}
      </div>
    </div>
  </div>
</template>
```

## Store Organization

### Directory Structure
```
frontend/src/
├── stores/
│   ├── auth.ts              # Authentication & user
│   ├── gl-accounts.ts       # General Ledger accounts
│   ├── vendors.ts           # AP vendors
│   ├── customers.ts         # AR customers
│   ├── budget.ts            # Budget management
│   ├── payroll.ts           # Payroll data
│   ├── settings.ts          # Application settings
│   └── notifications.ts     # Notifications
```

### Module-Specific Stores
```
frontend/src/modules/
├── general-ledger/
│   └── store/
│       ├── gl-accounts.ts
│       ├── journal-entries.ts
│       └── trial-balance.ts
├── accounts-payable/
│   └── store/
│       ├── vendors.ts
│       ├── invoices.ts
│       └── payments.ts
```

## Best Practices

### 1. **Naming Conventions**
- Store files: `kebab-case.ts` (e.g., `gl-accounts.ts`)
- Store names: `camelCase` (e.g., `glAccounts`)
- Composable: `useCamelCase` (e.g., `useGlAccountsStore`)

### 2. **Error Handling**
```typescript
// ✅ DO: Handle errors in store actions
async function fetchData() {
  try {
    const response = await apiClient.get('/data')
    items.value = response.data
  } catch (err) {
    const parsed = handleApiError(err)
    error.value = parsed.userMessage
    throw err // Re-throw for component handling
  }
}

// ❌ DON'T: Swallow errors silently
async function fetchData() {
  try {
    const response = await apiClient.get('/data')
    items.value = response.data
  } catch (err) {
    // Silent failure - bad!
  }
}
```

### 3. **Loading States**
```typescript
// ✅ DO: Use loading states for async operations
const loading = ref(false)

async function fetchData() {
  loading.value = true
  try {
    // ... fetch data
  } finally {
    loading.value = false
  }
}

// ❌ DON'T: Forget to reset loading state
async function fetchData() {
  loading.value = true
  const response = await apiClient.get('/data')
  // loading never set to false!
}
```

### 4. **Computed Properties**
```typescript
// ✅ DO: Use computed for derived state
const activeItems = computed(() => 
  items.value.filter(item => item.isActive)
)

// ❌ DON'T: Create duplicate reactive state
const activeItems = ref([])
watch(items, () => {
  activeItems.value = items.value.filter(item => item.isActive)
})
```

### 5. **Store Composition**
```typescript
// ✅ DO: Compose stores when needed
export const useInvoiceStore = defineStore('invoice', () => {
  const customerStore = useCustomerStore()
  
  async function createInvoice(data: any) {
    // Can access customer store data
    const customer = customerStore.getCustomerById(data.customerId)
    // ...
  }
  
  return { createInvoice }
})
```

## Migration Checklist

When migrating from local state to Pinia:

1. ✅ Identify data that needs to be shared
2. ✅ Create or update appropriate store
3. ✅ Move API calls to store actions
4. ✅ Update components to use store
5. ✅ Remove local state and API calls from components
6. ✅ Test all affected components
7. ✅ Update related tests

## Common Patterns

### Pattern 1: List with CRUD Operations
See "Standard Store Pattern" above

### Pattern 2: Single Entity Store
```typescript
export const useCurrentUserStore = defineStore('currentUser', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  
  async function fetchCurrentUser() {
    loading.value = true
    try {
      const response = await apiClient.get<User>('/auth/me')
      user.value = response.data
    } finally {
      loading.value = false
    }
  }
  
  return { user, loading, fetchCurrentUser }
})
```

### Pattern 3: Settings Store
```typescript
export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<Record<string, any>>({})
  
  async function loadSettings() {
    const response = await apiClient.get('/settings')
    settings.value = response.data
  }
  
  async function updateSetting(key: string, value: any) {
    await apiClient.put(`/settings/${key}`, { value })
    settings.value[key] = value
  }
  
  return { settings, loadSettings, updateSetting }
})
```

## Resources

- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [TypeScript with Vue](https://vuejs.org/guide/typescript/overview.html)

## Questions?

If you're unsure whether to use Pinia or local state, ask:
1. Do multiple components need this data?
2. Does this data come from an API?
3. Should this data persist across route changes?

If you answered "yes" to any of these, use Pinia. Otherwise, use local state.
