/**
 * Tenant-aware logging utility
 */
class TenantLogger {
  constructor() {
    this.logs = []
    this.maxLogs = 1000
    this.currentTenant = null
  }
  
  setTenant(tenantId) {
    this.currentTenant = tenantId
  }
  
  log(level, message, data = {}) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      tenantId: this.currentTenant,
      data,
      url: window.location.href,
      userAgent: navigator.userAgent
    }
    
    // Add to local storage
    this.logs.push(logEntry)
    if (this.logs.length > this.maxLogs) {
      this.logs.shift()
    }
    
    // Console output with tenant context
    const tenantPrefix = this.currentTenant ? `[Tenant: ${this.currentTenant}]` : '[No Tenant]'
    console[level](`${tenantPrefix} ${message}`, data)
    
    // Send to backend if configured
    this.sendToBackend(logEntry)
  }
  
  info(message, data) {
    this.log('info', message, data)
  }
  
  warn(message, data) {
    this.log('warn', message, data)
  }
  
  error(message, data) {
    this.log('error', message, data)
  }
  
  debug(message, data) {
    this.log('debug', message, data)
  }
  
  async sendToBackend(logEntry) {
    try {
      // Only send error and warn logs to backend
      if (['error', 'warn'].includes(logEntry.level)) {
        await fetch('/api/v1/logging/client-logs', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Tenant-ID': this.currentTenant
          },
          body: JSON.stringify(logEntry)
        })
      }
    } catch (error) {
      console.error('Failed to send log to backend:', error)
    }
  }
  
  getTenantLogs(tenantId = null) {
    const targetTenant = tenantId || this.currentTenant
    return this.logs.filter(log => log.tenantId === targetTenant)
  }
  
  clearLogs(tenantId = null) {
    if (tenantId) {
      this.logs = this.logs.filter(log => log.tenantId !== tenantId)
    } else {
      this.logs = []
    }
  }
  
  exportLogs(tenantId = null) {
    const logs = this.getTenantLogs(tenantId)
    const dataStr = JSON.stringify(logs, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `tenant-logs-${tenantId || 'all'}-${Date.now()}.json`
    link.click()
    
    URL.revokeObjectURL(url)
  }
}

export const tenantLogger = new TenantLogger()

// Vue plugin
export default {
  install(app) {
    app.config.globalProperties.$tenantLogger = tenantLogger
    app.provide('tenantLogger', tenantLogger)
  }
}

// Composable
export function useTenantLogger() {
  return {
    log: tenantLogger.log.bind(tenantLogger),
    info: tenantLogger.info.bind(tenantLogger),
    warn: tenantLogger.warn.bind(tenantLogger),
    error: tenantLogger.error.bind(tenantLogger),
    debug: tenantLogger.debug.bind(tenantLogger),
    setTenant: tenantLogger.setTenant.bind(tenantLogger),
    getTenantLogs: tenantLogger.getTenantLogs.bind(tenantLogger),
    clearLogs: tenantLogger.clearLogs.bind(tenantLogger),
    exportLogs: tenantLogger.exportLogs.bind(tenantLogger)
  }
}