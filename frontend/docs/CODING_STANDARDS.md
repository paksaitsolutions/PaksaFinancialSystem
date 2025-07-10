# Paksa Financial System - Frontend Coding Standards

## Table of Contents
1. [TypeScript Standards](#typescript-standards)
2. [Validation Rules](#validation-rules)
3. [API Integration](#api-integration)
4. [Form Handling](#form-handling)
5. [State Management](#state-management)
6. [Error Handling](#error-handling)
7. [Naming Conventions](#naming-conventions)
8. [File Structure](#file-structure)
9. [Code Organization](#code-organization)
10. [Performance](#performance)

## TypeScript Standards

### Type Definitions
- Always define types/interfaces for all data structures
- Use `type` for simple type definitions and unions
- Use `interface` for object shapes that can be extended or implemented
- Avoid using `any` - use `unknown` when the type is truly dynamic
- Use generics for reusable components and utilities

### Basic Types
```typescript
// Primitive types
let isActive: boolean = true;
let count: number = 0;
let name: string = 'John';

// Arrays
let numbers: number[] = [1, 2, 3];
let names: Array<string> = ['Alice', 'Bob'];

// Tuples
let tuple: [string, number] = ['age', 30];

// Enums
enum Status {
  Active = 'ACTIVE',
  Inactive = 'INACTIVE',
  Pending = 'PENDING'
}

// Type assertions
const value = someValue as string;
```

### Type Guards
```typescript
// Type predicate
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

// Type narrowing
if (typeof value === 'string') {
  // value is string here
}
```

## Validation Rules

### Client-Side Validation
Use Vuelidate with custom validators for form validation:

```typescript
// validation/rules.ts
import { helpers } from '@vuelidate/validators';
import { isNumber, isString, isValidEmail } from '@/utils/validationUtils';

export const required = helpers.withMessage('This field is required', (value: any) => {
  if (value === null || value === undefined) return false;
  if (isString(value)) return value.trim().length > 0;
  if (Array.isArray(value)) return value.length > 0;
  return true;
});

export const email = helpers.withMessage('Invalid email format', (value: string) => {
  return !value || isValidEmail(value);
});

export const minLength = (min: number) => 
  helpers.withMessage(`Must be at least ${min} characters`, 
    (value: string) => !value || value.length >= min
  );

export const maxLength = (max: number) =>
  helpers.withMessage(`Must be less than ${max} characters`,
    (value: string) => !value || value.length <= max
  );

export const numeric = helpers.withMessage('Must be a number', 
  (value: any) => !value || isNumber(Number(value))
);

export const minValue = (min: number) =>
  helpers.withMessage(`Must be at least ${min}`,
    (value: any) => !value || Number(value) >= min
  );

export const maxValue = (max: number) =>
  helpers.withMessage(`Must be less than or equal to ${max}`,
    (value: any) => !value || Number(value) <= max
  );
```

### Usage in Components
```vue
<script setup lang="ts">
import { required, email, minLength } from '@/validation/rules';
import { useVuelidate } from '@vuelidate/core';

const form = reactive({
  email: '',
  password: ''
});

const rules = {
  email: { required, email },
  password: { required, minLength: minLength(8) }
};

const v$ = useVuelidate(rules, form);
</script>
```

## API Integration

### API Client
Use a centralized API client with interceptors for consistent request/response handling:

```typescript
// services/api.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { useAuthStore } from '@/stores/auth';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore();
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          const authStore = useAuthStore();
          await authStore.logout();
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  // Add other HTTP methods as needed
}

export const api = new ApiClient();
```

### Service Layer
Organize API calls into service modules:

```typescript
// services/gl/accountService.ts
import { api } from '@/services/api';
import type { Account, AccountCreate, AccountUpdate } from '@/types/gl/account';

export const accountService = {
  async getAll(): Promise<Account[]> {
    return api.get<Account[]>('/gl/accounts');
  },

  async getById(id: string): Promise<Account> {
    return api.get<Account>(`/gl/accounts/${id}`);
  },

  async create(data: AccountCreate): Promise<Account> {
    return api.post<Account>('/gl/accounts', data);
  },

  async update(id: string, data: AccountUpdate): Promise<Account> {
    return api.put<Account>(`/gl/accounts/${id}`, data);
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/gl/accounts/${id}`);
  }
};
```

## Form Handling

### Composition API Pattern
Use the Composition API with TypeScript for form components:

```vue
<template>
  <form @submit.prevent="handleSubmit">
    <!-- Form fields -->
  </form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useVuelidate } from '@vuelidate/core';
import { required, email } from '@/validation/rules';
import { useNotification } from '@/composables/useNotification';
import { accountService } from '@/services/gl/accountService';

const props = defineProps<{
  accountId?: string;
}>();

const emit = defineEmits<{
  (e: 'success'): void;
  (e: 'cancel'): void;
}>();

const { showSuccess, showError } = useNotification();
const loading = ref(false);

// Form data
const form = reactive({
  name: '',
  code: '',
  type: 'ASSET',
  description: ''
});

// Validation rules
const rules = {
  name: { required },
  code: { required },
  type: { required }
};

const v$ = useVuelidate(rules, form);

// Load account data if in edit mode
if (props.accountId) {
  loadAccount();
}

async function loadAccount() {
  try {
    loading.value = true;
    const account = await accountService.getById(props.accountId!);
    Object.assign(form, account);
  } catch (error) {
    showError('Failed to load account');
    emit('cancel');
  } finally {
    loading.value = false;
  }
}

async function handleSubmit() {
  const isValid = await v$.value.$validate();
  if (!isValid) return;

  try {
    loading.value = true;
    
    if (props.accountId) {
      await accountService.update(props.accountId, form);
      showSuccess('Account updated successfully');
    } else {
      await accountService.create(form);
      showSuccess('Account created successfully');
    }
    
    emit('success');
  } catch (error) {
    showError('Failed to save account');
  } finally {
    loading.value = false;
  }
}
</script>
```

## State Management

### Pinia Store Pattern
```typescript
// stores/gl/accountStore.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { accountService, type Account } from '@/services/gl/accountService';

export const useAccountStore = defineStore('gl/account', () => {
  const accounts = ref<Account[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const assetAccounts = computed(() => 
    accounts.value.filter(a => a.type === 'ASSET')
  );

  const liabilityAccounts = computed(() => 
    accounts.value.filter(a => a.type === 'LIABILITY')
  );

  async function fetchAccounts() {
    try {
      loading.value = true;
      error.value = null;
      accounts.value = await accountService.getAll();
    } catch (e) {
      error.value = 'Failed to load accounts';
      console.error('Failed to load accounts:', e);
    } finally {
      loading.value = false;
    }
  }

  async function createAccount(data: AccountCreate) {
    try {
      loading.value = true;
      const account = await accountService.create(data);
      accounts.value.push(account);
      return account;
    } catch (e) {
      error.value = 'Failed to create account';
      console.error('Failed to create account:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  return {
    accounts,
    loading,
    error,
    assetAccounts,
    liabilityAccounts,
    fetchAccounts,
    createAccount
  };
});
```

## Error Handling

### Global Error Handler
```typescript
// utils/errorHandler.ts
import { useNotification } from '@/composables/useNotification';

export class AppError extends Error {
  constructor(
    message: string,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export function handleError(error: unknown, defaultMessage = 'An error occurred') {
  const { showError } = useNotification();
  
  if (error instanceof AppError) {
    showError(error.message);
    if (error.details) {
      console.error('Error details:', error.details);
    }
  } else if (error instanceof Error) {
    showError(error.message || defaultMessage);
    console.error(error);
  } else {
    showError(defaultMessage);
    console.error('Unknown error:', error);
  }
}
```

## Naming Conventions

### Files and Folders
- Use kebab-case for file and folder names: `account-service.ts`
- Component files should be PascalCase: `AccountForm.vue`
- Test files should match the source file with `.spec` or `.test` suffix

### Variables and Functions
- Use camelCase for variables and functions
- Use PascalCase for classes, interfaces, and type aliases
- Use UPPER_CASE for constants
- Prefix interfaces with `I` only when necessary
- Use descriptive names that indicate purpose

### Components
- Use multi-word component names to avoid conflicts with HTML elements
- Use PascalCase for component names in templates
- Use kebab-case for props and events

## File Structure

```
src/
├── assets/              # Static assets (images, fonts, etc.)
├── components/          # Reusable UI components
│   ├── common/          # Common components (buttons, inputs, etc.)
│   └── gl/              # GL module components
├── composables/         # Composition API functions
├── layouts/             # Layout components
├── router/              # Vue Router configuration
├── services/            # API services
│   └── gl/              # GL module services
├── stores/              # Pinia stores
│   └── gl/              # GL module stores
├── types/               # TypeScript type definitions
│   └── gl/              # GL module types
├── utils/               # Utility functions
├── views/               # Page components
│   └── gl/              # GL module views
├── App.vue              # Root component
└── main.ts              # Application entry point
```

## Code Organization

### Single File Components
```vue
<template>
  <!-- Template section -->
</template>

<script setup lang="ts">
// Script section with Composition API
</script>

<style scoped>
/* Component styles */
</style>
```

### Component Documentation
```vue
<template>
  <!-- Component template -->
</template>

<script setup lang="ts">
/**
 * ComponentName
 * 
 * @description Brief description of the component
 * 
 * @props {
 *   prop1 - Description of prop1
 *   prop2 - Description of prop2 with type and default
 * }
 * 
 * @emits event1 - Description of event1
 * @emits event2 - Description of event2
 */

// Component implementation
</script>
```

## Performance

### Optimization Techniques
1. Use `v-once` for static content
2. Use `v-memo` for expensive v-for renders
3. Lazy load components with `defineAsyncComponent`
4. Use `shallowRef` and `shallowReactive` for large data structures
5. Debounce expensive operations

### Performance Monitoring
```typescript
// utils/performance.ts
export function measurePerformance<T extends (...args: any[]) => any>(
  fn: T,
  name: string
): T {
  return ((...args: Parameters<T>): ReturnType<T> => {
    const start = performance.now();
    try {
      return fn(...args);
    } finally {
      const end = performance.now();
      console.log(`[Performance] ${name} took ${(end - start).toFixed(2)}ms`);
    }
  }) as T;
}
```
