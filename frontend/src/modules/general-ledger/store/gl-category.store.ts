import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useNotification } from '@/shared/composables/useNotification';
import type { GlCategory } from '../types/gl-category';

export const useGlCategoryStore = defineStore('glCategory', () => {
  const notification = useNotification();
  
  // State
  const categories = ref<GlCategory[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  
  // Getters
  const activeCategories = computed(() => 
    categories.value.filter(category => category.isActive)
  );
  
  const categoryOptions = computed(() => 
    categories.value.map(category => ({
      label: category.name,
      value: category.id,
      code: category.code,
      type: category.type
    }))
  );
  
  // Actions
  const fetchCategories = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      // TODO: Replace with actual API call
      // const response = await glCategoryService.getCategories();
      // categories.value = response.data;
      
      // Mock data for now
      categories.value = [
        { id: '1', code: 'CUR_ASSET', name: 'Current Assets', type: 'ASSET', isActive: true, description: 'Assets expected to be converted to cash within one year' },
        { id: '2', code: 'FIXED_ASSET', name: 'Fixed Assets', type: 'ASSET', isActive: true, description: 'Long-term tangible assets' },
        { id: '3', code: 'CUR_LIAB', name: 'Current Liabilities', type: 'LIABILITY', isActive: true, description: 'Obligations due within one year' },
        { id: '4', code: 'LONG_LIAB', name: 'Long-term Liabilities', type: 'LIABILITY', isActive: true, description: 'Obligations due after one year' },
        { id: '5', code: 'EQUITY', name: 'Equity', type: 'EQUITY', isActive: true, description: 'Owner\'s equity' },
        { id: '6', code: 'REVENUE', name: 'Revenue', type: 'REVENUE', isActive: true, description: 'Income from sales or services' },
        { id: '7', code: 'EXPENSE', name: 'Expenses', type: 'EXPENSE', isActive: true, description: 'Operating expenses' },
        { id: '8', code: 'COGS', name: 'Cost of Goods Sold', type: 'EXPENSE', isActive: true, description: 'Direct costs of producing goods' },
      ];
    } catch (err) {
      error.value = 'Failed to fetch GL categories';
      notification.error({
        title: 'Error',
        message: 'Failed to load GL categories. Please try again.'
      });
      console.error('Error fetching GL categories:', err);
    } finally {
      loading.value = false;
    }
  };
  
  const getCategoryById = (id: string) => {
    return categories.value.find(category => category.id === id);
  };
  
  const getCategoriesByType = (type: string) => {
    return categories.value.filter(category => category.type === type);
  };
  
  // Initialize the store
  fetchCategories();
  
  return {
    // State
    categories,
    loading,
    error,
    
    // Getters
    activeCategories,
    categoryOptions,
    
    // Actions
    fetchCategories,
    getCategoryById,
    getCategoriesByType,
  };
});

export default useGlCategoryStore;
