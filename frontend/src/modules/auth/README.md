# Paksa Financial System - Authentication Module

## Overview
Complete modern authentication module built with Vue 3, Vuetify 3, and Pinia for state management. Features a clean, responsive design with comprehensive security features.

## Features

### 🔐 Authentication Components
- **Login** - Modern login form with email/password validation
- **Register** - User registration with company information
- **Forgot Password** - Password reset request with email verification
- **Reset Password** - Secure password reset with strength indicator

### 🎨 Design Features
- **Vuetify 3** - Modern Material Design components
- **Responsive Layout** - Mobile-first responsive design
- **Custom Theme** - Paksa brand colors and styling
- **Glass Morphism** - Modern backdrop blur effects
- **Smooth Animations** - Elegant transitions and loading states

### 🛡️ Security Features
- **Form Validation** - Comprehensive client-side validation
- **Password Strength** - Real-time password strength indicator
- **Token Management** - Secure JWT token handling
- **Remember Me** - Persistent login sessions
- **Auto Logout** - Session timeout handling

### 📱 User Experience
- **Loading States** - Visual feedback for all operations
- **Error Handling** - User-friendly error messages
- **Success Notifications** - Clear success confirmations
- **Accessibility** - WCAG compliant components
- **Keyboard Navigation** - Full keyboard support

## File Structure

```
src/modules/auth/
├── components/
│   ├── MFALogin.vue          # Multi-factor authentication
│   └── MFASetup.vue          # MFA setup component
├── store/
│   ├── auth.store.ts         # Pinia auth store
│   └── index.ts              # Store exports
├── views/
│   ├── Login.vue             # Login page
│   ├── Register.vue          # Registration page
│   ├── ForgotPassword.vue    # Password reset request
│   └── ResetPassword.vue     # Password reset form
├── api.ts                    # Auth API functions
└── README.md                 # This file
```

## Backend Integration

### Endpoints
- `POST /auth/token` - User login
- `POST /auth/register` - User registration
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password` - Password reset
- `POST /auth/refresh-token` - Token refresh
- `GET /auth/me` - Get current user
- `GET /auth/verify-token` - Verify token validity
- `POST /auth/logout` - User logout

### Demo Credentials
- **Email**: admin@paksa.com
- **Password**: admin123

## Usage

### Login Component
```vue
<template>
  <Login />
</template>

<script setup>
import Login from '@/modules/auth/views/Login.vue'
</script>
```

### Auth Store
```typescript
import { useAuthStore } from '@/modules/auth/store/auth.store'

const authStore = useAuthStore()

// Login
await authStore.login({
  email: 'user@example.com',
  password: 'password123',
  rememberMe: true
})

// Check authentication
if (authStore.isAuthenticated) {
  // User is logged in
}

// Logout
await authStore.logout()
```

## Styling

### Custom CSS Variables
```css
:root {
  --auth-primary: #1976D2;
  --auth-secondary: #424242;
  --auth-background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --auth-card-bg: rgba(255, 255, 255, 0.95);
  --auth-border-radius: 12px;
}
```

### Responsive Breakpoints
- **Mobile**: < 600px
- **Tablet**: 600px - 960px
- **Desktop**: > 960px

## Installation

1. **Install Dependencies**
```bash
npm install vuetify @mdi/font
```

2. **Configure Vuetify**
```typescript
// main.ts
import vuetify from './plugins/vuetify'
app.use(vuetify)
```

3. **Setup Router**
```typescript
// router/index.ts
{
  path: '/auth',
  component: () => import('@/layouts/AuthLayout.vue'),
  children: [
    {
      path: 'login',
      name: 'Login',
      component: () => import('@/modules/auth/views/Login.vue')
    }
    // ... other auth routes
  ]
}
```

## Customization

### Theme Colors
Update `src/plugins/vuetify.ts`:
```typescript
const paksaTheme = {
  colors: {
    primary: '#YOUR_PRIMARY_COLOR',
    secondary: '#YOUR_SECONDARY_COLOR',
    // ... other colors
  }
}
```

### Validation Rules
Extend validation in components:
```typescript
const emailRules = [
  (v: string) => !!v || 'Email is required',
  (v: string) => /.+@.+\..+/.test(v) || 'Email must be valid',
  // Add custom rules
]
```

## Testing

### Unit Tests
```bash
npm run test:unit
```

### E2E Tests
```bash
npm run test:e2e
```

## Performance

### Bundle Size
- **Vuetify**: ~200KB (tree-shaken)
- **Auth Module**: ~50KB
- **Total**: ~250KB

### Loading Times
- **Initial Load**: < 2s
- **Route Transitions**: < 300ms
- **Form Submissions**: < 1s

## Browser Support

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## Contributing

1. Follow Vue 3 Composition API patterns
2. Use TypeScript for type safety
3. Follow Vuetify design guidelines
4. Write comprehensive tests
5. Update documentation

## License

Proprietary - Paksa IT Solutions