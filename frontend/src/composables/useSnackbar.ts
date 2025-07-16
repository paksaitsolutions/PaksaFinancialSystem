import { ref, inject, InjectionKey, Ref, computed } from 'vue';

type SnackbarColor = 'success' | 'error' | 'warning' | 'info' | '';

interface SnackbarState {
  message: string;
  color: SnackbarColor;
  timeout: number;
  show: boolean;
}

interface SnackbarMethods {
  showMessage(message: string, color?: SnackbarColor, timeout?: number): void;
  success(message: string, timeout?: number): void;
  error(message: string, timeout?: number): void;
  warning(message: string, timeout?: number): void;
  info(message: string, timeout?: number): void;
}

const snackbarKey: InjectionKey<SnackbarMethods> = Symbol('snackbar');

export function useSnackbar() {
  const state = inject<Ref<SnackbarState>>('snackbarState');
  const methods = inject<SnackbarMethods>(snackbarKey);

  if (!state || !methods) {
    throw new Error('useSnackbar must be used within a SnackbarProvider');
  }

  return {
    ...methods,
    state: computed(() => state.value),
  };
}

export function createSnackbar() {
  const state = ref<SnackbarState>({
    message: '',
    color: '',
    timeout: 3000,
    show: false,
  });

  let timeoutId: number | null = null;

  const showMessage = (message: string, color: SnackbarColor = 'info', timeout: number = 3000) => {
    // Clear any existing timeout
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }

    // Update the state
    state.value = {
      message,
      color,
      timeout,
      show: true,
    };

    // Auto-hide after timeout
    if (timeout > 0) {
      timeoutId = window.setTimeout(() => {
        state.value.show = false;
        timeoutId = null;
      }, timeout);
    }
  };

  const success = (message: string, timeout: number = 3000) => {
    showMessage(message, 'success', timeout);
  };

  const error = (message: string, timeout: number = 5000) => {
    showMessage(message, 'error', timeout);
  };

  const warning = (message: string, timeout: number = 4000) => {
    showMessage(message, 'warning', timeout);
  };

  const info = (message: string, timeout: number = 3000) => {
    showMessage(message, 'info', timeout);
  };

  // Provide methods that can be used in components
  const methods: SnackbarMethods = {
    showMessage,
    success,
    error,
    warning,
    info,
  };

  return {
    state,
    methods,
    snackbarKey,
  };
}

export { SnackbarColor };
