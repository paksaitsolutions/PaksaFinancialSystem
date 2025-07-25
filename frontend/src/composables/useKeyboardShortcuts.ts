import { onMounted, onUnmounted } from 'vue'

export function useKeyboardShortcuts() {
  const handleKeydown = (event: KeyboardEvent) => {
    // Ctrl + K for search
    if (event.ctrlKey && event.key === 'k') {
      event.preventDefault()
      console.log('Search shortcut triggered')
    }
    
    // Ctrl + / for shortcuts dialog
    if (event.ctrlKey && event.key === '/') {
      event.preventDefault()
      console.log('Shortcuts dialog triggered')
    }
  }

  onMounted(() => {
    document.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown)
  })
}