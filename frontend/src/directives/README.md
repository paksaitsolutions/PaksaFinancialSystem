# Vue Directives

This directory contains custom Vue directives used throughout the Paksa Financial System frontend. Directives are reusable functions that can be applied to DOM elements to add special behavior.

## Available Directives

### v-click-outside
Dismisses dropdowns, modals, or other UI elements when clicking outside of them.

### v-tooltip
Displays a tooltip when hovering over an element.

### v-has-permission
Conditionally renders elements based on user permissions.

### v-debounce
Limits how often a function can be called on events like window resize or input.

### v-copy
Copies text to the clipboard when the element is clicked.

## Usage

1. **Register Directives Globally**
   In your `main.js` or `app.js`:
   ```javascript
   import { createApp } from 'vue';
   import { clickOutside, tooltip, hasPermission, debounce, copy } from '@/directives';

   const app = createApp(App);
   
   // Register directives globally
   app.directive('click-outside', clickOutside);
   app.directive('tooltip', tooltip);
   app.directive('has-permission', hasPermission);
   app.directive('debounce', debounce);
   app.directing('copy', copy);
   ```

2. **Use in Templates**
   ```vue
   <template>
     <!-- Click outside directive -->
     <div v-click-outside="closeDropdown">
       <!-- Dropdown content -->
     </div>

     <!-- Tooltip directive -->
     <button v-tooltip="'Click to save changes'">Save</button>

     <!-- Permission directive -->
     <button v-has-permission="'edit_transactions'">Edit</button>

     <!-- Debounce input -->
     <input v-debounce:input="search" placeholder="Search...">

     <!-- Copy to clipboard -->
     <button v-copy="textToCopy">Copy Text</button>
   </template>
   ```

## Creating a New Directive

1. Create a new file in this directory (e.g., `my-directive.js`)
2. Define your directive logic:
   ```javascript
   export default {
     beforeMount(el, binding) {
       // Directive logic here
     },
     // Other lifecycle hooks as needed
   };
   ```
3. Export it in `index.js`:
   ```javascript
   export { default as myDirective } from './my-directive';
   ```
4. Register it in your Vue application

## Best Practices

- Keep directive logic focused and reusable
- Document the directive's purpose, parameters, and usage
- Follow Vue's naming conventions (kebab-case in templates)
- Consider accessibility when adding interactive behavior
