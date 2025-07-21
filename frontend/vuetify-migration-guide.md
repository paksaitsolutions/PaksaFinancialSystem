# Vuetify 3 Migration Guide

This document outlines the migration from PrimeVue to Vuetify 3 in the Paksa Financial System frontend.

## Component Mappings

| PrimeVue Component | Vuetify 3 Equivalent | Notes |
|-------------------|----------------------|-------|
| Button | v-btn | Use `color="primary"` for primary actions |
| DataTable | v-data-table | Requires different props and slots |
| Column | v-data-table-column | Part of v-data-table |
| Dropdown | v-select or v-combobox | v-select for single select, v-combobox for searchable |
| Dialog | v-dialog | Similar functionality, different API |
| InputText | v-text-field | Similar but different props |
| Card | v-card | Similar structure |
| Toast | v-snackbar | Similar notification system |
| Calendar | v-date-picker | Similar date selection |
| ProgressBar | v-progress-linear | Similar progress indication |
| Tag | v-chip | Similar chip/tag component |
| Checkbox | v-checkbox | Similar functionality |
| Textarea | v-textarea | Similar multi-line input |
| Toolbar | v-toolbar | Similar toolbar component |
| Menu | v-menu | Similar dropdown menu |
| Sidebar | v-navigation-drawer | Similar sidebar/drawer |
| Panel | v-card | Use v-card with appropriate props |
| TabView | v-tabs | Similar tabbed interface |
| TabPanel | v-tab | Part of v-tabs |
| FileUpload | v-file-input | Similar file upload |
| InputNumber | v-text-field with type="number" | |
| InputSwitch | v-switch | Similar toggle switch |
| MultiSelect | v-select with multiple | Use v-select with multiple prop |
| Select | v-select | Similar select component |
| Slider | v-slider | Similar range input |
| ToggleButton | v-btn-toggle | Similar button group toggle |
| RadioButton | v-radio | Similar radio button |
| RadioGroup | v-radio-group | Group for radio buttons |
| Listbox | v-list | Similar list component |
| Tooltip | v-tooltip | Similar tooltip functionality |
| ConfirmDialog | v-dialog with v-card | Custom implementation needed |
| ContextMenu | v-menu | Similar context menu |
| Steps | v-stepper | Similar stepper component |
| Avatar | v-avatar | Similar avatar component |
| Badge | v-badge | Similar badge component |
| Chip | v-chip | Similar chip component |
| Chips | v-chip-group | Group of chips |

## Migration Steps

1. **Update Dependencies**
   - Remove PrimeVue related packages
   - Add Vuetify 3
   - Update main.ts to use Vuetify

2. **Global Styles**
   - Remove PrimeFlex classes
   - Update to Vuetify utility classes
   - Update theme configuration

3. **Component Refactoring**
   - Replace PrimeVue components with Vuetify equivalents
   - Update component props and events
   - Update slots and templates
   - Update form handling

4. **Testing**
   - Test each component after migration
   - Verify functionality and styling
   - Fix any issues that arise

## Common Patterns

### Forms
- Replace PrimeVue form components with v-form
- Use v-text-field, v-select, v-checkbox, etc.
- Update validation to use Vuetify's validation system

### Data Tables
- Replace DataTable with v-data-table
- Update column definitions
- Update sorting, filtering, and pagination

### Dialogs
- Replace Dialog with v-dialog
- Update dialog content structure
- Update dialog events

### Navigation
- Replace Menu and Menubar with v-navigation-drawer and v-app-bar
- Update navigation structure
- Update routing

## Best Practices

1. **Use Vuetify's Grid System**
   - Replace PrimeFlex grid with v-row and v-col
   - Use Vuetify's spacing utilities

2. **Theming**
   - Use Vuetify's theming system
   - Update color variables
   - Update typography

3. **Accessibility**
   - Ensure all components are accessible
   - Add ARIA attributes where needed
   - Test with screen readers

4. **Performance**
   - Use v-lazy for heavy components
   - Optimize v-for with :key
   - Use v-intersect for lazy loading

## Common Issues and Solutions

1. **Styling Conflicts**
   - Use deep selectors (>>> or ::v-deep) for custom styles
   - Use !important sparingly
   - Check Vuetify's CSS variables

2. **Missing Features**
   - Check Vuetify Labs for experimental components
   - Consider custom implementations
   - Look for Vuetify plugins

3. **Performance Issues**
   - Use v-virtual-scroll for large lists
   - Optimize v-data-table with server-side pagination
   - Use v-lazy for off-screen content

## Resources

- [Vuetify 3 Documentation](https://next.vuetifyjs.com/)
- [Vuetify Migration Guide](https://next.vuetifyjs.com/en/getting-started/migration/)
- [Vuetify Component Examples](https://next.vuetifyjs.com/en/components/all/)
