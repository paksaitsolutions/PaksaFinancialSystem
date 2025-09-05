import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface BreadcrumbItem {
  label: string
  route?: string
  icon?: string
  command?: () => void
}

export const useBreadcrumbStore = defineStore('breadcrumb', () => {
  const customBreadcrumbs = ref<BreadcrumbItem[]>([])

  const setBreadcrumbs = (breadcrumbs: BreadcrumbItem[]) => {
    customBreadcrumbs.value = breadcrumbs
  }

  const clearBreadcrumbs = () => {
    customBreadcrumbs.value = []
  }

  const addBreadcrumb = (breadcrumb: BreadcrumbItem) => {
    customBreadcrumbs.value.push(breadcrumb)
  }

  return {
    customBreadcrumbs,
    setBreadcrumbs,
    clearBreadcrumbs,
    addBreadcrumb
  }
})