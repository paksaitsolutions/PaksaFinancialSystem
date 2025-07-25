<template>
  <div class="budget-dashboard">
    <PageHeader title="Budget Dashboard" subtitle="Overview of your budget performance" />
    
    <!-- Summary Cards -->
    <div class="grid">
      <div class="col-12 md:col-6 lg:col-3">
        <StatCard 
          title="Total Budget" 
          :value="formatCurrency(totalBudget)" 
          icon="pi pi-wallet" 
          color="primary"
        />
      </div>
      <div class="col-12 md:col-6 lg:col-3">
        <StatCard 
          title="Actual Spend" 
          :value="formatCurrency(actualSpend)" 
          icon="pi pi-chart-line" 
          color="success"
        />
      </div>
      <div class="col-12 md:col-6 lg:3">
        <StatCard 
          title="Remaining" 
          :value="formatCurrency(remainingBudget)" 
          icon="pi pi-percentage" 
          :color="remainingBudget < 0 ? 'danger' : 'info'"
        />
      </div>
      <div class="col-12 md:col-6 lg:3">
        <StatCard 
          title="Utilization" 
          :value="`${utilizationRate}%`" 
          icon="pi pi-chart-pie" 
          color="warning"
        />
      </div>
    </div>

    <!-- Budget vs Actual Chart -->
    <div class="card">
      <div class="flex justify-content-between align-items-center mb-4">
        <h3>Budget vs Actual</h3>
        <div>
          <v-select 
            v-model="selectedPeriod" 
            :items="periods" 
            item-title="name"
            item-value="code"
            label="Select Period"
            style="width: 200px"
          />
        </div>
      </div>
      <div style="height: 400px; display: flex; align-items: center; justify-content: center; background: #f5f5f5; border-radius: 8px;">
        <div class="text-center">
          <v-icon size="48" color="grey">mdi-chart-bar</v-icon>
          <p class="text-h6 mt-2">Budget vs Actual Chart</p>
          <p class="text-body-2">Chart visualization would be implemented here</p>
        </div>
      </div>
    </div>

    <!-- Recent Budget Activities -->
    <div class="card mt-4">
      <v-data-table 
        :items="recentActivities" 
        :headers="tableHeaders"
        items-per-page="5"
        class="elevation-1"
      >
        <template #item.date="{ item }">
          {{ formatDate(item.date) }}
        </template>
        <template #item.amount="{ item }">
          {{ formatCurrency(item.amount) }}
        </template>
        <template #item.status="{ item }">
          <v-chip :color="getStatusColor(item.status)" size="small">
            {{ item.status }}
          </v-chip>
        </template>
      </v-data-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useFormatting } from '../../composables/useFormatting';
import PageHeader from '../../components/layout/PageHeader.vue';
import StatCard from '../../components/common/StatCard.vue';
// Removed PrimeVue imports - using Vuetify components

const formatCurrency = (value: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
const formatDate = (date: Date) => new Intl.DateTimeFormat('en-US').format(date);

const tableHeaders = [
  { title: 'Date', key: 'date' },
  { title: 'Description', key: 'description' },
  { title: 'Amount', key: 'amount' },
  { title: 'Status', key: 'status' }
];

// Mock data - replace with actual API calls
const totalBudget = ref(1250000);
const actualSpend = ref(875000);
const remainingBudget = computed(() => totalBudget.value - actualSpend.value);
const utilizationRate = computed(() => 
  Math.round((actualSpend.value / totalBudget.value) * 100)
);

// Chart data
const selectedPeriod = ref({ name: 'This Year', code: 'year' });
const periods = [
  { name: 'This Month', code: 'month' },
  { name: 'This Quarter', code: 'quarter' },
  { name: 'This Year', code: 'year' },
];

const budgetChartData = ref({
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  datasets: [
    {
      label: 'Budget',
      backgroundColor: '#42A5F5',
      data: [100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000]
    },
    {
      label: 'Actual',
      backgroundColor: '#66BB6A',
      data: [70000, 85000, 92000, 78000, 88000, 90000, 95000, 102000, 88000, 92000, 0, 0]
    }
  ]
});

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      stacked: false,
    },
    y: {
      stacked: false,
      ticks: {
        callback: function(value: number) {
          return '₹' + (value / 1000) + 'k';
        }
      }
    }
  },
  plugins: {
    tooltip: {
      callbacks: {
        label: function(context: any) {
          let label = context.dataset.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed.y !== null) {
            label += formatCurrency(context.parsed.y);
          }
          return label;
        }
      }
    }
  }
});

// Recent activities
const recentActivities = ref([
  { 
    id: 1, 
    date: new Date(2023, 10, 15), 
    description: 'Marketing Campaign Q4', 
    amount: 50000, 
    status: 'Completed' 
  },
  { 
    id: 2, 
    date: new Date(2023, 10, 10), 
    description: 'Office Rent - November', 
    amount: 25000, 
    status: 'Completed' 
  },
  { 
    id: 3, 
    date: new Date(2023, 10, 5), 
    description: 'Team Offsite', 
    amount: 15000, 
    status: 'Pending Approval' 
  },
  { 
    id: 4, 
    date: new Date(2023, 9, 28), 
    description: 'Software Subscriptions', 
    amount: 5000, 
    status: 'Completed' 
  },
  { 
    id: 5, 
    date: new Date(2023, 9, 15), 
    description: 'Office Supplies', 
    amount: 3500, 
    status: 'Completed' 
  }
]);

// Helper functions
const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'completed':
      return 'success';
    case 'pending approval':
      return 'warning';
    case 'rejected':
      return 'error';
    default:
      return 'info';
  }
};

onMounted(() => {
  // Fetch actual data from API
  // fetchBudgetData();
});
</script>

<style scoped>
.budget-dashboard {
  padding: 1rem;
}

:deep(.p-datatable) {
  font-size: 0.9rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f8f9fa;
  font-weight: 600;
}
</style>
