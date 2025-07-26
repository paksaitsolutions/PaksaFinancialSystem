declare global {
  interface Window {
    // Add any global window properties here
  }
}

// Vue component types
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// Common types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T = any> {
  data: T[];
  total: number;
  page: number;
  limit: number;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
  search?: string;
}

// Module augmentation for missing libraries
declare module 'primevue/*' {
  const component: any;
  export default component;
}

declare module 'vue-toastification' {
  export const useToast: () => any;
  export const POSITION: any;
}

declare module 'date-fns' {
  export const format: (date: Date, format: string) => string;
  export const parseISO: (date: string) => Date;
  export const startOfDay: (date: Date) => Date;
  export const endOfDay: (date: Date) => Date;
  export const subDays: (date: Date, days: number) => Date;
  export const formatDistanceToNow: (date: Date) => string;
}

declare module 'chart.js' {
  export const Chart: any;
}

declare module 'echarts' {
  export const init: (element: HTMLElement) => any;
}

declare module 'jspdf' {
  export default class jsPDF {
    constructor(options?: any);
    text(text: string, x: number, y: number): void;
    save(filename: string): void;
  }
}

declare module 'html2canvas' {
  export default function html2canvas(element: HTMLElement): Promise<HTMLCanvasElement>;
}

declare module 'lodash' {
  export const debounce: (func: Function, wait: number) => Function;
  export const throttle: (func: Function, wait: number) => Function;
}

declare module 'lodash-es' {
  export const debounce: (func: Function, wait: number) => Function;
  export const throttle: (func: Function, wait: number) => Function;
}

declare module 'uuid' {
  export const v4: () => string;
}

declare module 'vitest' {
  export const describe: any;
  export const it: any;
  export const expect: any;
  export const vi: any;
  export const beforeEach: any;
}

declare module '@vue/test-utils' {
  export const mount: any;
  export const shallowMount: any;
}

export {};