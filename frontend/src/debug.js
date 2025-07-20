// Debug script to help identify issues
const debug = {
  init() {
    console.log('Debug initialized');
    
    // Add global error handler
    window.addEventListener('error', (event) => {
      this.error('Global error caught:', event.error);
    });

    // Add unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      this.error('Unhandled promise rejection:', event.reason);
    });
    
    console.log('Debug module initialized');
  },
  
  log(...args) {
    console.log('[DEBUG]', ...args);
  },
  
  warn(...args) {
    console.warn('[WARN]', ...args);
  },
  
  error(...args) {
    console.error('[ERROR]', ...args);
  }
};

// Initialize debug module
debug.init();

// Make debug available globally for easier access in browser console
if (typeof window !== 'undefined') {
  window.$debug = debug;
}

export default debug;