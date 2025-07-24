// frontend/src/main.ts
import { createApp } from 'vue';
import App from './App.vue';
import { createPinia } from 'pinia';
import router from './router';
import './assets/styles/reset.css';
import './assets/styles/theme.css';
import './assets/styles/responsive.css';

// Vuetify
import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg';

// Create app and plugins
const app = createApp(App);
const pinia = createPinia();

// Configure Vuetify
const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
  },
  defaults: {
    VBtn: {
      variant: 'flat',
    },
  },
});

// Use plugins
app.use(pinia);
app.use(router);
app.use(vuetify);

// Initialize theme
import { useThemeStore } from './stores/theme';
const themeStore = useThemeStore();
themeStore.loadThemePreference();

// Mount the app
app.mount('#app');