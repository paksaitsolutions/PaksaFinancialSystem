import { ref, onMounted, onUnmounted } from 'vue'

export function useMobile() {
  const isMobile = ref(false)
  const isTablet = ref(false)
  const screenWidth = ref(0)
  
  const checkDevice = () => {
    screenWidth.value = window.innerWidth
    isMobile.value = window.innerWidth < 600
    isTablet.value = window.innerWidth >= 600 && window.innerWidth < 960
  }
  
  const handleResize = () => {
    checkDevice()
  }
  
  onMounted(() => {
    checkDevice()
    window.addEventListener('resize', handleResize)
  })
  
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })
  
  return {
    isMobile,
    isTablet,
    screenWidth
  }
}

export function useTouch() {
  const handleSwipe = (element, onSwipeLeft, onSwipeRight) => {
    let startX = 0
    let startY = 0
    
    const handleTouchStart = (e) => {
      startX = e.touches[0].clientX
      startY = e.touches[0].clientY
    }
    
    const handleTouchEnd = (e) => {
      const endX = e.changedTouches[0].clientX
      const endY = e.changedTouches[0].clientY
      const diffX = startX - endX
      const diffY = startY - endY
      
      if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
        if (diffX > 0 && onSwipeLeft) {
          onSwipeLeft()
        } else if (diffX < 0 && onSwipeRight) {
          onSwipeRight()
        }
      }
    }
    
    element.addEventListener('touchstart', handleTouchStart)
    element.addEventListener('touchend', handleTouchEnd)
    
    return () => {
      element.removeEventListener('touchstart', handleTouchStart)
      element.removeEventListener('touchend', handleTouchEnd)
    }
  }
  
  return { handleSwipe }
}