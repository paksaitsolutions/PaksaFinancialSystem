# Paksa Financial System - Vuetify Style Guide

This style guide defines the design system and component usage patterns for the Paksa Financial System frontend, ensuring consistency and maintainability across the application.

## Table of Contents
- [Design Tokens](#design-tokens)
- [Typography](#typography)
- [Color System](#color-system)
- [Spacing](#spacing)
- [Component Patterns](#component-patterns)
- [Layout Guidelines](#layout-guidelines)
- [Motion & Interaction](#motion--interaction)
- [Accessibility](#accessibility)
- [Code Style](#code-style)

## Design Tokens

### Breakpoints

| Name      | Value    | Usage                      |
|-----------|----------|----------------------------|
| xs        | 0px      | Mobile phones              |
| sm        | 600px    | Tablets                    |
| md        | 960px    | Small laptops              |
| lg        | 1280px   | Desktops                   |
| xl        | 1920px   | Large desktops             |

### Elevation

| Level | Value | Usage                                  |
|-------|-------|----------------------------------------|
| 0     | 0     | Flat surfaces, cards at rest           |
| 1     | 2px   | Raised buttons, cards on mobile        |
| 2     | 4px   | Cards on desktop, dropdowns            |
| 3     | 8px   | Dialogs, modals                        |
| 4     | 16px  | Navigation drawer, app bar (elevated)  |

## Typography

### Type Scale

| Element          | Font Size | Line Height | Font Weight | Letter Spacing |
|------------------|-----------|-------------|-------------|----------------|
| H1               | 2.5rem    | 3rem        | 300         | -0.0156em      |
| H2               | 2rem      | 2.5rem      | 300         | -0.0089em      |
| H3               | 1.75rem   | 2.25rem     | 400         | 0              |
| H4               | 1.5rem    | 2rem        | 400         | 0.0074em       |
| H5               | 1.25rem   | 2rem        | 400         | 0              |
| H6               | 1.125rem  | 1.75rem     | 500         | 0.0094em       |
| Subtitle 1       | 1rem      | 1.75rem     | 400         | 0.0094em       |
| Subtitle 2       | 0.875rem  | 1.375rem    | 500         | 0.0067em       |
| Body 1           | 1rem      | 1.5rem      | 400         | 0.0313em       |
| Body 2           | 0.875rem  | 1.25rem     | 400         | 0.0179em       |
| Button           | 0.875rem  | 2.25rem     | 500         | 0.0893em       |
| Caption          | 0.75rem   | 1.25rem     | 400         | 0.0333em       |
| Overline         | 0.75rem   | 2rem        | 500         | 0.1667em       |

### Usage in Vuetify

```vue
<template>
  <div>
    <h1 class="text-h1">Heading 1</h1>
    <h2 class="text-h2">Heading 2</h2>
    <p class="text-body-1">Body text</p>
    <p class="text-caption">Caption text</p>
  </div>
</template>
```

## Color System

### Primary Colors

| Name          | Hex       | Usage                          |
|---------------|-----------|--------------------------------|
| Primary       | #1976D2   | Primary brand color, actions   |
| Primary Dark  | #1565C0   | Hover/focus states             |
| Primary Light | #E3F2FD   | Backgrounds, highlights        |

### Semantic Colors

| Name      | Hex       | Usage                          |
|-----------|-----------|--------------------------------|
| Success   | #4CAF50   | Success messages, completed    |
| Warning   | #FFC107   | Warnings, attention needed     |
| Error     | #F44336   | Error messages, destructive    |
| Info      | #2196F3   | Informational messages         |

### Neutral Colors

| Name          | Hex       | Usage                          |
|---------------|-----------|--------------------------------|
| Background   | #FFFFFF   | Main background               |
| Surface      | #F5F5F5   | Cards, sheets, menus          |
| Border       | #E0E0E0   | Dividers, borders             |
| Text Primary | #212121   | Primary text                  |
| Text Secondary | #757575 | Secondary text               |
| Disabled     | #BDBDBD   | Disabled elements             |

### Usage in Vuetify

```vue
<template>
  <div>
    <v-btn color="primary">Primary Button</v-btn>
    <v-alert color="success">Success message</v-alert>
    <v-card class="bg-surface">Content</v-card>
  </div>
</template>
```

## Spacing

### Spacing Scale

| Size | Value | Usage                          |
|------|-------|--------------------------------|
| xs   | 4px   | Small spacing between elements |
| sm   | 8px   | Default spacing                |
| md   | 16px  | Section spacing                |
| lg   | 24px  | Large spacing                  |
| xl   | 48px  | Extra large spacing            |

### Usage

```vue
<template>
  <div class="ma-4"> <!-- Margin all around -->
    <v-card class="pa-4"> <!-- Padding all around -->
      <div class="mb-4">Margin bottom</div>
      <div class="ml-2">Margin left</div>
    </v-card>
  </div>
</template>
```

## Component Patterns

### Buttons

#### Primary Button
- Use for primary actions
- Always include a clear label
- Use `prepend-icon` for better scannability

```vue
<v-btn
  color="primary"
  prepend-icon="mdi-content-save"
  @click="save"
>
  Save Changes
</v-btn>
```

#### Secondary Button
- Use for secondary actions
- Use `variant="outlined"`

```vue
<v-btn
  variant="outlined"
  @click="cancel"
>
  Cancel
</v-btn>
```

### Cards

#### Standard Card
- Use `elevation` for depth
- Include proper spacing
- Use consistent corner radius

```vue
<v-card
  elevation="2"
  rounded="lg"
  class="pa-4"
>
  <v-card-title>Card Title</v-card-title>
  <v-divider class="my-4" />
  <v-card-text>
    Card content
  </v-card-text>
</v-card>
```

### Forms

#### Form Layout
- Use `v-form` for all forms
- Group related fields
- Use consistent field spacing

```vue
<v-form @submit.prevent="submit">
  <v-row>
    <v-col cols="12" md="6">
      <v-text-field
        v-model="form.firstName"
        label="First Name"
        :rules="[required]"
        density="comfortable"
        variant="outlined"
      />
    </v-col>
    <v-col cols="12" md="6">
      <v-text-field
        v-model="form.lastName"
        label="Last Name"
        :rules="[required]"
        density="comfortable"
        variant="outlined"
      />
    </v-col>
  </v-row>
  
  <div class="d-flex justify-end mt-4">
    <v-btn
      variant="text"
      class="mr-2"
      @click="cancel"
    >
      Cancel
    </v-btn>
    <v-btn
      type="submit"
      color="primary"
      :loading="loading"
    >
      Save Changes
    </v-btn>
  </div>
</v-form>
```

## Layout Guidelines

### Page Layout

```vue
<template>
  <v-app>
    <app-navigation />
    
    <v-app-bar color="primary" :elevation="1">
      <v-app-bar-nav-icon @click="toggleDrawer" />
      <v-toolbar-title>Page Title</v-toolbar-title>
      <v-spacer />
      <!-- Actions -->
    </v-app-bar>
    
    <v-main>
      <v-container fluid class="pa-4">
        <!-- Page content -->
      </v-container>
    </v-main>
    
    <v-footer app inset>
      <v-spacer />
      <div class="text-caption">
        &copy; {{ new Date().getFullYear() }} Paksa Financial System
      </div>
    </v-footer>
  </v-app>
</template>
```

### Grid System
- Use `v-row` and `v-col` for layouts
- Use breakpoint suffixes for responsive behavior
- Keep gutters consistent

```vue
<v-row>
  <v-col cols="12" md="8">
    <!-- Main content -->
  </v-col>
  <v-col cols="12" md="4">
    <!-- Sidebar -->
  </v-col>
</v-row>
```

## Motion & Interaction

### Transitions
- Use `v-fade-transition` for fades
- Use `v-slide-x-transition` for horizontal slides
- Keep transitions subtle and purposeful

```vue
<v-fade-transition mode="out-in">
  <router-view />
</v-fade-transition>
```

### Loading States
- Use `v-progress-linear` for page loads
- Use `v-skeleton-loader` for content placeholders
- Show loading states for async operations

```vue
<v-btn
  color="primary"
  :loading="saving"
  @click="save"
>
  Save Changes
</v-btn>
```

## Accessibility

### Keyboard Navigation
- Ensure all interactive elements are focusable
- Maintain logical tab order
- Use `tabindex="0"` for custom interactive elements

### ARIA Labels
- Add `aria-label` to icon buttons
- Use descriptive labels for form controls
- Include `aria-live` for dynamic content

```vue
<v-btn
  icon
  aria-label="Search"
  @click="search"
>
  <v-icon>mdi-magnify</v-icon>
</v-btn>
```

## Code Style

### Component Structure
1. Template
2. Script
3. Style

### Props Order
1. v-model
2. v-if/v-show
3. v-for
4. id/ref/key
5. Other directives
6. Props
7. Events
8. Slots

### Example Component

```vue
<template>
  <v-card
    :elevation="elevation"
    :class="$style.card"
    @click="$emit('click', $event)"
  >
    <v-card-title class="text-h6">
      {{ title }}
    </v-card-title>
    
    <v-card-text>
      <slot />
    </v-card-text>
    
    <v-card-actions v-if="$slots.actions">
      <slot name="actions" />
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'AppCard',
  
  props: {
    title: {
      type: String,
      required: true,
    },
    elevation: {
      type: [Number, String],
      default: 2,
    },
  },
  
  emits: ['click'],
});
</script>

<style module>
.card {
  transition: box-shadow 0.2s ease-in-out;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}
</style>
```

## Best Practices

### Do
- Use Vuetify components consistently
- Follow the 8px grid system
- Use theme variables for colors and spacing
- Keep components focused and reusable
- Write accessible markup

### Don't
- Override Vuetify styles with `!important`
- Use inline styles
- Create custom components when Vuetify provides an equivalent
- Skip accessibility considerations

## Resources
- [Vuetify Documentation](https://vuetifyjs.com/)
- [Material Design Guidelines](https://material.io/design)
- [WCAG 2.1 Guidelines](https://www.w3.org/TR/WCAG21/)
