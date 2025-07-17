import { ref } from 'vue';

interface SnackbarOptions {
  text: string;
  color?: string;
  timeout?: number;
  location?: string;
}

export function useSnackbar() {
  const visible = ref(false);
  const text = ref('');
  const color = ref('success');
  const timeout = ref(5000);
  const location = ref('bottom');

  const show = (options: SnackbarOptions) => {
    text.value = options.text;
    color.value = options.color || 'success';
    timeout.value = options.timeout || 5000;
    location.value = options.location || 'bottom';
    visible.value = true;
  };

  const success = (message: string, options: Partial<SnackbarOptions> = {}) => {
    show({
      text: message,
      color: 'success',
      ...options
    });
  };

  const error = (message: string, options: Partial<SnackbarOptions> = {}) => {
    show({
      text: message,
      color: 'error',
      ...options
    });
  };

  const info = (message: string, options: Partial<SnackbarOptions> = {}) => {
    show({
      text: message,
      color: 'info',
      ...options
    });
  };

  const warning = (message: string, options: Partial<SnackbarOptions> = {}) => {
    show({
      text: message,
      color: 'warning',
      ...options
    });
  };

  const hide = () => {
    visible.value = false;
  };

  return {
    visible,
    text,
    color,
    timeout,
    location,
    show,
    success,
    error,
    info,
    warning,
    hide
  };
}