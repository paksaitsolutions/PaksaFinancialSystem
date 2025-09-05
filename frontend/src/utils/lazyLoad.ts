import { defineAsyncComponent, AsyncComponentLoader } from 'vue'

// Lazy load component with loading and error states
export function lazyLoad(loader: AsyncComponentLoader) {
  return defineAsyncComponent({
    loader,
    loadingComponent: {
      template: `
        <div class="flex justify-content-center align-items-center" style="height: 200px;">
          <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
        </div>
      `
    },
    errorComponent: {
      template: `
        <div class="text-center p-4">
          <i class="pi pi-exclamation-triangle text-red-500" style="font-size: 2rem"></i>
          <p class="mt-2">Failed to load component</p>
        </div>
      `
    },
    delay: 200,
    timeout: 10000
  })
}

// Preload components
export function preloadComponent(loader: AsyncComponentLoader) {
  return loader()
}

// Preload multiple components
export function preloadComponents(loaders: AsyncComponentLoader[]) {
  return Promise.all(loaders.map(loader => loader().catch(() => null)))
}