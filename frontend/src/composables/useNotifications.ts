import { ref } from 'vue';

export interface Notification {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  timeout?: number;
}

const notifications = ref<Notification[]>([]);
let nextId = 1;

export function useNotifications() {
  const showNotification = (
    message: string,
    type: 'success' | 'error' | 'info' | 'warning' = 'info',
    timeout = 5000
  ) => {
    const id = nextId++;
    const notification = { id, message, type, timeout };
    
    notifications.value.push(notification);
    
    if (timeout > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, timeout);
    }
    
    return id;
  };
  
  const removeNotification = (id: number) => {
    const index = notifications.value.findIndex(n => n.id === id);
    if (index !== -1) {
      notifications.value.splice(index, 1);
    }
  };
  
  return {
    notifications,
    showNotification,
    removeNotification,
    success: (message: string, timeout?: number) => showNotification(message, 'success', timeout),
    error: (message: string, timeout?: number) => showNotification(message, 'error', timeout),
    info: (message: string, timeout?: number) => showNotification(message, 'info', timeout),
    warning: (message: string, timeout?: number) => showNotification(message, 'warning', timeout)
  };
}
