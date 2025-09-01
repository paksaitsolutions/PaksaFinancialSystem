import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'

export interface SnackbarOptions {
  severity?: 'success' | 'info' | 'warn' | 'error'
  summary?: string
  detail?: string
  life?: number
}

export function useSnackbar() {
  const toast = useToast()
  const visible = ref(false)
  const message = ref('')
  const severity = ref<'success' | 'info' | 'warn' | 'error'>('info')

  const show = (text: string, options: SnackbarOptions = {}) => {
    const {
      severity: sev = 'info',
      summary = '',
      detail = text,
      life = 3000
    } = options

    toast.add({
      severity: sev,
      summary: summary || getSummaryBySeverity(sev),
      detail,
      life
    })

    // Also update local state for compatibility
    message.value = text
    severity.value = sev
    visible.value = true

    // Auto hide after life duration
    setTimeout(() => {
      visible.value = false
    }, life)
  }

  const showSuccess = (text: string, life = 3000) => {
    show(text, { severity: 'success', life })
  }

  const showError = (text: string, life = 5000) => {
    show(text, { severity: 'error', life })
  }

  const showWarning = (text: string, life = 4000) => {
    show(text, { severity: 'warn', life })
  }

  const showInfo = (text: string, life = 3000) => {
    show(text, { severity: 'info', life })
  }

  const hide = () => {
    visible.value = false
  }

  const getSummaryBySeverity = (severity: string): string => {
    switch (severity) {
      case 'success': return 'Success'
      case 'error': return 'Error'
      case 'warn': return 'Warning'
      case 'info': return 'Information'
      default: return 'Notification'
    }
  }

  return {
    visible,
    message,
    severity,
    show,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    hide
  }
}

// Export default for backward compatibility
export default useSnackbar