import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { BreadcrumbItem } from '@/composables/useBreadcrumbs'

export const useBreadcrumbStore = defineStore('breadcrumb', () => {
  const customBreadcrumbs = ref<BreadcrumbItem[]>([])

  const setCustomBreadcrumbs = (items: BreadcrumbItem[]) => {
    customBreadcrumbs.value = items
  }

  const clearCustomBreadcrumbs = () => {
    customBreadcrumbs.value = []
  }

  const addBreadcrumb = (item: BreadcrumbItem) => {
    customBreadcrumbs.value.push(item)
  }

  return {
    customBreadcrumbs,
    setCustomBreadcrumbs,
    clearCustomBreadcrumbs,
    addBreadcrumb
  }
})