/**
 * Performance monitoring utilities
 */

export class PerformanceMonitor {
  private static marks: Map<string, number> = new Map();

  /**
   * Start performance measurement
   */
  static start(label: string) {
    this.marks.set(label, performance.now());
  }

  /**
   * End performance measurement and log
   */
  static end(label: string) {
    const startTime = this.marks.get(label);
    if (startTime) {
      const duration = performance.now() - startTime;
      console.log(`[Performance] ${label}: ${duration.toFixed(2)}ms`);
      this.marks.delete(label);
      return duration;
    }
    return 0;
  }

  /**
   * Measure component render time
   */
  static measureRender(componentName: string, callback: () => void) {
    this.start(`render-${componentName}`);
    callback();
    requestAnimationFrame(() => {
      this.end(`render-${componentName}`);
    });
  }

  /**
   * Get page load metrics
   */
  static getPageMetrics() {
    if (!window.performance) return null;

    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    
    return {
      dns: navigation.domainLookupEnd - navigation.domainLookupStart,
      tcp: navigation.connectEnd - navigation.connectStart,
      ttfb: navigation.responseStart - navigation.requestStart,
      download: navigation.responseEnd - navigation.responseStart,
      domInteractive: navigation.domInteractive - navigation.fetchStart,
      domComplete: navigation.domComplete - navigation.fetchStart,
      loadComplete: navigation.loadEventEnd - navigation.fetchStart
    };
  }

  /**
   * Monitor bundle size
   */
  static logBundleSize() {
    if (!window.performance) return;

    const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
    const jsResources = resources.filter(r => r.name.endsWith('.js'));
    const cssResources = resources.filter(r => r.name.endsWith('.css'));

    const totalJS = jsResources.reduce((sum, r) => sum + r.transferSize, 0);
    const totalCSS = cssResources.reduce((sum, r) => sum + r.transferSize, 0);

    console.log('[Bundle Size]', {
      js: `${(totalJS / 1024).toFixed(2)} KB`,
      css: `${(totalCSS / 1024).toFixed(2)} KB`,
      total: `${((totalJS + totalCSS) / 1024).toFixed(2)} KB`
    });
  }
}

/**
 * Debounce function for performance
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * Throttle function for performance
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};
