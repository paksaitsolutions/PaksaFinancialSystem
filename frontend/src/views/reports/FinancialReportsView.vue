<template>
  <div class="reports-dashboard">
    <!-- Header Section -->
    <div class="reports-header p-4">
      <div class="flex justify-content-between align-items-center mb-4">
        <div>
          <h1 class="text-3xl font-bold m-0">Financial Reports</h1>
          <p class="text-color-secondary m-0 mt-2">Access, generate, and analyze all your financial reports in one place</p>
        </div>
        <div class="flex gap-2">
          <Button 
            icon="pi pi-plus" 
            label="New Report" 
            class="p-button-outlined"
            @click="showReportBuilder = true"
          />
          <Button 
            icon="pi pi-cog" 
            class="p-button-text" 
            v-tooltip.top="'Report Settings'"
          />
        </div>
      </div>

      <!-- Search and Filters -->
      <div class="flex justify-content-between align-items-center mb-4 gap-4">
        <span class="p-input-icon-left w-full">
          <i class="pi pi-search" />
          <InputText 
            v-model="searchQuery" 
            placeholder="Search reports..." 
            class="w-full"
            @keyup.enter="applySearch"
          />
        </span>
        <div class="flex gap-2">
          <Dropdown 
            v-model="selectedCategory" 
            :options="reportCategories.map(c => c.name)" 
            placeholder="All Categories" 
            class="w-15rem"
            @change="filterReports"
          />
          <Button 
            icon="pi pi-filter" 
            class="p-button-outlined" 
            label="Filters" 
            @click="showFilters = !showFilters"
          />
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions mb-5">
        <div class="text-500 font-medium mb-2">QUICK ACTIONS</div>
        <div class="flex flex-wrap gap-3">
          <Button 
            v-for="action in quickActions" 
            :key="action.label"
            :label="action.label"
            :icon="action.icon"
            class="p-button-outlined p-button-sm"
            @click="handleQuickAction(action)"
          />
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="p-4">
      <!-- Favorites Section -->
      <div v-if="favoriteReports.length > 0" class="mb-6">
        <div class="flex justify-content-between align-items-center mb-3">
          <h2 class="text-xl font-semibold m-0">
            <i class="pi pi-star-fill text-yellow-500 mr-2"></i>
            Favorites
          </h2>
          <Button 
            label="View All" 
            icon="pi pi-chevron-right" 
            class="p-button-text p-0"
            @click="navigateTo('/reports/favorites')"
          />
        </div>
        <div class="grid">
          <div 
            v-for="report in favoriteReports" 
            :key="'fav-' + report.id"
            class="col-12 md:col-6 lg:col-4 xl:col-3"
          >
            <ReportCard 
              :report="report" 
              :is-favorite="true" 
              @favorite="toggleFavorite(report)"
              @run="navigateToReport(report)"
            />
          </div>
        </div>
      </div>

      <!-- Recent Reports -->
      <div v-if="recentReports.length > 0" class="mb-6">
        <div class="flex justify-content-between align-items-center mb-3">
          <h2 class="text-xl font-semibold m-0">
            <i class="pi pi-clock text-blue-500 mr-2"></i>
            Recently Viewed
          </h2>
          <Button 
            label="View All" 
            icon="pi pi-chevron-right" 
            class="p-button-text p-0"
            @click="navigateTo('/reports/recent')"
          />
        </div>
        <div class="grid">
          <div 
            v-for="report in recentReports" 
            :key="'recent-' + report.id"
            class="col-12 md:col-6 lg:col-4 xl:col-3"
          >
            <ReportCard 
              :report="report" 
              :is-favorite="isFavorite(report.id)" 
              @favorite="toggleFavorite(report)"
              @run="navigateToReport(report)"
            />
          </div>
        </div>
      </div>

      <!-- All Reports by Category -->
      <div v-for="category in filteredCategories" :key="category.id" class="mb-6">
        <h2 class="text-xl font-semibold mb-3">
          <i :class="[category.icon, 'mr-2', 'text-primary']"></i>
          {{ category.name }}
        </h2>
        <div class="grid">
          <div 
            v-for="report in category.reports" 
            :key="report.id"
            class="col-12 md:col-6 lg:col-4 xl:col-3"
          >
            <ReportCard 
              :report="report" 
              :is-favorite="isFavorite(report.id)" 
              @favorite="toggleFavorite(report)"
              @run="navigateToReport(report)"
            />
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredCategories.length === 0" class="text-center p-5">
        <i class="pi pi-search text-6xl text-400 mb-3"></i>
        <h3 class="text-2xl font-medium mb-2">No reports found</h3>
        <p class="text-600 mb-4">Try adjusting your search or filter criteria</p>
        <Button 
          label="Clear Filters" 
          class="p-button-text" 
          @click="clearFilters"
        />
      </div>
    </div>

    <!-- Report Builder Dialog -->
    <Dialog 
      v-model:visible="showReportBuilder" 
      header="Create New Report" 
      :modal="true"
      :style="{ width: '50vw' }"
      :dismissableMask="true"
    >
      <ReportBuilder @close="showReportBuilder = false" />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import Button from 'primevue/button';
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import Dialog from 'primevue/dialog';
import ReportCard from '@/components/reports/ReportCard.vue';
import ReportBuilder from '@/components/reports/ReportBuilder.vue';

interface ReportDefinition {
  id: string;
  name: string;
  description: string;
  route: string;
  icon: string;
  category: string;
  lastRun?: string;
  favorite?: boolean;
  tags?: string[];
}

interface ReportCategory {
  id: string;
  name: string;
  icon: string;
  reports: ReportDefinition[];
}

const reportCategories = ref<ReportCategory[]>([
  {
    id: 'financial-statements',
    name: 'Financial Statements',
    icon: 'pi pi-file-pdf',
    reports: [
      {
        id: 'balance-sheet',
        name: 'Balance Sheet',
        description: 'View your company\'s financial position at a specific point in time',
        route: '/reports/balance-sheet',
        icon: 'pi pi-file-pdf'
      },
      {
        id: 'income-statement',
        name: 'Income Statement',
        description: 'View your company\'s revenues and expenses over a period of time',
        route: '/reports/income-statement',
        icon: 'pi pi-chart-line'
      },
      {
        id: 'cash-flow',
        name: 'Cash Flow Statement',
        description: 'Track the flow of cash in and out of your business',
        route: '/reports/cash-flow',
        icon: 'pi pi-money-bill'
      },
      {
        id: 'retained-earnings',
        name: 'Retained Earnings',
        description: 'View the accumulated profits not distributed to shareholders',
        route: '/reports/retained-earnings',
        icon: 'pi pi-chart-pie'
      }
    ]
  },
  {
    id: 'general-ledger',
    name: 'General Ledger',
    icon: 'pi pi-book',
    reports: [
      {
        id: 'trial-balance',
        name: 'Trial Balance',
        description: 'View all account balances to ensure debits equal credits',
        route: '/reports/trial-balance',
        icon: 'pi pi-balance-scale'
      },
      {
        id: 'general-ledger-detail',
        name: 'General Ledger Detail',
        description: 'View detailed transaction history for all accounts',
        route: '/reports/general-ledger-detail',
        icon: 'pi pi-list'
      },
      {
        id: 'journal',
        name: 'Journal Report',
        description: 'View all journal entries for a specific period',
        route: '/reports/journal',
        icon: 'pi pi-bookmark'
      }
    ]
  },
  {
    id: 'accounts',
    name: 'Accounts',
    icon: 'pi pi-wallet',
    reports: [
      {
        id: 'accounts-receivable',
        name: 'Accounts Receivable Aging',
        description: 'Track outstanding customer invoices and payments',
        route: '/reports/ar-aging',
        icon: 'pi pi-credit-card'
      },
      {
        id: 'accounts-payable',
        name: 'Accounts Payable Aging',
        description: 'Track outstanding bills and vendor payments',
        route: '/reports/ap-aging',
        icon: 'pi pi-shopping-cart'
      },
      {
        id: 'revenue-by-customer',
        name: 'Revenue by Customer',
        description: 'Analyze revenue by customer for a specific period',
        route: '/reports/revenue-by-customer',
        icon: 'pi pi-users'
      },
      {
        id: 'expenses-by-vendor',
        name: 'Expenses by Vendor',
        description: 'Analyze expenses by vendor for a specific period',
        route: '/reports/expenses-by-vendor',
        icon: 'pi pi-truck'
      }
    ]
  },
  {
    id: 'tax',
    name: 'Tax Reports',
    icon: 'pi pi-percentage',
    reports: [
      {
        id: 'sales-tax',
        name: 'Sales Tax Report',
        description: 'View sales tax collected and owed',
        route: '/reports/sales-tax',
        icon: 'pi pi-percentage'
      },
      {
        id: 'vat',
        name: 'VAT Report',
        description: 'View VAT collected and paid',
        route: '/reports/vat',
        icon: 'pi pi-euro'
      },
      {
        id: 'tax-summary',
        name: 'Tax Summary',
        description: 'Summary of all tax-related transactions',
        route: '/reports/tax-summary',
        icon: 'pi pi-file-export'
      }
    ]
  },
  {
    id: 'budget',
    name: 'Budget Reports',
    icon: 'pi pi-chart-bar',
    reports: [
      {
        id: 'budget-vs-actual',
        name: 'Budget vs Actual',
        description: 'Compare budgeted amounts to actual results',
        route: '/reports/budget-vs-actual',
        icon: 'pi pi-chart-bar'
      },
      {
        id: 'budget-overview',
        name: 'Budget Overview',
        description: 'View budget allocations and spending by category',
        route: '/reports/budget-overview',
        icon: 'pi pi-chart-pie'
      }
    ]
  },
  {
    id: 'inventory',
    name: 'Inventory Reports',
    icon: 'pi pi-box',
    reports: [
      {
        id: 'inventory-valuation',
        name: 'Inventory Valuation',
        description: 'View the value of your current inventory',
        route: '/reports/inventory-valuation',
        icon: 'pi pi-tags'
      },
      {
        id: 'inventory-turnover',
        name: 'Inventory Turnover',
        description: 'Analyze how quickly inventory is sold',
        route: '/reports/inventory-turnover',
        icon: 'pi pi-sync'
      }
    ]
  }
]);

const navigateToReport = (report: ReportDefinition) => {
  router.push(report.route);
};
</script>

<style scoped>
.financial-reports {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.report-header {
  margin-bottom: 2rem;
  text-align: center;
}

.report-header h1 {
  margin: 0;
  font-size: 2rem;
  color: var(--primary-color);
}

.report-categories {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.category-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.report-list {
  padding: 0;
  margin: 0;
}

.report-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0.5rem;
  border-bottom: 1px solid var(--surface-d);
  cursor: pointer;
  transition: background-color 0.2s;
}

.report-item:last-child {
  border-bottom: none;
}

.report-item:hover {
  background-color: var(--surface-100);
}

.report-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  color: var(--text-color);
}

.report-info .description {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.report-item i {
  color: var(--text-color-secondary);
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .report-categories {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
}

@media (max-width: 768px) {
  .report-categories {
    grid-template-columns: 1fr;
  }
  
  .financial-reports {
    padding: 1rem;
  }
}
</style>
