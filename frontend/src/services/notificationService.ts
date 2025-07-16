import { createApp, h, ref } from 'vue';
import Notification from '@/components/ui/Notification.vue';

type NotificationType = 'success' | 'error' | 'info' | 'warning';
type NotificationPosition = 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';

interface NotificationOptions {
  title?: string;
  message: string;
  type?: NotificationType;
  position?: NotificationPosition;
  timeout?: number;
  dismissible?: boolean;
  icon?: string;
}

const defaultOptions: Partial<NotificationOptions> = {
  type: 'info',
  position: 'top-right',
  timeout: 5000,
  dismissible: true,
};

const notifications = ref<{ id: number; options: NotificationOptions }[]>([]);
let notificationId = 0;

// Create a container for notifications
const createNotificationContainer = () => {
  const container = document.createElement('div');
  container.className = 'notification-container';
  document.body.appendChild(container);
  return container;
};

// Show a notification
const show = (options: string | NotificationOptions) => {
  // If options is a string, treat it as the message
  const notificationOptions: NotificationOptions = typeof options === 'string' 
    ? { message: options }
    : { ...options };

  // Apply default options
  const finalOptions = { ...defaultOptions, ...notificationOptions };
  
  // Generate a unique ID for the notification
  const id = ++notificationId;
  
  // Add to the notifications array
  notifications.value.push({ id, options: finalOptions });
  
  // Create a container if it doesn't exist
  let container = document.querySelector('.notification-container');
  if (!container) {
    container = createNotificationContainer();
  }
  
  // Create a mount point for this notification
  const mountPoint = document.createElement('div');
  container.appendChild(mountPoint);
  
  // Create a new Vue app for this notification
  const app = createApp({
    setup() {
      const isVisible = ref(true);
      
      const dismiss = () => {
        isVisible.value = false;
        // Remove from DOM after animation
        setTimeout(() => {
          const index = notifications.value.findIndex(n => n.id === id);
          if (index !== -1) {
            notifications.value.splice(index, 1);
          }
          app.unmount();
          container?.removeChild(mountPoint);
        }, 300);
      };
      
      // Auto-dismiss if timeout is set
      if (finalOptions.timeout && finalOptions.timeout > 0) {
        setTimeout(dismiss, finalOptions.timeout);
      }
      
      return {
        isVisible,
        dismiss,
      };
    },
    render() {
      return h(Notification, {
        ...finalOptions,
        modelValue: this.isVisible,
        'onUpdate:modelValue': (val: boolean) => {
          if (!val) this.dismiss();
        },
        onDismissed: this.dismiss,
      });
    },
  });
  
  // Mount the notification
  app.mount(mountPoint);
  
  // Return a function to dismiss the notification
  return () => {
    const notification = document.querySelector(`[data-notification-id="${id}"]`);
    if (notification) {
      // Trigger the dismiss animation
      notification.dispatchEvent(new CustomEvent('dismiss'));
    }
  };
};

// Helper methods for different notification types
const success = (message: string, options: Omit<NotificationOptions, 'message' | 'type'> = {}) => {
  return show({ ...options, message, type: 'success' });
};

const error = (message: string, options: Omit<NotificationOptions, 'message' | 'type'> = {}) => {
  return show({ ...options, message, type: 'error' });
};

const info = (message: string, options: Omit<NotificationOptions, 'message' | 'type'> = {}) => {
  return show({ ...options, message, type: 'info' });
};

const warning = (message: string, options: Omit<NotificationOptions, 'message' | 'type'> = {}) => {
  return show({ ...options, message, type: 'warning' });
};

// Export the notification service
export const notificationService = {
  show,
  success,
  error,
  info,
  warning,
  notifications,
};

// Plugin installation
const install = (app: any) => {
  // Add global properties
  app.config.globalProperties.$notify = notificationService;
  
  // Provide the notification service
  app.provide('notification', notificationService);
};

export default {
  install,
  ...notificationService,
};

// Add TypeScript support for global properties
declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $notify: typeof notificationService;
  }
}
