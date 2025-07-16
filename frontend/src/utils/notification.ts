import { useToast, POSITION, type PluginOptions } from 'vue-toastification';

// Create toast instance
const toast = useToast();

// Define toast options type
type ToastType = 'success' | 'error' | 'warning' | 'info';

// Default toast options
const defaultOptions: PluginOptions = {
  position: POSITION.TOP_RIGHT,
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
  icon: true,
  rtl: false
};

/**
 * Show a toast notification with the specified type and options
 * @param message - The message to display
 * @param type - The type of toast (success, error, warning, info)
 * @param title - Optional title for the notification
 */
const showToast = (message: string, type: ToastType, title?: string): void => {
  // Add title if provided
  const toastMessage = title ? `${title}: ${message}` : message;
  
  // Show the toast with the specified type
  switch (type) {
    case 'success':
      toast.success(toastMessage);
      break;
    case 'error':
      toast.error(toastMessage);
      break;
    case 'warning':
      toast.warning(toastMessage);
      break;
    case 'info':
      toast.info(toastMessage);
      break;
    default:
      toast(toastMessage);
  }
};

// Apply default options when creating the toast instance
toast.updateDefaults(defaultOptions);

/**
 * Show a success notification
 * @param message - The message to display
 * @param title - Optional title for the notification
 */
export function showSuccess(message: string, title: string = 'Success'): void {
  showToast(message, 'success', title);
}

/**
 * Show an error notification
 * @param message - The error message to display
 * @param title - Optional title for the notification
 */
export function showError(message: string, title: string = 'Error'): void {
  showToast(message, 'error', title);
}

/**
 * Show a warning notification
 * @param message - The warning message to display
 * @param title - Optional title for the notification
 */
export function showWarning(message: string, title: string = 'Warning'): void {
  showToast(message, 'warning', title);
}

/**
 * Show an info notification
 * @param message - The info message to display
 * @param title - Optional title for the notification
 */
export function showInfo(message: string, title: string = 'Info'): void {
  showToast(message, 'info', title);
}

// Export the toast instance in case it's needed directly
export { toast };
