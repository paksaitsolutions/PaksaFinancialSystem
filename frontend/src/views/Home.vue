<template>
  <div class="min-h-screen bg-gray-50 p-4 sm:p-6 md:p-8">
    <!-- Page Header -->
    <div class="max-w-7xl mx-auto mb-8">
      <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-2">Financial Management Dashboard</h1>
      <p class="text-gray-600">Access all financial modules and tools from one centralized location</p>
    </div>
    <!-- Quick Stats -->
    <div class="max-w-7xl mx-auto mb-8">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-200">
          <div class="flex items-center">
            <div class="p-3 rounded-lg bg-blue-50 text-blue-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Active Modules</p>
              <p class="text-2xl font-bold text-gray-800">12+</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
          <div class="flex items-center">
            <div class="p-3 rounded-lg bg-green-50 text-green-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Active Users</p>
              <p class="text-2xl font-bold text-gray-800">24/7</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
          <div class="flex items-center">
            <div class="p-3 rounded-lg bg-purple-50 text-purple-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Transactions</p>
              <p class="text-2xl font-bold text-gray-800">1,248</p>
              <p class="text-xs text-green-600 font-medium mt-1">+12.5% from yesterday</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
          <div class="flex items-center">
            <div class="p-3 rounded-lg bg-emerald-50 text-emerald-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">System Status</p>
              <div class="flex items-center mt-1">
                <span class="h-2.5 w-2.5 bg-green-500 rounded-full mr-2"></span>
                <span class="text-gray-800 font-medium">All Systems Operational</span>
              </div>
              <p class="text-xs text-gray-500 mt-1">Last updated: Just now</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Search and Quick Actions -->
    <div class="max-w-7xl mx-auto mb-8">
      <div class="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div class="relative flex-1 max-w-2xl">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input 
              type="text" 
              v-model="searchQuery"
              placeholder="Search modules, features, or actions..."
              class="block w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 placeholder-gray-400 text-sm"
            >
          </div>
          
          <div class="flex items-center space-x-2">
            <button 
              v-for="action in quickActions" 
              :key="action.label"
              @click="handleQuickAction(action)"
              class="flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors"
              :class="action.isPrimary 
                ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm' 
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="action.icon" />
              </svg>
              {{ action.label }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Module Categories -->
    <div class="max-w-7xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-semibold text-gray-800">Core Financial Modules</h2>
        <div class="text-sm text-gray-500">{{ filteredModules.length }} modules available</div>
      </div>
      <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3">
        <!-- General Ledger -->
        <ModuleCard 
          title="General Ledger"
          description="Complete accounting system with multi-currency support, financial statements, and reporting"
          icon="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          :actions="[
            { label: 'Chart of Accounts', to: '/gl/accounts' },
            { label: 'Journal Entries', to: '/gl/journal-entries' }
          ]"
          color="blue"
        />

        <!-- Accounts Payable -->
        <ModuleCard 
          title="Accounts Payable"
          description="Process vendor invoices, track payables, and manage vendor relationships"
          icon="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.1-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          :actions="[
            { label: 'Vendors', to: '/ap/vendors' },
            { label: 'Bills', to: '/ap/bills' }
          ]"
          color="green"
        />

        <!-- Accounts Receivable -->
        <ModuleCard 
          title="Accounts Receivable"
          description="Manage customer invoices, track receivables, and process payments"
          icon="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"
          :actions="[
            { label: 'Customers', to: '/ar/customers' },
            { label: 'Invoices', to: '/ar/invoices' }
          ]"
          color="purple"
        />
      </div>
    </div>

    <div class="max-w-7xl mx-auto mt-8">
      <h2 class="text-xl font-semibold text-gray-800 mb-6">Payroll & HR</h2>
      <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3">
        <!-- Payroll -->
        <ModuleCard 
          title="Payroll"
          description="Process employee salaries, benefits, and tax withholdings"
          icon="M12 6v6m0 0v6m0-6h6m-6 0H6M12 22a10 10 0 100-20 10 10 0 000 20z"
          :actions="[
            { label: 'Employees', to: '/payroll/employees' },
            { label: 'Process Payroll', to: '/payroll/process' }
          ]"
          color="yellow"
        />

        <!-- Human Resources -->
        <ModuleCard 
          title="Human Resources"
          description="Manage employee records, benefits, and compliance"
          icon="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
          :actions="[
            { label: 'Employee Directory', to: '/hr/employees' },
            { label: 'Time & Attendance', to: '/hr/attendance' }
          ]"
          color="pink"
        />

        <!-- Time & Attendance -->
        <ModuleCard 
          title="Time & Attendance"
          description="Track employee work hours, leaves, and attendance"
          icon="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          :actions="[
            { label: 'Timesheets', to: '/time/timesheets' },
            { label: 'Leave Management', to: '/time/leave' }
          ]"
          color="red"
        />
      </div>
    </div><!-- Close Payroll & HR section -->

    <!-- Additional Modules -->
    <div class="max-w-7xl mx-auto mt-8">
      <h2 class="text-xl font-semibold text-gray-800 mb-6">Additional Modules</h2>
      <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3">
        <!-- Payroll -->
        <ModuleCard 
          title="Payroll"
          description="Process employee salaries and benefits"
          icon="M12 6v6m0 0v6m0-6h6m-6 0H6M12 22a10 10 0 100-20 10 10 0 000 20z"
          :actions="[
            { label: 'Employees', to: '/payroll/employees' },
            { label: 'Process Payroll', to: '/payroll/process' }
          ]"
          color="yellow"
        />

        <!-- Cash Management -->
        <ModuleCard 
          title="Cash Management"
          description="Track and manage cash flow"
          icon="M3 6l9.735 5.52a1 1 0 00.53.143h.002a1 1 0 00.53-.143L21 6M4 18h16a1 1 0 001-1V7a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1z"
          :actions="[
            { label: 'Bank Accounts', to: '/cash/bank-accounts' },
            { label: 'Reconcile', to: '/cash/reconcile' }
          ]"
          color="indigo"
        />

        <!-- Fixed Assets -->
        <ModuleCard 
          title="Fixed Assets"
          description="Manage company assets and depreciation"
          icon="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
          :actions="[
            { label: 'Asset Register', to: '/assets/register' },
            { label: 'Depreciation', to: '/assets/depreciation' }
          ]"
          color="pink"
        />

        <!-- Taxation -->
        <ModuleCard 
          title="Taxation"
          description="Manage tax calculations and filings"
          icon="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          :actions="[
            { label: 'Tax Dashboard', to: '/tax/dashboard' },
            { label: 'File Returns', to: '/tax/returns' }
          ]"
          color="red"
        />

        <!-- Budgeting -->
        <ModuleCard 
          title="Budgeting"
          description="Create and track budgets"
          icon="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
          :actions="[
            { label: 'Create Budget', to: '/budgets/create' },
            { label: 'Budget Reports', to: '/budgets/reports' }
          ]"
          color="teal"
        />

        <!-- Inventory -->
        <ModuleCard 
          title="Inventory"
          description="Manage stock and inventory items"
          icon="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
          :actions="[
            { label: 'Products', to: '/inventory/products' },
            { label: 'Stock Movement', to: '/inventory/movement' }
          ]"
          color="orange"
        />
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="max-w-7xl mx-auto mt-16">
      <div class="bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-100">
        <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-center">
          <h2 class="text-xl font-bold text-gray-800 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            Recent Activity
          </h2>
          <button @click="router.push('/activity')" class="text-sm text-blue-600 hover:text-blue-800">View All</button>
        </div>
        
        <div class="divide-y divide-gray-100">
          <div v-for="(activity, index) in recentActivities" :key="index" class="p-6 hover:bg-gray-50 transition-colors duration-150">
            <div class="flex items-start">
              <div class="flex-shrink-0 h-10 w-10 rounded-xl bg-blue-50 flex items-center justify-center">
                <span class="text-blue-600 font-medium">{{ activity.initials }}</span>
              </div>
              <div class="ml-4 flex-1 min-w-0">
                <p class="text-sm text-gray-700">
                  <span class="font-medium text-gray-900">{{ activity.user }}</span> {{ activity.action }}
                  <a :href="activity.link" class="font-medium text-blue-600 hover:text-blue-800 hover:underline">{{ activity.entity }}</a>
                </p>
                <div class="flex items-center mt-1">
                  <span class="text-xs text-gray-500">{{ activity.time }}</span>
                  <span class="mx-2 text-gray-300">•</span>
                  <span class="text-xs px-2 py-0.5 rounded-full" :class="getActivityTypeClass(activity.type)">
                    {{ activity.type }}
                  </span>
                </div>
              </div>
              <button class="text-gray-400 hover:text-gray-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="max-w-7xl mx-auto mt-8 mb-16">
      <div class="p-6 bg-white rounded-lg shadow">
        <h3 class="mb-4 text-lg font-semibold">Quick Actions</h3>
        <div class="grid grid-cols-2 gap-3">
          <button 
            v-for="action in quickActions" 
            :key="action.label"
            @click="handleQuickAction(action)"
            class="flex flex-col items-center justify-center p-4 text-center transition-colors duration-200 bg-white border rounded-lg hover:bg-gray-50"
          >
            <div class="p-2 mb-2 rounded-full" :class="`bg-${action.color}-100 text-${action.color}-600`">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="action.icon" />
              </svg>
            </div>
            <span class="text-sm font-medium text-gray-700">{{ action.label }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import ModuleCard from '@/components/ui/ModuleCard.vue';

interface QuickAction {
  label: string;
  to: string;
  icon: string;
  color: string;
  isPrimary?: boolean;
}

interface Activity {
  user: string;
  action: string;
  entity: string;
  link: string;
  time: string;
  type: 'Create' | 'Update' | 'Delete' | 'System';
  initials: string;
}

// Removed unused icon components as they're not being used in the template

export default {
  name: 'HomeView',
  components: {
    ModuleCard,
  },
  setup() {
    const router = useRouter();
    const searchQuery = ref('');
    const activeCategory = ref('all');
    
    const modules = [
      {
        id: 'general-ledger',
        title: 'General Ledger',
        description: 'Manage chart of accounts, journal entries, and financial statements',
        category: 'accounting',
        icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
        actions: [
          { label: 'Chart of Accounts', to: '/gl/accounts' },
          { label: 'Journal Entries', to: '/gl/entries' },
          { label: 'Financial Statements', to: '/gl/reports' }
        ],
        color: 'blue'
      },
      {
        id: 'accounts-payable',
        title: 'Accounts Payable',
        description: 'Track and manage money owed to vendors',
        category: 'accounting',
        icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4',
        actions: [
          { label: 'Vendors', to: '/ap/vendors' },
          { label: 'Bills', to: '/ap/bills' },
          { label: 'Payments', to: '/ap/payments' }
        ],
        color: 'green'
      },
      {
        id: 'accounts-receivable',
        title: 'Accounts Receivable',
        description: 'Track and manage money owed by customers',
        category: 'accounting',
        icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
        actions: [
          { label: 'Customers', to: '/ar/customers' },
          { label: 'Invoices', to: '/ar/invoices' },
          { label: 'Receipts', to: '/ar/receipts' }
        ],
        color: 'purple'
      },
      {
        id: 'payroll',
        title: 'Payroll',
        description: 'Process employee salaries and benefits',
        category: 'hr',
        icon: 'M12 6v6m0 0v6m0-6h6m-6 0H6M12 22a10 10 0 100-20 10 10 0 000 20z',
        actions: [
          { label: 'Employees', to: '/payroll/employees' },
          { label: 'Process Payroll', to: '/payroll/process' },
          { label: 'Reports', to: '/payroll/reports' }
        ],
        color: 'yellow'
      },
      {
        id: 'cash-management',
        title: 'Cash Management',
        description: 'Track and manage cash flow',
        category: 'treasury',
        icon: 'M3 6l9.735 5.52a1 1 0 00.53.143h.002a1 1 0 00.53-.143L21 6M4 18h16a1 1 0 001-1V7a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1z',
        actions: [
          { label: 'Bank Accounts', to: '/cash/bank-accounts' },
          { label: 'Reconcile', to: '/cash/reconcile' },
          { label: 'Transfers', to: '/cash/transfers' }
        ],
        color: 'indigo'
      },
      {
        id: 'fixed-assets',
        title: 'Fixed Assets',
        description: 'Manage company assets and depreciation',
        category: 'accounting',
        icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10',
        actions: [
          { label: 'Asset Register', to: '/assets/register' },
          { label: 'Depreciation', to: '/assets/depreciation' },
          { label: 'Disposals', to: '/assets/disposals' }
        ],
        color: 'pink'
      },
      {
        id: 'taxation',
        title: 'Taxation',
        description: 'Manage tax calculations and filings',
        category: 'compliance',
        icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
        actions: [
          { label: 'Tax Dashboard', to: '/tax/dashboard' },
          { label: 'File Returns', to: '/tax/returns' },
          { label: 'Compliance', to: '/tax/compliance' }
        ],
        color: 'red'
      },
      {
        id: 'budgeting',
        title: 'Budgeting',
        description: 'Create and manage budgets',
        category: 'planning',
        icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01',
        actions: [
          { label: 'Create Budget', to: '/budgets/new' },
          { label: 'Budget Reports', to: '/budgets/reports' },
          { label: 'Forecasting', to: '/budgets/forecast' }
        ],
        color: 'teal'
      },
      {
        id: 'inventory',
        title: 'Inventory',
        description: 'Manage stock levels and items',
        category: 'operations',
        icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4',
        actions: [
          { label: 'Items', to: '/inventory/items' },
          { label: 'Stock Movements', to: '/inventory/movements' },
          { label: 'Valuation', to: '/inventory/valuation' }
        ],
        color: 'orange'
      }
    ];

    const filteredModules = computed(() => {
      let result = [...modules];
      
      // Filter by search query
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(module => 
          module.title.toLowerCase().includes(query) || 
          module.description.toLowerCase().includes(query) ||
          module.category.toLowerCase().includes(query)
        );
      }
      
      // Filter by category
      if (activeCategory.value !== 'all') {
        result = result.filter(module => module.category === activeCategory.value);
      }
      
      return result;
    });
    
    const categories = [
      { id: 'all', name: 'All Modules' },
      { id: 'accounting', name: 'Accounting' },
      { id: 'hr', name: 'HR & Payroll' },
      { id: 'treasury', name: 'Treasury' },
      { id: 'compliance', name: 'Compliance' },
      { id: 'planning', name: 'Planning' },
      { id: 'operations', name: 'Operations' }
    ];
    const recentActivities: Activity[] = [
      {
        user: 'System',
        action: 'System initialized',
        entity: 'Dashboard',
        link: '#',
        time: 'Just now',
        type: 'System',
        initials: 'SYS'
      }
    ];

    const quickActions: QuickAction[] = [
      { label: 'New Invoice', to: '/invoices/new', icon: 'M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z', color: 'blue', isPrimary: true },
      { label: 'Record Payment', to: '/payments/new', icon: 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z', color: 'green', isPrimary: false },
      { label: 'Add Expense', to: '/expenses/new', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z', color: 'red', isPrimary: false },
      { label: 'New Customer', to: '/customers/new', icon: 'M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z', color: 'purple', isPrimary: false }
    ];

    const getActivityTypeClass = (type: Activity['type']) => {
      const typeClasses = {
        Create: 'bg-green-100 text-green-800',
        Update: 'bg-blue-100 text-blue-800',
        Delete: 'bg-red-100 text-red-800',
        System: 'bg-gray-100 text-gray-800',
        default: 'bg-gray-100 text-gray-800'
      };
      return typeClasses[type] || typeClasses.default;
    };

    const handleQuickAction = (action: QuickAction) => {
      if (action.to) {
        router.push(action.to);
      }
    };

    return {
      searchQuery,
      activeCategory,
      recentActivities,
      quickActions,
      getActivityTypeClass,
      router,
      filteredModules,
      categories,
      modules,
      handleQuickAction
    };
  }
}
</script>

<style scoped>
/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Animation for cards */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.module-card {
  animation: fadeIn 0.3s ease-out forwards;
  opacity: 0;
}

/* Add delay for each card */
.module-card:nth-child(1) { animation-delay: 0.1s; }
.module-card:nth-child(2) { animation-delay: 0.15s; }
.module-card:nth-child(3) { animation-delay: 0.2s; }
.module-card:nth-child(n+4) { animation-delay: 0.25s; }

/* Hover effects */
.hover-scale {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.hover-scale:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
}

/* Gradient text */
.text-gradient {
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Custom focus styles */
.focus-ring:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5);
}

/* Smooth transitions */
.transition-smooth {
  transition: all 0.2s ease-in-out;
}

/* Custom scrollbar for activity feed */
.activity-scroll {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.activity-scroll::-webkit-scrollbar {
  width: 6px;
}

.activity-scroll::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.activity-scroll::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
}

.activity-scroll::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .quick-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .quick-stats,
  .quick-actions {
    grid-template-columns: 1fr;
  }
}

.home-page {
  min-height: 100vh;
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 0;
  margin: -24px -24px 0 -24px;
}

.feature-card {
  transition: transform 0.2s ease-in-out;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.stat-card {
  transition: transform 0.2s ease-in-out;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.quick-action-card {
  transition: all 0.2s ease-in-out;
  cursor: pointer;
}

.quick-action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.features-section,
.stats-section,
.quick-access-section {
  padding: 60px 0;
}
</style>