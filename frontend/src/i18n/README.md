# Internationalization (i18n)

This directory contains all internationalization and localization configurations for the Paksa Financial System frontend. The application supports multiple languages including English, Urdu, and Arabic with RTL (Right-to-Left) language support.

## Directory Structure

```
i18n/
├── en/                    # English translations
│   ├── common.json        # Common UI elements
│   ├── dashboard.json     # Dashboard specific translations
│   ├── auth.json         # Authentication related translations
│   └── ...
├── ur/                    # Urdu translations
│   └── ...
├── ar/                    # Arabic translations (RTL)
│   └── ...
└── index.js              # i18n configuration
```

## Supported Languages

- English (en) - Default
- Urdu (ur)
- Arabic (ar) - RTL

## Adding a New Language

1. Create a new directory for the language code (e.g., `es` for Spanish)
2. Copy the translation files from the `en` directory
3. Translate all the strings in each JSON file
4. Update the `i18n/index.js` file to include the new language:
   ```javascript
   import en from './en';
   import ur from './ur';
   import ar from './ar';
   import es from './es'; // New language
   
   export const messages = {
     en,
     ur,
     ar,
     es // Add new language
   };
   ```

## Using Translations in Components

### Composition API
```vue
<template>
  <div>{{ $t('common.welcome') }}</div>
  <div>{{ $t('dashboard.greeting', { name: user.name }) }}</div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
console.log(t('common.welcome'));
</script>
```

### Options API
```vue
<template>
  <div>{{ $t('common.welcome') }}</div>
  <div>{{ greeting }}</div>
</template>

<script>
export default {
  computed: {
    greeting() {
      return this.$t('dashboard.greeting', { name: this.user.name });
    }
  }
};
</script>
```

## Translation Files Structure

Each language directory should contain JSON files with the same structure. For example:

```json
// en/common.json
{
  "common": {
    "welcome": "Welcome to Paksa Financial System",
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "search": "Search..."
  }
}
```

## RTL Language Support

For RTL languages like Arabic, the application automatically applies RTL styling when the language is switched. This is handled by the `dir` attribute on the HTML element and corresponding CSS classes.

## Best Practices

1. **Use Namespacing**: Group related translations under appropriate namespaces (e.g., `auth.login`, `dashboard.summary`)
2. **Reuse Common Terms**: Avoid duplicating common terms across different files
3. **Parameterize Strings**: Use placeholders for dynamic content (e.g., `"welcome": "Welcome, {name}!")`
4. **Keep Translations Consistent**: Maintain consistent terminology across all languages
5. **Pluralization**: Handle plural forms appropriately in each language

## Adding New Translation Keys

1. Add the new key to the English translation file first
2. Add the corresponding translations to other language files
3. Use the key in your components
4. Test the translation in all supported languages
