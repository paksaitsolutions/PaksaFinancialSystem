import { performanceOptimizer } from '@/utils/performance'
import { offlineManager } from '@/utils/offline'

export default {
  install(app) {
    // Global mobile utilities
    app.config.globalProperties.$mobile = {
      isMobile: () => window.innerWidth < 600,
      isTablet: () => window.innerWidth >= 600 && window.innerWidth < 960,
      isTouch: () => 'ontouchstart' in window
    }
    
    // Performance optimization
    app.config.globalProperties.$performance = performanceOptimizer
    
    // Offline support
    app.config.globalProperties.$offline = offlineManager
    
    // Mobile-specific directives
    app.directive('touch', {
      mounted(el, binding) {
        let startX, startY, startTime
        
        const handleTouchStart = (e) => {
          startX = e.touches[0].clientX
          startY = e.touches[0].clientY
          startTime = Date.now()
        }
        
        const handleTouchEnd = (e) => {
          const endX = e.changedTouches[0].clientX
          const endY = e.changedTouches[0].clientY
          const endTime = Date.now()
          
          const diffX = startX - endX
          const diffY = startY - endY
          const diffTime = endTime - startTime
          
          // Swipe detection
          if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50 && diffTime < 300) {
            if (diffX > 0) {
              binding.value?.onSwipeLeft?.()
            } else {
              binding.value?.onSwipeRight?.()
            }
          }
          
          // Tap detection
          if (Math.abs(diffX) < 10 && Math.abs(diffY) < 10 && diffTime < 300) {
            binding.value?.onTap?.()
          }
          
          // Long press detection
          if (diffTime > 500) {
            binding.value?.onLongPress?.()
          }
        }
        
        el.addEventListener('touchstart', handleTouchStart, { passive: true })
        el.addEventListener('touchend', handleTouchEnd, { passive: true })
        
        el._touchHandlers = { handleTouchStart, handleTouchEnd }
      },
      
      unmounted(el) {
        if (el._touchHandlers) {
          el.removeEventListener('touchstart', el._touchHandlers.handleTouchStart)
          el.removeEventListener('touchend', el._touchHandlers.handleTouchEnd)
        }
      }
    })
    
    // Lazy loading directive
    app.directive('lazy', {
      mounted(el, binding) {
        const observer = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              if (el.tagName === 'IMG') {
                el.src = binding.value
              } else {
                binding.value?.()
              }
              observer.unobserve(el)
            }
          })
        })
        
        observer.observe(el)
        el._observer = observer
      },
      
      unmounted(el) {
        if (el._observer) {
          el._observer.disconnect()
        }
      }
    })
    
    // Initialize mobile optimizations
    if (typeof window !== 'undefined') {
      // Optimize for mobile
      performanceOptimizer.optimizeForMobile?.()
      
      // Add touch device class
      if ('ontouchstart' in window) {
        document.body.classList.add('touch-device')
      }
      
      // Prevent zoom on input focus (iOS)
      const viewport = document.querySelector('meta[name=viewport]')
      if (viewport) {
        viewport.setAttribute('content', 
          'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
        )
      }
      
      // Handle orientation change
      window.addEventListener('orientationchange', () => {
        setTimeout(() => {
          window.scrollTo(0, 0)
        }, 100)
      })
    }
  }
}