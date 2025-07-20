import { getCurrentInstance, type App } from 'vue';

export interface SnackbarMessage {
  message: string;
  type?: 'success' | 'error' | 'info' | 'warning';
  timeout?: number;
}

export function useSnackbar() {
  function showMessage({ message, type = 'info', timeout = 6000 }: SnackbarMessage) {
    const app = getCurrentInstance()?.appContext.app;
    if (!app) {
      console.warn('Snackbar not available - app instance not found');
      return;
    }
    
    // Emit event to the root component
    const root = app.config.globalProperties.$root;
    if (root) {
      root.$emit('show-snackbar', { message, type, timeout });
    } else {
      console.warn('Root instance not available for snackbar');
    }
  }

  function showSuccess(message: string, timeout: number = 6000) {
    showMessage({ message, type: 'success', timeout });
  }

  function showError(message: string, timeout: number = 10000) {
    showMessage({ message, type: 'error', timeout });
  }

  function showInfo(message: string, timeout: number = 4000) {
    showMessage({ message, type: 'info', timeout });
  }

  function showWarning(message: string, timeout: number = 8000) {
    showMessage({ message, type: 'warning', timeout });
  }

  return {
    showMessage,
    showSuccess,
    showError,
    showInfo,
    showWarning,
  };
}

export type Snackbar = ReturnType<typeof useSnackbar>;

// Plugin installation
export default {
  install(app: App) {
    const snackbar = useSnackbar();
    app.config.globalProperties.$snackbar = snackbar;
    app.provide('snackbar', snackbar);
  },
};
