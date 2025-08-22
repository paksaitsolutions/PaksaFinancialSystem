import { ref } from 'vue'

interface ToastMessage {
  id: string
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
  duration?: number
}

const messages = ref<ToastMessage[]>([])

export const useToast = () => {
  const show = (message: string, type: ToastMessage['type'] = 'info', duration = 3000) => {
    const id = Date.now().toString()
    const toast: ToastMessage = { id, message, type, duration }
    
    messages.value.push(toast)
    
    if (duration > 0) {
      setTimeout(() => {
        remove(id)
      }, duration)
    }
    
    return id
  }

  const remove = (id: string) => {
    const index = messages.value.findIndex(m => m.id === id)
    if (index > -1) {
      messages.value.splice(index, 1)
    }
  }

  const success = (message: string, duration?: number) => show(message, 'success', duration)
  const error = (message: string, duration?: number) => show(message, 'error', duration)
  const warning = (message: string, duration?: number) => show(message, 'warning', duration)
  const info = (message: string, duration?: number) => show(message, 'info', duration)

  return {
    messages,
    show,
    remove,
    success,
    error,
    warning,
    info
  }
}