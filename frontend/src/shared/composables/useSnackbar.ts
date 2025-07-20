import { ref } from 'vue';

export interface SnackbarMessage {
  text: string;
  color?: 'success' | 'error' | 'info' | 'warning';
  timeout?: number;
  showClose?: boolean;
}

export function useSnackbar() {
  const message = ref('');
  const color = ref('success');
  const show = ref(false);
  const timeout = ref(6000);
  const showClose = ref(true);

  function showMessage({ text, color: msgColor = 'success', timeout: msgTimeout = 6000, showClose: msgShowClose = true }: SnackbarMessage) {
    message.value = text;
    color.value = msgColor;
    timeout.value = msgTimeout;
    showClose.value = msgShowClose;
    show.value = true;
  }

  function showSuccess(text: string, msgTimeout: number = 6000) {
    showMessage({ text, color: 'success', timeout: msgTimeout });
  }

  function showError(text: string, msgTimeout: number = 10000) {
    showMessage({ text, color: 'error', timeout: msgTimeout });
  }

  function showInfo(text: string, msgTimeout: number = 4000) {
    showMessage({ text, color: 'info', timeout: msgTimeout });
  }

  function showWarning(text: string, msgTimeout: number = 8000) {
    showMessage({ text, color: 'warning', timeout: msgTimeout });
  }

  function close() {
    show.value = false;
  }

  return {
    message,
    color,
    show,
    timeout,
    showClose,
    showMessage,
    showSuccess,
    showError,
    showInfo,
    showWarning,
    close,
  };
}

export type Snackbar = ReturnType<typeof useSnackbar>;
