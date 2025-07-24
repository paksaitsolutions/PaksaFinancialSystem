import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'

export interface KeyboardShortcut {
  key: string
  ctrl?: boolean
  alt?: boolean
  shift?: boolean
  action: () => void
  description: string
}

export function useKeyboardShortcuts() {
  const router = useRouter()
  const themeStore = useThemeStore()
  
  const shortcuts: KeyboardShortcut[] = [
    // Navigation shortcuts
    { key: 'h', ctrl: true, action: () => router.push('/'), description: 'Go to Dashboard' },
    { key: 'd', ctrl: true, action: () => router.push('/'), description: 'Go to Dashboard' },
    { key: 'p', ctrl: true, action: () => router.push('/payroll'), description: 'Go to Payroll' },
    { key: 'a', ctrl: true, action: () => router.push('/accounts-payable'), description: 'Go to Accounts Payable' },
    { key: 'r', ctrl: true, action: () => router.push('/accounts-receivable'), description: 'Go to Accounts Receivable' },
    { key: 'g', ctrl: true, action: () => router.push('/general-ledger'), description: 'Go to General Ledger' },
    { key: 'o', ctrl: true, action: () => router.push('/reports'), description: 'Go to Reports' },
    
    // Theme shortcuts
    { key: 't', ctrl: true, action: () => themeStore.toggleTheme(), description: 'Toggle Theme' },
    
    // Search shortcut
    { key: 'k', ctrl: true, action: () => focusSearch(), description: 'Focus Search' },
    
    // Quick actions
    { key: 'n', ctrl: true, shift: true, action: () => createNew(), description: 'Create New Entry' },
    { key: 's', ctrl: true, action: (e: Event) => { e.preventDefault(); saveForm() }, description: 'Save Form' },
    { key: 'Escape', action: () => closeModal(), description: 'Close Modal/Dialog' }
  ]

  const handleKeydown = (event: KeyboardEvent) => {
    const shortcut = shortcuts.find(s => 
      s.key.toLowerCase() === event.key.toLowerCase() &&
      !!s.ctrl === event.ctrlKey &&
      !!s.alt === event.altKey &&
      !!s.shift === event.shiftKey
    )

    if (shortcut) {
      event.preventDefault()
      shortcut.action(event)
    }
  }

  const focusSearch = () => {
    const searchInput = document.querySelector('input[placeholder*="Search"], input[type="search"]') as HTMLInputElement
    if (searchInput) {
      searchInput.focus()
    }
  }

  const createNew = () => {
    const createButton = document.querySelector('[data-shortcut="create"], button:contains("New"), button:contains("Add"), button:contains("Create")') as HTMLButtonElement
    if (createButton) {
      createButton.click()
    }
  }

  const saveForm = () => {
    const saveButton = document.querySelector('[data-shortcut="save"], button:contains("Save"), button[type="submit"]') as HTMLButtonElement
    if (saveButton && !saveButton.disabled) {
      saveButton.click()
    }
  }

  const closeModal = () => {
    const closeButton = document.querySelector('[data-shortcut="close"], .v-dialog .v-btn:contains("Cancel"), .v-dialog .v-btn:contains("Close")') as HTMLButtonElement
    if (closeButton) {
      closeButton.click()
    }
  }

  onMounted(() => {
    document.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown)
  })

  return {
    shortcuts
  }
}