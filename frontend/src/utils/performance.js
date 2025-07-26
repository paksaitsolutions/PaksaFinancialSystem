// Frontend performance optimization utilities

export class PerformanceOptimizer {
  constructor() {
    this.cache = new Map()
    this.cacheTimeout = 5 * 60 * 1000 // 5 minutes
    this.performanceMetrics = []
  }

  // Debounce function for search inputs
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

  // Throttle function for scroll events
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

  // Cache API responses
  cacheResponse(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  getCachedResponse(key) {
    const cached = this.cache.get(key)
    if (cached && (Date.now() - cached.timestamp) < this.cacheTimeout) {
      return cached.data
    }
    this.cache.delete(key)
    return null
  }

  // Lazy loading for components
  lazyLoad(importFunc) {
    return () => ({
      component: importFunc(),
      loading: () => import('@/components/common/LoadingSpinner.vue'),
      error: () => import('@/components/common/ErrorComponent.vue'),
      delay: 200,
      timeout: 10000
    })
  }

  // Virtual scrolling for large lists
  calculateVisibleItems(containerHeight, itemHeight, scrollTop, totalItems) {
    const visibleCount = Math.ceil(containerHeight / itemHeight)
    const startIndex = Math.floor(scrollTop / itemHeight)
    const endIndex = Math.min(startIndex + visibleCount + 5, totalItems) // 5 item buffer
    
    return {
      startIndex: Math.max(0, startIndex - 5), // 5 item buffer
      endIndex,
      visibleCount
    }
  }

  // Performance monitoring
  measurePerformance(name, fn) {
    const start = performance.now()
    const result = fn()
    const end = performance.now()
    
    this.performanceMetrics.push({
      name,
      duration: end - start,
      timestamp: Date.now()
    })
    
    return result
  }

  // Image optimization
  optimizeImage(src, width, height) {
    return `${src}?w=${width}&h=${height}&q=80&f=webp`
  }

  // Bundle splitting helper
  loadChunk(chunkName) {
    return import(
      /* webpackChunkName: "[request]" */
      `@/modules/${chunkName}`
    )
  }

  // Memory cleanup
  cleanup() {
    this.cache.clear()
    this.performanceMetrics = this.performanceMetrics.slice(-100) // Keep last 100 metrics
  }

  // Get performance report
  getPerformanceReport() {
    const metrics = this.performanceMetrics.slice(-50) // Last 50 operations
    const avgDuration = metrics.reduce((sum, m) => sum + m.duration, 0) / metrics.length
    
    return {
      cacheSize: this.cache.size,
      averageOperationTime: avgDuration || 0,
      totalOperations: this.performanceMetrics.length,
      recentMetrics: metrics
    }
  }
}

// Singleton instance
export const performanceOptimizer = new PerformanceOptimizer()

// Vue directive for lazy loading images
export const lazyImageDirective = {
  mounted(el, binding) {
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target
          img.src = binding.value
          img.classList.remove('lazy')
          imageObserver.unobserve(img)
        }
      })
    })
    
    el.classList.add('lazy')
    imageObserver.observe(el)
  }
}

// Mixin for component performance optimization
export const performanceMixin = {
  data() {
    return {
      isVisible: true,
      intersectionObserver: null
    }
  },
  
  mounted() {
    // Implement intersection observer for component visibility
    this.intersectionObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        this.isVisible = entry.isIntersecting
      })
    })
    
    if (this.$el) {
      this.intersectionObserver.observe(this.$el)
    }
  },
  
  beforeUnmount() {
    if (this.intersectionObserver) {
      this.intersectionObserver.disconnect()
    }
  },
  
  methods: {
    optimizedUpdate: performanceOptimizer.debounce(function(updateFn) {
      if (this.isVisible) {
        updateFn()
      }
    }, 100)
  }
}