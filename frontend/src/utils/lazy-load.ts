import { defineAsyncComponent, Component } from 'vue';
import type { AsyncComponentLoader } from 'vue';

/**
 * Lazy load component with loading and error states
 */
export const lazyLoad = (
  loader: AsyncComponentLoader,
  loadingComponent?: Component,
  errorComponent?: Component,
  delay = 200,
  timeout = 30000
) => {
  return defineAsyncComponent({
    loader,
    loadingComponent,
    errorComponent,
    delay,
    timeout
  });
};

/**
 * Preload component for better UX
 */
export const preloadComponent = (loader: AsyncComponentLoader) => {
  return loader();
};

/**
 * Lazy load route component
 */
export const lazyLoadRoute = (path: string) => {
  return () => import(`../modules/${path}`);
};
