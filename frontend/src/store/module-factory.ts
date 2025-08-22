import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Ref } from 'vue';
import type { ApiResponse, PaginatedResponse, PaginationParams } from '@/types/global';

/**
 * Options for creating a module store
 */
interface ModuleStoreOptions<T, F = any> {
  /**
   * Name of the store (should be unique)
   */
  name: string;
  
  /**
   * Initial state function
   */
  initialState: () => {
    items: T[];
    currentItem: T | null;
    loading: boolean;
    error: string | null;
    filters: F;
    pagination: {
      page: number;
      pageSize: number;
      total: number;
      totalPages: number;
    };
  };
  
  /**
   * API service for CRUD operations
   */
  apiService: {
    fetchAll: (params?: any) => Promise<PaginatedResponse<T> | T[]>;
    fetchById?: (id: string | number) => Promise<T>;
    create?: (data: Partial<T>) => Promise<T>;
    update?: (id: string | number, data: Partial<T>) => Promise<T>;
    delete?: (id: string | number) => Promise<void>;
    [key: string]: any;
  };
  
  /**
   * Default pagination parameters
   */
  defaultPagination?: Partial<PaginationParams>;
  
  /**
   * Default filters
   */
  defaultFilters?: F;
  
  /**
   * Whether to persist the store state
   */
  persist?: boolean | string[];
}

/**
 * Create a standardized module store with CRUD operations
 */
export function createModuleStore<T extends { id?: string | number }, F = any>({
  name,
  initialState,
  apiService,
  defaultPagination = { page: 1, pageSize: 10 },
  defaultFilters = {} as F,
  persist = false,
}: ModuleStoreOptions<T, F>) {
  return defineStore(name, () => {
    // State
    const items = ref<T[]>(initialState().items) as Ref<T[]>;
    const currentItem = ref<T | null>(initialState().currentItem) as Ref<T | null>;
    const loading = ref(initialState().loading);
    const error = ref<string | null>(initialState().error);
    const filters = ref<F>({ ...defaultFilters, ...initialState().filters }) as Ref<F>;
    const pagination = ref({
      page: defaultPagination.page || 1,
      pageSize: defaultPagination.pageSize || 10,
      total: 0,
      totalPages: 0,
    });

    // Getters
    const isEmpty = computed(() => items.value.length === 0);
    const hasItems = computed(() => items.value.length > 0);
    const isLoading = computed(() => loading.value);
    const currentError = computed(() => error.value);
    const currentFilters = computed(() => filters.value);
    const currentPagination = computed(() => ({
      page: pagination.value.page,
      pageSize: pagination.value.pageSize,
      total: pagination.value.total,
      totalPages: pagination.value.totalPages,
    }));

    // Actions
    const setLoading = (value: boolean) => {
      loading.value = value;
    };

    const setError = (err: string | null) => {
      error.value = err;
    };

    const setItems = (newItems: T[]) => {
      items.value = newItems;
    };

    const setCurrentItem = (item: T | null) => {
      currentItem.value = item;
    };

    const setFilters = (newFilters: Partial<F>) => {
      filters.value = { ...filters.value, ...newFilters };
    };

    const setPagination = (newPagination: Partial<typeof pagination.value>) => {
      pagination.value = { ...pagination.value, ...newPagination };
    };

    const resetFilters = () => {
      filters.value = { ...defaultFilters } as F;
    };

    const resetPagination = () => {
      pagination.value = {
        page: defaultPagination.page || 1,
        pageSize: defaultPagination.pageSize || 10,
        total: 0,
        totalPages: 0,
      };
    };

    // CRUD Operations
    const fetchAll = async (params: any = {}) => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await apiService.fetchAll({
          ...params,
          ...filters.value,
          page: pagination.value.page,
          pageSize: pagination.value.pageSize,
        });

        // Handle paginated response
        if ('items' in response && 'total' in response) {
          const { items: responseItems, total, page, pageSize, totalPages } = response as PaginatedResponse<T>;
          setItems(responseItems);
          setPagination({
            total,
            page: page || pagination.value.page,
            pageSize: pageSize || pagination.value.pageSize,
            totalPages: totalPages || Math.ceil(total / (pageSize || pagination.value.pageSize)),
          });
        } else {
          // Handle non-paginated response
          setItems(response as T[]);
          setPagination({
            total: (response as T[]).length,
            page: 1,
            pageSize: (response as T[]).length,
            totalPages: 1,
          });
        }

        return response;
      } catch (err: any) {
        const errorMessage = err.response?.data?.message || err.message || 'Failed to fetch items';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    };

    const fetchById = async (id: string | number) => {
      if (!apiService.fetchById) {
        throw new Error('fetchById is not implemented in the API service');
      }

      try {
        setLoading(true);
        setError(null);
        
        const item = await apiService.fetchById(id);
        setCurrentItem(item);
        return item;
      } catch (err: any) {
        const errorMessage = err.response?.data?.message || err.message || 'Failed to fetch item';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    };

    const create = async (data: Partial<T>) => {
      if (!apiService.create) {
        throw new Error('create is not implemented in the API service');
      }

      try {
        setLoading(true);
        setError(null);
        
        const newItem = await apiService.create(data);
        
        // Add the new item to the items list if it's not paginated
        if (!('total' in items.value)) {
          setItems([...items.value, newItem]);
        }
        
        return newItem;
      } catch (err: any) {
        const errorMessage = err.response?.data?.message || err.message || 'Failed to create item';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    };

    const update = async (id: string | number, data: Partial<T>) => {
      if (!apiService.update) {
        throw new Error('update is not implemented in the API service');
      }

      try {
        setLoading(true);
        setError(null);
        
        const updatedItem = await apiService.update(id, data);
        
        // Update the item in the items list
        setItems(
          items.value.map((item) =>
            (item as any).id === id ? { ...item, ...updatedItem } : item
          )
        );
        
        // Update current item if it's the one being updated
        if (currentItem.value && (currentItem.value as any).id === id) {
          setCurrentItem({ ...currentItem.value, ...updatedItem });
        }
        
        return updatedItem;
      } catch (err: any) {
        const errorMessage = err.response?.data?.message || err.message || 'Failed to update item';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    };

    const remove = async (id: string | number) => {
      if (!apiService.delete) {
        throw new Error('delete is not implemented in the API service');
      }

      try {
        setLoading(true);
        setError(null);
        
        await apiService.delete(id);
        
        // Remove the item from the items list
        setItems(items.value.filter((item) => (item as any).id !== id));
        
        // Clear current item if it's the one being deleted
        if (currentItem.value && (currentItem.value as any).id === id) {
          setCurrentItem(null);
        }
      } catch (err: any) {
        const errorMessage = err.response?.data?.message || err.message || 'Failed to delete item';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    };

    // Reset store to initial state
    const $reset = () => {
      const initial = initialState();
      items.value = initial.items;
      currentItem.value = initial.currentItem;
      loading.value = initial.loading;
      error.value = initial.error;
      filters.value = { ...defaultFilters, ...initial.filters } as F;
      resetPagination();
    };

    return {
      // State
      items,
      currentItem,
      loading,
      error,
      filters,
      pagination,
      
      // Getters
      isEmpty,
      hasItems,
      isLoading,
      currentError,
      currentFilters,
      currentPagination,
      
      // Actions
      setLoading,
      setError,
      setItems,
      setCurrentItem,
      setFilters,
      setPagination,
      resetFilters,
      resetPagination,
      fetchAll,
      fetchById,
      create,
      update,
      remove,
      $reset,
    };
  }, {
    // Persist options
    persist: Array.isArray(persist)
      ? { paths: persist }
      : persist === true
      ? {}
      : false,
  });
}

/**
 * Type for the module store instance
 */
export type ModuleStore<T, F = any> = ReturnType<typeof createModuleStore<T, F>>;
