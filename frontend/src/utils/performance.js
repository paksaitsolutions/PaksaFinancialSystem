// Performance optimization utilities for mobile
export class PerformanceOptimizer {
  constructor() {
    this.imageCache = new Map()
    this.componentCache = new Map()
    this.observers = new Map()
  }
  
  // Lazy load images
  lazyLoadImage(img, src) {
    if (this.imageCache.has(src)) {
      img.src = this.imageCache.get(src)
      return
    }
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const image = entry.target
          image.src = src
          this.imageCache.set(src, src)
          observer.unobserve(image)
        }
      })
    })
    
    observer.observe(img)
  }
  
  // Debounce function calls
  debounce(func, wait) {
    let timeout
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout)
        func(...args)
      }
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
    }
  }
  
  // Throttle function calls
  throttle(func, limit) {
    let inThrottle
    return function() {
      const args = arguments
      const context = this
      if (!inThrottle) {
        func.apply(context, args)
        inThrottle = true
        setTimeout(() => inThrottle = false, limit)
      }
    }
  }
  
  // Virtual scrolling for large lists
  createVirtualScroller(container, itemHeight, items, renderItem) {
    const containerHeight = container.clientHeight
    const visibleCount = Math.ceil(containerHeight / itemHeight) + 2
    let startIndex = 0
    
    const render = () => {
      const fragment = document.createDocumentFragment()
      const endIndex = Math.min(startIndex + visibleCount, items.length)
      
      container.innerHTML = ''
      container.style.height = `${items.length * itemHeight}px`
      container.style.paddingTop = `${startIndex * itemHeight}px`
      
      for (let i = startIndex; i < endIndex; i++) {
        const element = renderItem(items[i], i)
        fragment.appendChild(element)
      }
      
      container.appendChild(fragment)
    }
    
    const onScroll = this.throttle(() => {
      const scrollTop = container.scrollTop
      const newStartIndex = Math.floor(scrollTop / itemHeight)
      
      if (newStartIndex !== startIndex) {
        startIndex = newStartIndex
        render()
      }
    }, 16)
    
    container.addEventListener('scroll', onScroll)
    render()
    
    return {
      destroy: () => container.removeEventListener('scroll', onScroll)
    }
  }
  
  // Preload critical resources
  preloadResource(url, type = 'fetch') {
    return new Promise((resolve, reject) => {
      if (type === 'image') {
        const img = new Image()
        img.onload = () => resolve(img)
        img.onerror = reject
        img.src = url
      } else {
        fetch(url)
          .then(response => response.json())
          .then(resolve)
          .catch(reject)
      }
    })
  }
  
  // Memory management
  cleanupUnusedResources() {
    // Clear old cache entries
    const now = Date.now()
    const maxAge = 30 * 60 * 1000 // 30 minutes
    
    this.imageCache.forEach((value, key) => {
      if (now - value.timestamp > maxAge) {
        this.imageCache.delete(key)
      }
    })
    
    // Cleanup observers
    this.observers.forEach((observer, key) => {
      if (!document.querySelector(key)) {
        observer.disconnect()
        this.observers.delete(key)
      }
    })
  }
  
  // Touch optimization
  optimizeTouch(element) {
    element.style.touchAction = 'manipulation'
    element.style.webkitTouchCallout = 'none'
    element.style.webkitUserSelect = 'none'
    element.style.userSelect = 'none'
  }
  
  // Reduce animations on low-end devices
  reduceMotion() {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    return mediaQuery.matches || this.isLowEndDevice()
  }
  
  // Detect low-end devices
  isLowEndDevice() {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection
    const memory = navigator.deviceMemory
    const cores = navigator.hardwareConcurrency
    
    return (
      (connection && connection.effectiveType === 'slow-2g') ||
      (memory && memory < 4) ||
      (cores && cores < 4)
    )
  }
}

export const performanceOptimizer = new PerformanceOptimizer()

// Vue composable for performance optimization
export function usePerformance() {
  const { debounce, throttle, preloadResource, cleanupUnusedResources } = performanceOptimizer
  
  const optimizeForMobile = () => {
    // Disable hover effects on touch devices
    if ('ontouchstart' in window) {
      document.body.classList.add('touch-device')
    }
    
    // Optimize scrolling
    document.addEventListener('touchstart', () => {}, { passive: true })
    document.addEventListener('touchmove', () => {}, { passive: true })
  }
  
  const measurePerformance = (name, fn) => {
    return async (...args) => {
      const start = performance.now()
      const result = await fn(...args)
      const end = performance.now()
      console.log(`${name} took ${end - start} milliseconds`)
      return result
    }
  }
  
  return {
    debounce,
    throttle,
    preloadResource,
    cleanupUnusedResources,
    optimizeForMobile,
    measurePerformance,
    isLowEndDevice: performanceOptimizer.isLowEndDevice,
    reduceMotion: performanceOptimizer.reduceMotion
  }
}