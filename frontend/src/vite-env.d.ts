/// <reference types="vite/client" />
/// <reference types="vite-plugin-pages/client" />
/// <reference types="vite-plugin-vue-layouts/client" />
/// <reference types="unplugin-vue-router/client" />
/// <reference types="primevue/global" />

// Vue SFC module declarations
declare module '*.vue' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

// Image and asset module declarations
declare module '*.png' {
  const src: string;
  export default src;
}

declare module '*.jpg' {
  const src: string;
  export default src;
}

declare module '*.jpeg' {
  const src: string;
  export default src;
}

declare module '*.gif' {
  const src: string;
  export default src;
}

declare module '*.svg' {
  const src: string;
  export default src;
  export const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement>>;
}

declare module '*.svg?component' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

declare module '*.svg?url' {
  const src: string;
  export default src;
}

// Style module declarations
declare module '*.module.css' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

declare module '*.module.scss' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

declare module '*.module.sass' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

declare module '*.module.less' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

// Environment variables
type EnvType = 'development' | 'production' | 'test' | 'staging';

interface ImportMetaEnv {
  // App Info
  readonly VITE_APP_NAME: string;
  readonly VITE_APP_VERSION: string;
  readonly VITE_APP_DESCRIPTION: string;
  
  // Environment
  readonly VITE_APP_ENV: EnvType;
  readonly VITE_APP_DEBUG: boolean;
  
  // API Configuration
  readonly VITE_API_BASE_URL: string;
  readonly VITE_API_PREFIX: string;
  readonly VITE_API_TIMEOUT: string;
  
  // Authentication
  readonly VITE_AUTH_TOKEN_KEY: string;
  readonly VITE_REFRESH_TOKEN_KEY: string;
  readonly VITE_TOKEN_EXPIRY_KEY: string;
  
  // Feature Flags
  readonly VITE_FEATURE_ANALYTICS: boolean;
  readonly VITE_FEATURE_MAINTENANCE: boolean;
  
  // Third-party Services
  readonly VITE_GOOGLE_ANALYTICS_ID: string;
  readonly VITE_SENTRY_DSN: string;
  
  // Add more environment variables as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// PrimeVue component type declarations
declare module 'primevue/*' {
  import { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

// Global type augmentations
declare global {
  interface Window {
    __APP_VERSION__: string;
    __APP_ENV__: EnvType;
    // Add any global browser extensions or polyfills here
  }
}

// Vue Router type extensions
import 'vue-router';

declare module 'vue-router' {
  interface RouteMeta {
    // Add custom route meta fields here
    requiresAuth?: boolean;
    roles?: string[];
    permissions?: string[];
    title?: string;
    icon?: string;
    hidden?: boolean;
    keepAlive?: boolean;
    breadcrumb?: boolean;
  }
}

// Pinia Store type extensions
import { PiniaCustomProperties } from 'pinia';

declare module 'pinia' {
  export interface PiniaCustomProperties {
    // Add custom store properties here
    $api: {
      get: <T>(url: string, config?: any) => Promise<T>;
      post: <T>(url: string, data?: any, config?: any) => Promise<T>;
      put: <T>(url: string, data?: any, config?: any) => Promise<T>;
      delete: <T>(url: string, config?: any) => Promise<T>;
    };
  }
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
