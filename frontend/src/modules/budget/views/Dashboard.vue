<template>
  <v-container fluid class="budget-dashboard">
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4">Budget Dashboard</h1>
        <p class="text-subtitle-1">Overview of your budget performance</p>
      </v-col>
    </v-row>
    
    <!-- Summary Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="6" lg="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center">
              <v-avatar color="primary" class="mr-3">
                <v-icon color="white">mdi-wallet</v-icon>
              </v-avatar>
              <div>
                <div class="text-caption">Total Budget</div>
                <div class="text-h6">{{ formatCurrency(totalBudget) }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6" lg="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center">
              <v-avatar color="success" class="mr-3">
                <v-icon color="white">mdi-chart-line</v-icon>
              </v-avatar>
              <div>
                <div class="text-caption">Actual Spend</div>
                <div class="text-h6">{{ formatCurrency(actualSpend) }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6" lg="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center">
              <v-avatar :color="remainingBudget < 0 ? 'error' : 'info'" class="mr-3">
                <v-icon color="white">mdi-percent</v-icon>
              </v-avatar>
              <div>
                <div class="text-caption">Remaining</div>
                <div class="text-h6">{{ formatCurrency(remainingBudget) }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6" lg="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center">
              <v-avatar color="warning" class="mr-3">
                <v-icon color="white">mdi-chart-pie</v-icon>
              </v-avatar>
              <div>
                <div class="text-caption">Utilization</div>
                <div class="text-h6">{{ utilizationRate }}%</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Budget vs Actual Chart -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span>Budget vs Actual</span>
            <v-select 
              v-model="selectedPeriod" 
              :items="periods" 
              item-title="name"
              item-value="code"
              label="Select Period"
              style="width: 200px"
              variant="outlined"
              density="compact"
            />
          </v-card-title>
          <v-card-text>
            <div style="height: 400px; display: flex; align-items: center; justify-content: center; background: #f5f5f5; border-radius: 8px;">
              <div class="text-center">
                <v-icon size="48" color="grey">mdi-chart-bar</v-icon>
                <p class="text-h6 mt-2">Budget vs Actual Chart</p>
                <p class="text-body-2">Chart visualization would be implemented here</p>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent Budget Activities -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Recent Budget Activities</v-card-title>
          <v-card-text>
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
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useFormatting } from '../../composables/useFormatting';
// Using Vuetify components only

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

/* Vuetify styling */
</style>
