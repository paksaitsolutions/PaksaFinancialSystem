import { ref, type Ref } from 'vue'

export interface UnifiedNotification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: string
  duration?: number
  dismissible?: boolean
  actions?: Array<{
    label: string
    action: () => void
    style?: 'primary' | 'secondary'
  }>
}

const notifications: Ref<UnifiedNotification[]> = ref([])

export function useUnifiedNotifications() {
  const add = (notification: Omit<UnifiedNotification, 'id'>) => {
    const id = Date.now().toString() + Math.random().toString(36).substr(2, 9)
    const newNotification: UnifiedNotification = {
      id,
      dismissible: true,
      duration: 5000,
      ...notification
    }
    
    notifications.value.push(newNotification)
    
    if (newNotification.duration && newNotification.duration > 0) {
      setTimeout(() => {
        dismiss(id)
      }, newNotification.duration)
    }
    
    return id
  }

  const dismiss = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clear = () => {
    notifications.value = []
  }

  const success = (message: string, title?: string, options?: Partial<UnifiedNotification>) => {
    return add({ type: 'success', message, title, ...options })
  }

  const error = (message: string, title?: string, options?: Partial<UnifiedNotification>) => {
    return add({ 
      type: 'error', 
      message, 
      title, 
      duration: 0, // Errors don't auto-dismiss
      ...options 
    })
  }

  const warning = (message: string, title?: string, options?: Partial<UnifiedNotification>) => {
    return add({ type: 'warning', message, title, ...options })
  }

  const info = (message: string, title?: string, options?: Partial<UnifiedNotification>) => {
    return add({ type: 'info', message, title, ...options })
  }

  return {
    notifications,
    add,
    dismiss,
    clear,
    success,
    error,
    warning,
    info
  }
}