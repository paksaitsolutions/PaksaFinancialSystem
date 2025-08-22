# Application Constants

This directory contains all application-wide constants used throughout the Paksa Financial System frontend.

## Structure

- **`api.ts`** - API endpoints and related constants
- **`app.ts`** - Application-wide configuration constants
- **`routes.ts`** - Route names and paths
- **`validation.ts`** - Form validation rules and messages

## Usage

Import constants as needed in your components or services:

```typescript
import { API_ENDPOINTS } from '@/constants/api';
import { APP_NAME, VERSION } from '@/constants/app';
import { ROUTE_NAMES } from '@/constants/routes';
import { VALIDATION_MESSAGES } from '@/constants/validation';
```

## Adding New Constants

1. Choose the appropriate file based on the constant's purpose
2. Use `PascalCase` for constant groups and `UPPER_SNAKE_CASE` for individual constants
3. Add JSDoc comments for documentation
4. Export all constants from the `index.ts` file

Example:

```typescript
/**
 * API configuration constants
 */
export const API_CONFIG = {
  TIMEOUT: 30000,
  MAX_RETRIES: 3,
} as const;
```
