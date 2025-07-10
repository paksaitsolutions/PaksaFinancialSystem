/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_NAME: string;
  readonly VITE_APP_VERSION: string;
  readonly VITE_API_BASE_URL: string;
  readonly VITE_APP_ENV: 'development' | 'production' | 'test';
  // Add more environment variables here as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
