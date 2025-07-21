# Vuetify 3 Component Usage Guide

This document outlines the standard patterns and best practices for using Vuetify 3 components in the Paksa Financial System.

## Table of Contents
- [Layout Components](#layout-components)
- [Form Components](#form-components)
- [Navigation Components](#navigation-components)
- [Data Display](#data-display)
- [Feedback Components](#feedback-components)
- [Utility Components](#utility-components)
- [Theming & Styling](#theming--styling)
- [Accessibility](#accessibility)

## Layout Components

### v-app
- **Always** wrap your entire application in a `v-app` component
- Only one `v-app` should exist in your application

```vue
<template>
  <v-app>
    <!-- Application content -->
  </v-app>
</template>
```

### v-main
- Use `v-main` as the main content container
- Place it inside `v-app`
- Use `:class` for responsive padding/margins

```vue
<v-main :class="{ 'px-4 py-2': $vuetify.display.mdAndUp }">
  <router-view />
</v-main>
```

### v-container
- Use for responsive content containers
- Prefer `fluid` for full-width layouts
- Use `max-width` props for content width control

```vue
<v-container fluid>
  <!-- Content -->
</v-container>
```

## Form Components

### v-form
- Wrap all forms with `v-form`
- Use `ref` for form validation
- Handle submission with `@submit.prevent`

```vue
<v-form ref="form" @submit.prevent="submit">
  <!-- Form fields -->
  <v-btn type="submit" color="primary">Submit</v-btn>
</v-form>
```

### Form Fields
- Use `v-model` for two-way binding
- Always include `:label` and `:rules` props
- Use `density` for consistent sizing

```vue
<v-text-field
  v-model="email"
  label="Email"
  :rules="[v => !!v || 'Email is required']"
  density="comfortable"
  variant="outlined"
/>
```

## Navigation Components

### v-navigation-drawer
- Use for main application navigation
- Include `rail` variant for collapsed state
- Use `v-model` for drawer state

```vue
<v-navigation-drawer
  v-model="drawer"
  :rail="rail"
  permanent
  @click="rail = false"
>
  <!-- Navigation items -->
</v-navigation-drawer>
```

### v-toolbar / v-app-bar
- Use for application headers
- Include navigation controls and user menu
- Use `elevation` for depth

```vue
<v-app-bar color="primary" :elevation="1">
  <v-app-bar-nav-icon @click="toggleDrawer" />
  <v-toolbar-title>Page Title</v-toolbar-title>
  <v-spacer />
  <!-- Actions -->
</v-app-bar>
```

## Data Display

### v-data-table
- Use for tabular data
- Include `:headers` and `:items`
- Use `:loading` for async data

```vue
<v-data-table
  :headers="headers"
  :items="items"
  :loading="loading"
  item-value="id"
  class="elevation-1"
>
  <!-- Custom columns -->
</v-data-table>
```

### v-card
- Use for content containers
- Include `elevation` and `rounded` props
- Use `variant="tonal"` for secondary content

```vue
<v-card
  elevation="2"
  rounded="lg"
  class="pa-4"
>
  <v-card-title>Card Title</v-card-title>
  <v-card-text>
    <!-- Content -->
  </v-card-text>
</v-card>
```

## Feedback Components

### v-alert
- Use for important messages
- Include `type` and `density` props
- Use `variant="tonal"` for subtle alerts

```vue
<v-alert
  type="success"
  variant="tonal"
  density="comfortable"
  class="mb-4"
>
  Operation completed successfully
</v-alert>
```

### v-dialog
- Use for modal dialogs
- Include `v-model` for visibility
- Use `persistent` for important actions

```vue
<v-dialog v-model="dialog" max-width="500">
  <template v-slot:activator="{ props }">
    <v-btn v-bind="props">Open Dialog</v-btn>
  </template>
  
  <v-card>
    <v-card-title>Dialog Title</v-card-title>
    <v-card-text>
      <!-- Dialog content -->
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn @click="dialog = false">Cancel</v-btn>
      <v-btn color="primary" @click="confirm">Confirm</v-btn>
    </v-card-actions>
  </v-card>
</v-dialog>
```

## Utility Components

### v-btn
- Use `variant` for different styles
- Include `prepend-icon` or `append-icon`
- Use `:loading` for async actions

```vue
<v-btn
  color="primary"
  variant="flat"
  prepend-icon="mdi-content-save"
  :loading="saving"
  @click="save"
>
  Save Changes
</v-btn>
```

### v-icon
- Use Material Design Icons with `mdi-` prefix
- Include `start` or `end` for proper spacing
- Use `size` for consistent sizing

```vue
<v-icon start>mdi-account</v-icon> Profile
```

## Theming & Styling

### Colors
- Use theme colors with `color` prop
- Access theme colors in SCSS with `map-get`

```scss.my-custom-class {
  background-color: map-get($colors, 'primary');
  color: map-get($on-colors, 'primary');
}
```

### Spacing
- Use utility classes for consistent spacing
- Follow the 8px grid system
- Use `ma-*`, `pa-*` classes

```vue
<v-card class="ma-4 pa-4">
  <!-- Content -->
</v-card>
```

## Accessibility

### ARIA Attributes
- Vuetify adds many ARIA attributes automatically
- Add `aria-label` to icon buttons
- Use `role` attributes when needed

```vue
<v-btn
  icon
  aria-label="Close dialog"
  @click="closeDialog"
>
  <v-icon>mdi-close</v-icon>
</v-btn>
```

### Keyboard Navigation
- All interactive elements should be focusable
- Use `tabindex="0"` for custom interactive elements
- Implement keyboard event handlers where needed

## Best Practices

1. **Component Composition**
   - Break down complex UIs into smaller components
   - Use slots for flexible component APIs
   - Keep components focused on a single responsibility

2. **Performance**
   - Use `v-lazy` for below-the-fold content
   - Implement virtual scrolling for long lists
   - Use `v-intersect` for lazy loading

3. **State Management**
   - Use Pinia for global state
   - Keep form state local when possible
   - Use computed properties for derived state

4. **Error Handling**
   - Validate form inputs
   - Show meaningful error messages
   - Log errors to your error tracking service

5. **Testing**
   - Test component interactions
   - Test form validation
   - Test accessibility
