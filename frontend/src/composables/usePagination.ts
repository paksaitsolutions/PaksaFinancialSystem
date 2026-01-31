/**
 * Vue composable for handling paginated API data with standardized response format
 */
import { ref, computed, watch } from 'vue'
import { apiClient } from '@/utils/apiClient'
import type { PaginatedResponse, PaginationParams, PaginationMeta } from '@/types/api'

export interface UsePaginationOptions {
  initialPage?: number
  initialPageSize?: number
  initialSortBy?: string
  initialSortOrder?: 'asc' | 'desc'
  autoLoad?: boolean
}

export function usePagination<T = any>(
  endpoint: string,
  options: UsePaginationOptions = {}
) {
  const {
    initialPage = 1,
    initialPageSize = 20,
    initialSortBy,
    initialSortOrder = 'asc',
    autoLoad = true
  } = options

  // Reactive state
  const data = ref<T[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Pagination state
  const currentPage = ref(initialPage)
  const pageSize = ref(initialPageSize)
  const sortBy = ref(initialSortBy)
  const sortOrder = ref<'asc' | 'desc'>(initialSortOrder)
  
  // Pagination metadata
  const pagination = ref<PaginationMeta>({
    total: 0,
    page: 1,
    page_size: 20,
    pages: 0,
    has_next: false,
    has_prev: false
  })

  // Computed properties
  const totalPages = computed(() => pagination.value.pages)
  const hasNextPage = computed(() => pagination.value.has_next)
  const hasPrevPage = computed(() => pagination.value.has_prev)
  const totalItems = computed(() => pagination.value.total)
  
  const startItem = computed(() => 
    (currentPage.value - 1) * pageSize.value + 1
  )
  
  const endItem = computed(() => 
    Math.min(currentPage.value * pageSize.value, totalItems.value)
  )

  // Load data function
  const loadData = async (params?: Partial<PaginationParams>) => {
    loading.value = true
    error.value = null

    try {
      const paginationParams: PaginationParams = {
        page: params?.page ?? currentPage.value,
        page_size: params?.page_size ?? pageSize.value,
        sort_by: params?.sort_by ?? sortBy.value,
        sort_order: params?.sort_order ?? sortOrder.value
      }

      const response = await apiClient.getPaginated<T>(endpoint, paginationParams)
      const result = apiClient.extractPaginatedData(response)
      
      data.value = result.data
      pagination.value = result.pagination
      
      // Update current state
      currentPage.value = result.pagination.page
      pageSize.value = result.pagination.page_size
      
    } catch (err: any) {
      error.value = err.message || 'Failed to load data'
      console.error('Pagination error:', err)
    } finally {
      loading.value = false
    }
  }

  // Navigation functions
  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
      loadData({ page })
    }
  }

  const nextPage = () => {
    if (hasNextPage.value) {
      goToPage(currentPage.value + 1)
    }
  }

  const prevPage = () => {
    if (hasPrevPage.value) {
      goToPage(currentPage.value - 1)
    }
  }

  const firstPage = () => {
    goToPage(1)
  }

  const lastPage = () => {
    goToPage(totalPages.value)
  }

  // Change page size
  const changePageSize = (newSize: number) => {
    pageSize.value = newSize
    currentPage.value = 1 // Reset to first page
    loadData({ page: 1, page_size: newSize })
  }

  // Change sorting
  const changeSort = (field: string, order?: 'asc' | 'desc') => {
    sortBy.value = field
    sortOrder.value = order || (sortBy.value === field && sortOrder.value === 'asc' ? 'desc' : 'asc')
    currentPage.value = 1 // Reset to first page
    loadData({ page: 1, sort_by: field, sort_order: sortOrder.value })
  }

  // Refresh data
  const refresh = () => {
    loadData()
  }

  // Reset pagination
  const reset = () => {
    currentPage.value = initialPage
    pageSize.value = initialPageSize
    sortBy.value = initialSortBy
    sortOrder.value = initialSortOrder
    loadData()
  }

  // Auto-load data on mount
  if (autoLoad) {
    loadData()
  }

  return {
    // Data
    data,
    loading,
    error,
    
    // Pagination state
    currentPage,
    pageSize,
    sortBy,
    sortOrder,
    pagination,
    
    // Computed
    totalPages,
    hasNextPage,
    hasPrevPage,
    totalItems,
    startItem,
    endItem,
    
    // Methods
    loadData,
    goToPage,
    nextPage,
    prevPage,
    firstPage,
    lastPage,
    changePageSize,
    changeSort,
    refresh,
    reset
  }
}