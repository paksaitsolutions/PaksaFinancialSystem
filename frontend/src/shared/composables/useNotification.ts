import { useToast } from 'primevue/usetoast';
import { ToastServiceMethods } from 'primevue/toastservice';

type NotificationType = 'success' | 'info' | 'warn' | 'error';

interface NotificationOptions {
  title?: string;
  message: string;
  duration?: number;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center' | 'center';
  closable?: boolean;
}

export const useNotification = () => {
  const toast = useToast();

  const show = (type: NotificationType, options: NotificationOptions) => {
    const {
      title = type.charAt(0).toUpperCase() + type.slice(1),
      message,
      duration = 3000,
      position = 'top-right',
      closable = true
    } = options;

    toast.add({
      severity: type,
      summary: title,
      detail: message,
      life: duration,
      group: position,
      closable,
    });
  };

  const success = (options: Omit<NotificationOptions, 'type'>) => show('success', options);
  const info = (options: Omit<NotificationOptions, 'type'>) => show('info', options);
  const warn = (options: Omit<NotificationOptions, 'type'>) => show('warn', options);
  const error = (options: Omit<NotificationOptions, 'type'>) => show('error', options);

  return {
    show,
    success,
    info,
    warn,
    error,
  };
};

export type NotificationService = ReturnType<typeof useNotification>;
