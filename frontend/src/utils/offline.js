class OfflineManager {
  constructor() {
    this.isOnline = navigator.onLine
    this.queue = []
    this.storage = localStorage
    this.init()
  }
  
  init() {
    window.addEventListener('online', () => {
      this.isOnline = true
      this.processQueue()
    })
    
    window.addEventListener('offline', () => {
      this.isOnline = false
    })
    
    this.loadQueue()
  }
  
  addToQueue(request) {
    this.queue.push({
      ...request,
      timestamp: Date.now(),
      id: Math.random().toString(36).substr(2, 9)
    })
    this.saveQueue()
  }
  
  async processQueue() {
    if (!this.isOnline || this.queue.length === 0) return
    
    const processedItems = []
    
    for (const item of this.queue) {
      try {
        await this.executeRequest(item)
        processedItems.push(item.id)
      } catch (error) {
        console.error('Failed to process queued request:', error)
      }
    }
    
    this.queue = this.queue.filter(item => !processedItems.includes(item.id))
    this.saveQueue()
  }
  
  async executeRequest(item) {
    const { method, url, data, headers } = item
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      body: data ? JSON.stringify(data) : undefined
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    
    return response.json()
  }
  
  saveQueue() {
    this.storage.setItem('offline_queue', JSON.stringify(this.queue))
  }
  
  loadQueue() {
    const saved = this.storage.getItem('offline_queue')
    if (saved) {
      this.queue = JSON.parse(saved)
    }
  }
  
  cacheData(key, data, ttl = 3600000) { // 1 hour default
    const item = {
      data,
      timestamp: Date.now(),
      ttl
    }
    this.storage.setItem(`cache_${key}`, JSON.stringify(item))
  }
  
  getCachedData(key) {
    const item = this.storage.getItem(`cache_${key}`)
    if (!item) return null
    
    const parsed = JSON.parse(item)
    const now = Date.now()
    
    if (now - parsed.timestamp > parsed.ttl) {
      this.storage.removeItem(`cache_${key}`)
      return null
    }
    
    return parsed.data
  }
  
  clearCache() {
    const keys = Object.keys(this.storage)
    keys.forEach(key => {
      if (key.startsWith('cache_')) {
        this.storage.removeItem(key)
      }
    })
  }
}

export const offlineManager = new OfflineManager()

export function useOffline() {
  const isOnline = () => offlineManager.isOnline
  
  const queueRequest = (method, url, data = null, headers = {}) => {
    if (!offlineManager.isOnline) {
      offlineManager.addToQueue({ method, url, data, headers })
      return Promise.resolve({ queued: true })
    }
    
    return offlineManager.executeRequest({ method, url, data, headers })
  }
  
  const cacheData = (key, data, ttl) => {
    offlineManager.cacheData(key, data, ttl)
  }
  
  const getCachedData = (key) => {
    return offlineManager.getCachedData(key)
  }
  
  return {
    isOnline,
    queueRequest,
    cacheData,
    getCachedData
  }
}