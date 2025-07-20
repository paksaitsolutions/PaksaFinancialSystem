// Type definitions for PrimeVue components and modules
declare module 'primevue/usetoast' {
  import { Plugin } from 'vue';

  interface ToastMessageOptions {
    severity?: 'success' | 'info' | 'warn' | 'error';
    summary?: string;
    detail?: string;
    life?: number;
    group?: string;
    closable?: boolean;
    sticky?: boolean;
    position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center' | 'center';
    data?: any;
    contentStyleClass?: string;
    contentStyle?: any;
    style?: any;
    class?: string;
  }

  interface ToastServiceMethods {
    add(message: ToastMessageOptions): void;
    removeGroup(group: string): void;
    removeAllGroups(): void;
  }

  export function useToast(): ToastServiceMethods;
  export const ToastService: Plugin;
}

// Add type declarations for other PrimeVue components as needed
declare module 'primevue/datatable' {
  import { Component } from 'vue';
  const component: Component;
  export default component;
}

declare module 'primevue/column' {
  import { Component } from 'vue';
  const component: Component;
  export default component;
}

declare module 'primevue/button' {
  import { Component } from 'vue';
  const component: Component;
  export default component;
}

declare module 'primevue/inputtext' {
  import { Component } from 'vue';
  const component: Component;
  export default component;
}

declare module 'primevue/dropdown' {
  import { Component } from 'vue';
  const component: Component;
  export default component;
}

declare module 'primevue/tag' {
  import { Component } from 'vue';
  const component: Component;
  export default component;
}
