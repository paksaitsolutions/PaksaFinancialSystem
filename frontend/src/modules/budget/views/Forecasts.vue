<template>
  <div class="budget-forecasts">
    <PageHeader 
      title="Budget Forecasts" 
      subtitle="Projected budget performance and variance analysis" 
    >
      <template #actions>
        <Button 
          label="New Forecast" 
          icon="pi pi-plus" 
          class="p-button-outlined"
          @click="openNewForecastDialog"
        />
      </template>
    </PageHeader>

    <!-- Forecast Controls -->
    <div class="card mb-4">
      <div class="grid">
        <div class="col-12 md:col-4">
          <div class="p-fluid">
            <label for="scenario">Scenario</label>
            <Dropdown 
              id="scenario"
              v-model="selectedScenario" 
              :options="scenarios" 
              optionLabel="name" 
              placeholder="Select Scenario"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12 md:col-4">
          <div class="p-fluid">
            <label for="timeframe">Timeframe</label>
            <Dropdown 
              id="timeframe"
              v-model="selectedTimeframe" 
              :options="timeframes" 
              optionLabel="name" 
              placeholder="Select Timeframe"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12 md:col-4">
          <div class="p-fluid">
            <label for="department">Department</label>
            <Dropdown 
              id="department"
              v-model="selectedDepartment" 
              :options="departments" 
              optionLabel="name" 
              placeholder="All Departments"
              class="w-full"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Forecast Summary -->
    <div class="grid">
      <div class="col-12 md:col-4">
        <div class="card h-full">
          <h3 class="text-center">Forecast Summary</h3>
          <div class="text-center mt-4">
            <h4 class="mb-2">Total Forecast</h4>
            <div class="text-4xl font-bold text-primary">{{ formatCurrency(forecastSummary.total) }}</div>
          </div>
          <Divider />
          <div class="grid text-center">
            <div class="col-6">
              <div class="text-500 mb-1">Budget</div>
              <div class="font-medium">{{ formatCurrency(forecastSummary.budget) }}</div>
            </div>
            <div class="col-6">
              <div class="text-500 mb-1">Variance</div>
              <div 
                class="font-medium" 
                :class="forecastSummary.variance >= 0 ? 'text-green-500' : 'text-red-500'"
              >
                {{ formatCurrency(forecastSummary.variance) }} ({{ forecastSummary.variancePercentage }}%)
              </div>
            </div>
          </div>
          <Divider />
          <div class="text-center">
            <span class="text-500">Last Updated: </span>
            <span class="font-medium">{{ formatDate(forecastSummary.lastUpdated) }}</span>
          </div>
        </div>
      </div>
      
      <div class="col-12 md:col-8">
        <div class="card h-full">
          <div class="flex justify-content-between align-items-center mb-4">
            <h3>Forecast vs Actual</h3>
            <div class="flex align-items-center">
              <span class="mr-3">View:</span>
              <SelectButton 
                v-model="chartView" 
                :options="chartViewOptions" 
                optionLabel="name"
                optionValue="value"
                class="p-buttons-sm"
              />
            </div>
          </div>
          <Chart type="bar" :data="forecastChartData" :options="chartOptions" />
        </div>
      </div>
    </div>

    <!-- Forecast Details -->
    <div class="card mt-4">
      <DataTable 
        :value="forecastDetails" 
        :paginator="true" 
        :rows="10"
        :rowsPerPageOptions="[5, 10, 20, 50]"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} entries"
        :filters="filters"
        filterDisplay="menu"
        :globalFilterFields="['category', 'department', 'status']"
      >
        <template #header>
          <div class="flex justify-content-between align-items-center">
            <h3>Forecast Details</h3>
            <span class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText v-model="filters['global'].value" placeholder="Search..." />
            </span>
          </div>
        </template>

        <Column field="category" header="Category" sortable filter filterPlaceholder="Search by category">
          <template #filter="{ filterModel, filterCallback }">
            <InputText 
              v-model="filterModel.value" 
              @keydown.enter="filterCallback()" 
              class="p-column-filter"
              placeholder="Search by category"
            />
          </template>
        </Column>
        
        <Column field="department" header="Department" sortable filter filterPlaceholder="Search by department">
          <template #filter="{ filterModel, filterCallback }">
            <Dropdown 
              v-model="filterModel.value" 
              :options="departments" 
              optionLabel="name"
              placeholder="Select Department"
              class="p-column-filter"
              @change="filterCallback()"
              :showClear="true"
            >
              <template #option="slotProps">
                <div>{{ slotProps.option.name }}</div>
              </template>
            </Dropdown>
          </template>
        </Column>
        
        <Column field="forecastAmount" header="Forecast" sortable>
          <template #body="{ data }">
            {{ formatCurrency(data.forecastAmount) }}
          </template>
        </Column>
        
        <Column field="actualAmount" header="Actual" sortable>
          <template #body="{ data }">
            {{ formatCurrency(data.actualAmount) }}
          </template>
        </Column>
        
        <Column field="variance" header="Variance" sortable>
          <template #body="{ data }">
            <div :class="data.variance >= 0 ? 'text-green-500' : 'text-red-500'">
              {{ formatCurrency(data.variance) }} ({{ data.variancePercentage }}%)
            </div>
          </template>
        </Column>
        
        <Column field="status" header="Status" sortable filter filterField="status">
          <template #body="{ data }">
            <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
          </template>
          <template #filter="{ filterModel, filterCallback }">
            <Dropdown 
              v-model="filterModel.value" 
              :options="statuses" 
              optionLabel="name"
              placeholder="Select Status"
              class="p-column-filter"
              @change="filterCallback()"
              :showClear="true"
            >
              <template #option="slotProps">
                <Tag :value="slotProps.option.name" :severity="getStatusSeverity(slotProps.option.name)" />
              </template>
            </Dropdown>
          </template>
        </Column>
        
        <Column header="Actions" :exportable="false" style="min-width: 8rem">
          <template #body="{ data }">
            <Button 
              icon="pi pi-pencil" 
              class="p-button-rounded p-button-text p-button-sm"
              @click="editForecast(data)"
            />
            <Button 
              icon="pi pi-trash" 
              class="p-button-rounded p-button-text p-button-sm p-button-danger"
              @click="confirmDeleteForecast(data)"
            />
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- New Forecast Dialog -->
    <Dialog 
      v-model:visible="forecastDialog" 
      :style="{width: '600px'}" 
      header="New Budget Forecast" 
      :modal="true"
      class="p-fluid"
    >
      <div class="field">
        <label for="forecastName">Forecast Name</label>
        <InputText 
          id="forecastName"
          v-model="forecast.name"
          required="true"
          autofocus
          :class="{'p-invalid': submitted && !forecast.name}"
        />
        <small class="p-error" v-if="submitted && !forecast.name">Name is required.</small>
      </div>
      
      <div class="field">
        <label for="scenario">Scenario</label>
        <Dropdown 
          id="scenario"
          v-model="forecast.scenario" 
          :options="scenarios" 
          optionLabel="name"
          placeholder="Select a Scenario"
          :class="{'p-invalid': submitted && !forecast.scenario}"
        />
        <small class="p-error" v-if="submitted && !forecast.scenario">Scenario is required.</small>
      </div>
      
      <div class="field">
        <label for="startDate">Start Date</label>
        <Calendar 
          id="startDate" 
          v-model="forecast.startDate" 
          :showIcon="true" 
          dateFormat="yy-mm-dd"
          :class="{'p-invalid': submitted && !forecast.startDate}"
        />
        <small class="p-error" v-if="submitted && !forecast.startDate">Start date is required.</small>
      </div>
      
      <div class="field">
        <label for="endDate">End Date</label>
        <Calendar 
          id="endDate" 
          v-model="forecast.endDate" 
          :showIcon="true" 
          dateFormat="yy-mm-dd"
          :minDate="forecast.startDate"
          :class="{'p-invalid': submitted && !forecast.endDate}"
        />
        <small class="p-error" v-if="submitted && !forecast.endDate">End date is required.</small>
      </div>
      
      <div class="field">
        <label for="description">Description</label>
        <Textarea 
          id="description" 
          v-model="forecast.description" 
          :autoResize="true" 
          rows="3"
        />
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="hideDialog"
        />
        <Button 
          label="Save" 
          icon="pi pi-check" 
          class="p-button-text" 
          @click="saveForecast"
        />
      </template>
    </Dialog>
    
    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="deleteForecastDialog" 
      :style="{width: '450px'}" 
      header="Confirm" 
      :modal="true"
    >
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="forecast">Are you sure you want to delete <b>{{forecast.name}}</b>?</span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="deleteForecastDialog = false"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-text" 
          @click="deleteForecast"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { FilterMatchMode } from 'primevue/api';
import { useFormatting } from '../../composables/useFormatting';
import PageHeader from '../../components/layout/PageHeader.vue';
import Chart from 'primevue/chart';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Calendar from 'primevue/calendar';
import Textarea from 'primevue/textarea';
import Tag from 'primevue/tag';
import SelectButton from 'primevue/selectbutton';
import Divider from 'primevue/divider';

const { formatCurrency, formatDate } = useFormatting();

// Data
const selectedScenario = ref({ name: 'Best Case', code: 'best' });
const selectedTimeframe = ref({ name: 'This Year', code: 'year' });
const selectedDepartment = ref({ name: 'All Departments', code: 'all' });
const chartView = ref('monthly');

const scenarios = [
  { name: 'Best Case', code: 'best' },
  { name: 'Most Likely', code: 'likely' },
  { name: 'Worst Case', code: 'worst' },
];

const timeframes = [
  { name: 'This Month', code: 'month' },
  { name: 'This Quarter', code: 'quarter' },
  { name: 'This Year', code: 'year' },
  { name: 'Custom', code: 'custom' },
];

const departments = [
  { name: 'All Departments', code: 'all' },
  { name: 'Sales', code: 'sales' },
  { name: 'Marketing', code: 'marketing' },
  { name: 'Operations', code: 'operations' },
  { name: 'Finance', code: 'finance' },
  { name: 'HR', code: 'hr' },
];

const chartViewOptions = [
  { name: 'Monthly', value: 'monthly' },
  { name: 'Quarterly', value: 'quarterly' },
  { name: 'Yearly', value: 'yearly' },
];

const forecastSummary = ref({
  total: 1250000,
  budget: 1000000,
  variance: 250000,
  variancePercentage: 25,
  lastUpdated: new Date(),
});

const forecastChartData = ref({
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  datasets: [
    {
      label: 'Forecast',
      backgroundColor: '#42A5F5',
      data: [100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000]
    },
    {
      label: 'Actual',
      backgroundColor: '#66BB6A',
      data: [95000, 105000, 98000, 102000, 110000, 95000, 100000, 98000, 105000, 95000, 0, 0]
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
    },
    legend: {
      position: 'top',
    }
  }
});

const statuses = [
  { name: 'On Track', code: 'ontrack' },
  { name: 'At Risk', code: 'atrisk' },
  { name: 'Off Track', code: 'offtrack' },
];

const forecastDetails = ref([
  { 
    id: 1, 
    category: 'Marketing Campaigns', 
    department: 'Marketing', 
    forecastAmount: 250000, 
    actualAmount: 275000, 
    variance: 25000, 
    variancePercentage: 10, 
    status: 'At Risk' 
  },
  { 
    id: 2, 
    category: 'Office Rent', 
    department: 'Operations', 
    forecastAmount: 300000, 
    actualAmount: 300000, 
    variance: 0, 
    variancePercentage: 0, 
    status: 'On Track' 
  },
  { 
    id: 3, 
    category: 'Salaries', 
    department: 'HR', 
    forecastAmount: 500000, 
    actualAmount: 480000, 
    variance: -20000, 
    variancePercentage: -4, 
    status: 'On Track' 
  },
  { 
    id: 4, 
    category: 'Software Subscriptions', 
    department: 'IT', 
    forecastAmount: 50000, 
    actualAmount: 60000, 
    variance: 10000, 
    variancePercentage: 20, 
    status: 'At Risk' 
  },
  { 
    id: 5, 
    category: 'Travel', 
    department: 'Sales', 
    forecastAmount: 150000, 
    actualAmount: 200000, 
    variance: 50000, 
    variancePercentage: 33, 
    status: 'Off Track' 
  },
]);

// Dialog and Form
const forecastDialog = ref(false);
const deleteForecastDialog = ref(false);
const submitted = ref(false);
const forecast = ref({});

// Filters
const filters = ref({
  'global': { value: null, matchMode: FilterMatchMode.CONTAINS },
  'category': { value: null, matchMode: FilterMatchMode.STARTS_WITH },
  'department': { value: null, matchMode: FilterMatchMode.EQUALS },
  'status': { value: null, matchMode: FilterMatchMode.EQUALS },
});

// Methods
const openNewForecastDialog = () => {
  forecast.value = {};
  submitted.value = false;
  forecastDialog.value = true;
};

const hideDialog = () => {
  forecastDialog.value = false;
  submitted.value = false;
};

const saveForecast = () => {
  submitted.value = true;
  
  if (forecast.value.name && forecast.value.scenario) {
    // Save logic here
    forecastDialog.value = false;
    forecast.value = {};
  }
};

const editForecast = (editForecast) => {
  forecast.value = { ...editForecast };
  forecastDialog.value = true;
};

const confirmDeleteForecast = (deleteForecast) => {
  forecast.value = deleteForecast;
  deleteForecastDialog.value = true;
};

const deleteForecast = () => {
  // Delete logic here
  deleteForecastDialog.value = false;
  forecast.value = {};
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'on track':
      return 'success';
    case 'at risk':
      return 'warning';
    case 'off track':
      return 'danger';
    default:
      return 'info';
  }
};

onMounted(() => {
  // Fetch forecast data from API
});
</script>

<style scoped>
.budget-forecasts {
  padding: 1rem;
}

:deep(.p-datatable) {
  font-size: 0.9rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f8f9fa;
  font-weight: 600;
}

.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

.p-column-filter {
  width: 100%;
}
</style>
