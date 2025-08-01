/**
 * Debug utility for logging and error handling
 */
interface DebugInterface {
  init(): void;
  log(...args: unknown[]): void;
  warn(...args: unknown[]): void;
  error(...args: unknown[]): void;
}

const debug: DebugInterface = {
  /**
   * Initialize debug handlers for global error and unhandled promise rejections
   */
  init(): void {
    console.log('Debug initialized');
    
    // Add global error handler
    window.addEventListener('error', (event: ErrorEvent) => {
      this.error('Global error caught:', event.error);
    });

    // Add unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event: PromiseRejectionEvent) => {
      this.error('Unhandled promise rejection:', event.reason);
    });
    
    console.log('Debug module initialized');
  },
  
  /**
   * Log debug information
   * @param args - Values to log
   */
  log(...args: unknown[]): void {
    console.log('[DEBUG]', ...args);
  },
  
  /**
   * Log warning messages
   * @param args - Warning messages to log
   */
  warn(...args: unknown[]): void {
    console.warn('[WARN]', ...args);
  },
  
  /**
   * Log error messages
   * @param args - Error messages to log
   */
  error(...args: unknown[]): void {
    console.error('[ERROR]', ...args);
  }
};

// Initialize debug module
debug.init();

// Extend Window interface to include $debug
declare global {
  interface Window {
    $debug: DebugInterface;
  }
}

// Make debug available globally for easier access in browser console
if (typeof window !== 'undefined') {
  window.$debug = debug;
}

// Make debug available globally for easier access in browser console
if (typeof window !== 'undefined') {
  window.$debug = debug;
}

export default debug;
