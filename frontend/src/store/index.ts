import { createPinia, defineStore } from 'pinia';
import { markRaw } from 'vue';
import type { App } from 'vue';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';

/**
 * Pinia instance
 */
const pinia = createPinia();

/**
 * Pinia plugin for handling store initialization
 */
pinia.use(({ store }) => {
  // Add a reactive property to track if the store is initialized
  store.$state = markRaw({
    ...store.$state,
    _isInitialized: false,
  });

  // Add initialization method
  store.initialize = async function (force = false) {
    if (!force && this._isInitialized) return;
    
    if (typeof this.$_initialize === 'function') {
      await this.$_initialize();
    }
    
    this._isInitialized = true;
  };

  // Add reset method
  store.reset = function () {
    if (typeof this.$_reset === 'function') {
      this.$_reset();
    } else {
      this.$reset();
    }
    this._isInitialized = false;
  };
});

// Add persistence plugin
pinia.use(piniaPluginPersistedstate);

/**
 * Initialize Pinia in the Vue app
 */
export function setupStore(app: App) {
  app.use(pinia);
  return pinia;
}

/**
 * Base store with common functionality
 */
export const useBaseStore = defineStore('base', {
  state: () => ({
    loading: false,
    error: null as string | null,
    _isInitialized: false,
  }),
  
  actions: {
    /**
     * Set loading state
     */
    setLoading(loading: boolean) {
      this.loading = loading;
    },
    
    /**
     * Set error
     */
    setError(error: string | null) {
      this.error = error;
    },
    
    /**
     * Reset store state
     */
    $_reset() {
      this.$reset();
    },
  },
});

/**
 * Create a namespaced store with common functionality
 */
export function createNamespacedStore<Id extends string, S, G, A>(
  id: Id,
  options: {
    state: () => S;
    getters?: G;
    actions: A;
  }
) {
  return defineStore(id, {
    state: options.state,
    
    getters: {
      ...(options.getters || {}),
      
      /**
       * Check if the store is loading
       */
      isLoading(): boolean {
        return (this as any).loading === true;
      },
      
      /**
       * Get the current error message
       */
      errorMessage(): string | null {
        return (this as any).error;
      },
      
      /**
       * Check if the store has been initialized
       */
      isInitialized(): boolean {
        return (this as any)._isInitialized === true;
      },
    },
    
    actions: {
      ...options.actions,
      
      /**
       * Set loading state
       */
      setLoading(loading: boolean) {
        (this as any).loading = loading;
      },
      
      /**
       * Set error
       */
      setError(error: string | null) {
        (this as any).error = error;
      },
      
      /**
       * Reset store state
       */
      $_reset() {
        this.$reset();
      },
    },
  });
}

export default pinia;
