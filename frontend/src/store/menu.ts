import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useAuthStore } from '@/modules/auth/store';

export interface MenuModule {
  id: string;
  title: string;
  icon: string;
  route: string;
  children?: MenuModule[];
  permissions?: string[];
  isPublic?: boolean;
  isVisible?: boolean;
}

export const useMenuStore = defineStore('menu', () => {
  const isExpanded = ref<boolean>(true);
  const activeModule = ref<string | null>(null);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);
  const authStore = useAuthStore();
  
  // Define all available modules with visibility and permissions
  const allModules = ref<MenuModule[]>([
    {
      id: 'dashboard',
      title: 'Dashboard',
      icon: 'mdi-view-dashboard',
      route: '/dashboard'
    },
    {
      id: 'general-ledger',
      title: 'General Ledger',
      icon: 'mdi-book-open-variant',
      route: '/gl',
      children: [
        { id: 'gl-accounts', title: 'Chart of Accounts', icon: 'mdi-format-list-bulleted', route: '/gl/accounts' },
        { id: 'journal-entries', title: 'Journal Entries', icon: 'mdi-book-open-page-variant', route: '/gl/entries' },
        { id: 'trial-balance', title: 'Trial Balance', icon: 'mdi-scale-balance', route: '/gl/trial-balance' },
        { id: 'financial-reports', title: 'Financial Reports', icon: 'mdi-file-document-multiple', route: '/gl/reports' }
      ]
    },
    {
      id: 'accounts-payable',
      title: 'Accounts Payable',
      icon: 'mdi-account-arrow-right',
      route: '/ap',
      children: [
        { id: 'vendors', title: 'Vendors', icon: 'mdi-account-group', route: '/ap/vendors' },
        { id: 'bills', title: 'Bills', icon: 'mdi-receipt', route: '/ap/bills' },
        { id: 'payments', title: 'Payments', icon: 'mdi-credit-card', route: '/ap/payments' },
        { id: 'ap-reports', title: 'Reports', icon: 'mdi-chart-bar', route: '/ap/reports' }
      ]
    },
    {
      id: 'accounts-receivable',
      title: 'Accounts Receivable',
      icon: 'mdi-account-arrow-left',
      route: '/ar',
      children: [
        { id: 'customers', title: 'Customers', icon: 'mdi-account-group', route: '/ar/customers' },
        { id: 'invoices', title: 'Invoices', icon: 'mdi-receipt', route: '/ar/invoices' },
        { id: 'receipts', title: 'Receipts', icon: 'mdi-credit-card', route: '/ar/receipts' },
        { id: 'ar-reports', title: 'Reports', icon: 'mdi-chart-bar', route: '/ar/reports' }
      ]
    },
    {
      id: 'payroll',
      title: 'Payroll',
      icon: 'mdi-account-cash',
      route: '/payroll',
      children: [
        { id: 'employees', title: 'Employees', icon: 'mdi-account-tie', route: '/payroll/employees' },
        { id: 'payroll-runs', title: 'Payroll Runs', icon: 'mdi-calendar-clock', route: '/payroll/runs' },
        { id: 'payroll-reports', title: 'Reports', icon: 'mdi-chart-bar', route: '/payroll/reports' },
        { id: 'tax-filings', title: 'Tax Filings', icon: 'mdi-file-document', route: '/payroll/tax-filings' }
      ]
    },
    {
      id: 'tax',
      title: 'Tax',
      icon: 'mdi-calculator',
      route: '/tax',
      children: [
        { id: 'tax-calculation', title: 'Tax Calculation', icon: 'mdi-calculator', route: '/tax/calculation' },
        { id: 'tax-filings', title: 'Tax Filings', icon: 'mdi-file-document', route: '/tax/filings' },
        { id: 'tax-reports', title: 'Reports', icon: 'mdi-chart-bar', route: '/tax/reports' }
      ]
    },
    {
      id: 'reports',
      title: 'Reports',
      icon: 'mdi-chart-bar',
      route: '/reports',
      children: [
        { id: 'financial-reports', title: 'Financial Reports', icon: 'mdi-file-document', route: '/reports/financial' },
        { id: 'tax-reports', title: 'Tax Reports', icon: 'mdi-file-document', route: '/reports/tax' },
        { id: 'payroll-reports', title: 'Payroll Reports', icon: 'mdi-file-document', route: '/reports/payroll' },
        { id: 'custom-reports', title: 'Custom Reports', icon: 'mdi-file-document', route: '/reports/custom' }
      ]
    },
    {
      id: 'settings',
      title: 'Settings',
      icon: 'mdi-cog',
      route: '/settings',
      children: [
        { id: 'company', title: 'Company', icon: 'mdi-office-building', route: '/settings/company' },
        { id: 'users', title: 'Users & Permissions', icon: 'mdi-account-group', route: '/settings/users' },
        { id: 'integrations', title: 'Integrations', icon: 'mdi-connection', route: '/settings/integrations' },
        { id: 'system', title: 'System Settings', icon: 'mdi-tune', route: '/settings/system' }
      ]
    }
  ]);

  // Fetch menu items based on user permissions
  const fetchMenuItems = async (): Promise<void> => {
    try {
      isLoading.value = true;
      error.value = null;
      
      // In a real app, you would fetch menu items from an API
      // const response = await api.get('/api/menu');
      // allModules.value = response.data;
      
      // For now, we'll just use the static modules but update visibility
      updateModuleVisibility();
    } catch (err) {
      console.error('Failed to fetch menu items:', err);
      error.value = 'Failed to load menu items. Please try again later.';
    } finally {
      isLoading.value = false;
    }
  };

  // Update module visibility based on user permissions
  const updateModuleVisibility = (): void => {
    allModules.value = allModules.value.map(module => ({
      ...module,
      isVisible: isModuleVisible(module)
    }));
  };

  // Check if a module should be visible to the current user
  const isModuleVisible = (module: MenuModule): boolean => {
    // Public modules are always visible
    if (module.isPublic) return true;
    
    // If user is not authenticated, only show public modules
    if (!authStore.isAuthenticated) return false;
    
    // If no permissions required, module is visible to all authenticated users
    if (!module.permissions || module.permissions.length === 0) return true;
    
    // Check if user has all required permissions
    return module.permissions.every(permission => 
      authStore.user?.permissions?.includes(permission)
    );
  };

  // Computed property for visible modules
  const visibleModules = computed(() => {
    return allModules.value.filter(module => module.isVisible !== false);
  });

  // Toggle sidebar expanded state
  const toggleExpanded = (): void => {
    isExpanded.value = !isExpanded.value;
  };

  // Set active module
  const setActiveModule = (module: string | null): void => {
    activeModule.value = module;
  };

  // Initialize the store
  const init = (): void => {
    // Update module visibility when authentication state changes
    authStore.$subscribe(() => {
      updateModuleVisibility();
    });
    
    // Initial visibility update
    updateModuleVisibility();
  };

  return {
    // State
    isExpanded,
    activeModule,
    isLoading,
    error,
    
    // Getters
    visibleModules,
    
    // Actions
    fetchMenuItems,
    toggleExpanded,
    setActiveModule,
    init
  };
});
