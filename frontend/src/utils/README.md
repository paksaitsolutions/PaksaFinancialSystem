# Utility Functions

This directory contains reusable utility functions and composables for the Paksa Financial System frontend. These utilities provide common functionality that can be used across different components and modules.

## Available Utilities

### Form Validation (`validators.ts`)

A comprehensive form validation system that provides:

- **Validation Rules**: Common validators like required, email, password strength, min/max length, etc.
- **Composable API**: Easy-to-use composables for form validation
- **Custom Validators**: Create custom validation rules
- **Form State Management**: Track form validity, dirty state, and errors

#### Usage Example

```vue
<script setup>
import { useValidators, useFormValidation } from '@/utils/validators';

const { required, email, minLength } = useValidators();
const { errors, validateField, validateForm } = useFormValidation();

const form = reactive({
  email: '',
  password: '',
});

const rules = {
  email: [
    required('Email is required'),
    email(),
  ],
  password: [
    required('Password is required'),
    minLength(8),
  ],
};

// Validate a single field
const onEmailBlur = () => {
  validateField('email', form.email, rules.email);
};

// Validate the entire form
const onSubmit = () => {
  const isValid = validateForm({
    email: { value: form.email, validators: rules.email },
    password: { value: form.password, validators: rules.password },
  });
  
  if (isValid) {
    // Submit the form
  }
};
</script>

<template>
  <form @submit.prevent="onSubmit">
    <div>
      <label>Email</label>
      <input 
        v-model="form.email" 
        @blur="onEmailBlur"
        :class="{ 'error': errors.email }"
      />
      <div v-if="errors.email" class="error-message">
        {{ errors.email }}
      </div>
    </div>
    
    <div>
      <label>Password</label>
      <input 
        v-model="form.password" 
        type="password"
        :class="{ 'error': errors.password }"
      />
      <div v-if="errors.password" class="error-message">
        {{ errors.password }}
      </div>
    </div>
    
    <button type="submit">Submit</button>
  </form>
</template>
```

### API Client (`api.ts`)

A centralized API client for making HTTP requests with built-in error handling, authentication, and request/response interceptors.

#### Features

- Automatic JWT token handling
- Request/response interceptors
- Error handling and notifications
- Request cancellation
- Response caching

#### Usage Example

```typescript
import { api } from '@/utils/api';

// GET request
const fetchData = async () => {
  try {
    const response = await api.get('/api/endpoint');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch data:', error);
    throw error;
  }
};

// POST request
const createItem = async (data) => {
  try {
    const response = await api.post('/api/items', data);
    return response.data;
  } catch (error) {
    console.error('Failed to create item:', error);
    throw error;
  }
};
```

### Date Utilities (`date.ts`)

Helper functions for working with dates and times.

#### Features

- Date formatting and parsing
- Date manipulation (add/subtract days, months, years)
- Date comparison
- Business day calculations

#### Usage Example

```typescript
import { formatDate, addDays, isWeekend } from '@/utils/date';

// Format a date
const formattedDate = formatDate(new Date(), 'yyyy-MM-dd');

// Add days to a date
const nextWeek = addDays(new Date(), 7);

// Check if a date is a weekend
const isWeekendDay = isWeekend(new Date());
```

### Number Formatting (`number.ts`)

Utilities for formatting and parsing numbers, currencies, and percentages.

#### Features

- Currency formatting
- Number formatting with thousands separators
- Percentage formatting
- Rounding and precision control

#### Usage Example

```typescript
import { formatCurrency, formatNumber, formatPercentage } from '@/utils/number';

// Format currency
const price = formatCurrency(1234.56, 'USD'); // $1,234.56

// Format number with thousands separator
const largeNumber = formatNumber(1000000); // 1,000,000

// Format percentage
const percentage = formatPercentage(0.1234); // 12.34%
```

### String Utilities (`string.ts`)

Helper functions for working with strings.

#### Features

- Truncation
- Capitalization
- URL slug generation
- String manipulation

#### Usage Example

```typescript
import { truncate, capitalize, toSlug } from '@/utils/string';

// Truncate a string
const shortText = truncate('This is a long text', 10); // 'This is a...'

// Capitalize the first letter
const name = capitalize('john'); // 'John'

// Generate a URL slug
const slug = toSlug('My Awesome Post'); // 'my-awesome-post'
```

### Storage Utilities (`storage.ts`)

Wrapper around localStorage and sessionStorage with type safety and expiration support.

#### Features

- Type-safe storage
- Automatic JSON serialization/deserialization
- Expiration support
- Namespacing

#### Usage Example

```typescript
import { createStorage } from '@/utils/storage';

// Create a namespaced storage
const userStorage = createStorage('user');

// Set a value
userStorage.set('token', 'abc123', 24 * 60 * 60 * 1000); // Expires in 24 hours

// Get a value
const token = userStorage.get('token');

// Remove a value
userStorage.remove('token');

// Clear all values
userStorage.clear();
```

## Adding New Utilities

1. Create a new TypeScript file in this directory
2. Export your utility functions from the file
3. Add documentation in this README.md file
4. Update the `index.ts` file to export your new utility

## Best Practices

- Keep utility functions pure and stateless when possible
- Add TypeScript types for all parameters and return values
- Write unit tests for all utility functions
- Document usage examples in this README
- Handle errors appropriately
- Consider performance implications for utility functions that process large amounts of data
