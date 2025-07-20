<template>
  <div class="budget-scenarios">
    <PageHeader 
      title="Budget Scenarios" 
      subtitle="Manage different budget scenarios for planning and forecasting"
    >
      <template #actions>
        <Button 
          label="New Scenario" 
          icon="pi pi-plus" 
          class="p-button-outlined"
          @click="openNewScenarioDialog"
        />
      </template>
    </PageHeader>

    <!-- Scenario Cards -->
    <div class="grid">
      <div 
        v-for="scenario in scenarios" 
        :key="scenario.id"
        class="col-12 md:col-6 lg:col-4 xl:col-3"
      >
        <div class="scenario-card" :class="getScenarioCardClass(scenario)">
          <div class="flex justify-content-between align-items-center mb-3">
            <h3 class="m-0">{{ scenario.name }}</h3>
            <Tag 
              :value="scenario.status" 
              :severity="getStatusSeverity(scenario.status)" 
              class="status-tag"
            />
          </div>
          <p class="text-500 mt-0 mb-3">{{ scenario.description }}</p>
          
          <div class="scenario-stats">
            <div class="stat-item">
              <span class="stat-label">Budget</span>
              <span class="stat-value">{{ formatCurrency(scenario.budget) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Variance</span>
              <span 
                class="stat-value" 
                :class="scenario.variance >= 0 ? 'text-green-500' : 'text-red-500'"
              >
                {{ formatCurrency(scenario.variance) }}
              </span>
            </div>
          </div>
          
          <Divider class="my-3" />
          
          <div class="flex justify-content-between align-items-center">
            <span class="text-500 text-sm">
              <i class="pi pi-calendar mr-1"></i>
              {{ formatDate(scenario.startDate) }} - {{ formatDate(scenario.endDate) }}
            </span>
            <div>
              <Button 
                icon="pi pi-chart-line" 
                class="p-button-rounded p-button-text p-button-sm"
                @click="viewScenario(scenario)"
                v-tooltip.top="'View Details'"
              />
              <Button 
                icon="pi pi-pencil" 
                class="p-button-rounded p-button-text p-button-sm"
                @click="editScenario(scenario)"
                v-tooltip.top="'Edit'"
              />
              <Button 
                icon="pi pi-trash" 
                class="p-button-rounded p-button-text p-button-sm p-button-danger"
                @click="confirmDeleteScenario(scenario)"
                v-tooltip.top="'Delete'"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Scenario Details Dialog -->
    <Dialog 
      v-model:visible="scenarioDialog" 
      :style="{width: '800px'}" 
      :header="scenarioDialogTitle" 
      :modal="true"
      class="p-fluid"
    >
      <div v-if="selectedScenario" class="scenario-details">
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="name">Scenario Name</label>
              <InputText 
                id="name" 
                v-model="selectedScenario.name" 
                :disabled="!editing"
                :class="{'p-invalid': submitted && !selectedScenario.name}"
              />
              <small class="p-error" v-if="submitted && !selectedScenario.name">Name is required.</small>
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="status">Status</label>
              <Dropdown 
                id="status" 
                v-model="selectedScenario.status" 
                :options="statuses" 
                optionLabel="name"
                :disabled="!editing"
                class="w-full"
              />
            </div>
          </div>
          <div class="col-12">
            <div class="field">
              <label for="description">Description</label>
              <Textarea 
                id="description" 
                v-model="selectedScenario.description" 
                :autoResize="true" 
                rows="3"
                :disabled="!editing"
              />
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="startDate">Start Date</label>
              <Calendar 
                id="startDate" 
                v-model="selectedScenario.startDate" 
                :showIcon="true" 
                dateFormat="yy-mm-dd"
                :disabled="!editing"
                :class="{'p-invalid': submitted && !selectedScenario.startDate}"
              />
              <small class="p-error" v-if="submitted && !selectedScenario.startDate">Start date is required.</small>
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="endDate">End Date</label>
              <Calendar 
                id="endDate" 
                v-model="selectedScenario.endDate" 
                :showIcon="true" 
                dateFormat="yy-mm-dd"
                :disabled="!editing"
                :minDate="selectedScenario.startDate"
                :class="{'p-invalid': submitted && !selectedScenario.endDate}"
              />
              <small class="p-error" v-if="submitted && !selectedScenario.endDate">End date is required.</small>
            </div>
          </div>
          
          <div class="col-12">
            <h4>Budget Allocation</h4>
            <DataTable 
              :value="selectedScenario.categories" 
              :scrollable="true" 
              scrollHeight="200px"
              :loading="loading"
              class="p-datatable-sm"
            >
              <Column field="category" header="Category" sortable></Column>
              <Column field="allocated" header="Allocated" sortable>
                <template #body="{ data }">
                  <InputNumber 
                    v-model="data.allocated" 
                    mode="currency" 
                    currency="INR" 
                    locale="en-IN"
                    :disabled="!editing"
                  />
                </template>
              </Column>
              <Column field="actual" header="Actual" sortable>
                <template #body="{ data }">
                  {{ formatCurrency(data.actual) }}
                </template>
              </Column>
              <Column field="variance" header="Variance" sortable>
                <template #body="{ data }">
                  <span :class="getVarianceClass(data.variance)">
                    {{ formatCurrency(data.variance) }}
                  </span>
                </template>
              </Column>
              <Column field="variancePercentage" header="%" sortable>
                <template #body="{ data }">
                  <span :class="getVarianceClass(data.variance)">
                    {{ data.variancePercentage }}%
                  </span>
                </template>
              </Column>
            </DataTable>
          </div>
          
          <div class="col-12 mt-3">
            <div class="flex justify-content-between align-items-center">
              <div>
                <span class="text-500 font-medium mr-3">Total Budget:</span>
                <span class="font-bold">{{ formatCurrency(selectedScenario.budget) }}</span>
              </div>
              <div>
                <span class="text-500 font-medium mr-3">Total Variance:</span>
                <span 
                  class="font-bold" 
                  :class="selectedScenario.variance >= 0 ? 'text-green-500' : 'text-red-500'"
                >
                  {{ formatCurrency(selectedScenario.variance) }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <template #footer>
          <Button 
            v-if="!editing"
            label="Edit" 
            icon="pi pi-pencil" 
            class="p-button-text"
            @click="enableEditing"
          />
          <Button 
            v-else
            label="Cancel" 
            icon="pi pi-times" 
            class="p-button-text"
            @click="cancelEditing"
          />
          <Button 
            v-if="editing"
            label="Save" 
            icon="pi pi-check" 
            class="p-button-text"
            @click="saveScenario"
          />
        </template>
      </div>
    </Dialog>
    
    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="deleteScenarioDialog" 
      :style="{width: '450px'}" 
      header="Confirm" 
      :modal="true"
    >
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="selectedScenario">Are you sure you want to delete <b>{{selectedScenario.name}}</b>?</span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="deleteScenarioDialog = false"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-text" 
          @click="deleteScenario"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useFormatting } from '../../composables/useFormatting';
import PageHeader from '../../components/layout/PageHeader.vue';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Calendar from 'primevue/calendar';
import Dropdown from 'primevue/dropdown';
import Tag from 'primevue/tag';
import Divider from 'primevue/divider';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import InputNumber from 'primevue/inputnumber';
import { useRouter } from 'vue-router';

const { formatCurrency, formatDate } = useFormatting();
const router = useRouter();

// Data
const scenarios = ref([
  {
    id: 1,
    name: 'Best Case',
    description: 'Optimistic revenue projections with controlled expenses',
    status: 'Active',
    startDate: new Date(2023, 0, 1),
    endDate: new Date(2023, 11, 31),
    budget: 1500000,
    actual: 1350000,
    variance: -150000,
    categories: [
      { category: 'Marketing', allocated: 300000, actual: 320000, variance: 20000, variancePercentage: 6.7 },
      { category: 'Sales', allocated: 250000, actual: 230000, variance: -20000, variancePercentage: -8 },
      { category: 'Operations', allocated: 400000, actual: 380000, variance: -20000, variancePercentage: -5 },
      { category: 'R&D', allocated: 200000, actual: 180000, variance: -20000, variancePercentage: -10 },
      { category: 'HR', allocated: 250000, actual: 240000, variance: -10000, variancePercentage: -4 },
      { category: 'IT', allocated: 100000, actual: 95000, variance: -5000, variancePercentage: -5 },
    ]
  },
  {
    id: 2,
    name: 'Most Likely',
    description: 'Realistic projections based on historical data',
    status: 'Draft',
    startDate: new Date(2023, 0, 1),
    endDate: new Date(2023, 11, 31),
    budget: 1200000,
    actual: 1250000,
    variance: 50000,
    categories: [
      { category: 'Marketing', allocated: 250000, actual: 270000, variance: 20000, variancePercentage: 8 },
      { category: 'Sales', allocated: 200000, actual: 210000, variance: 10000, variancePercentage: 5 },
      { category: 'Operations', allocated: 350000, actual: 380000, variance: 30000, variancePercentage: 8.6 },
      { category: 'R&D', allocated: 150000, actual: 140000, variance: -10000, variancePercentage: -6.7 },
      { category: 'HR', allocated: 200000, actual: 190000, variance: -10000, variancePercentage: -5 },
      { category: 'IT', allocated: 100000, actual: 95000, variance: -5000, variancePercentage: -5 },
    ]
  },
  {
    id: 3,
    name: 'Worst Case',
    description: 'Conservative estimates with higher expense allocations',
    status: 'Inactive',
    startDate: new Date(2023, 0, 1),
    endDate: new Date(2023, 11, 31),
    budget: 1000000,
    actual: 1100000,
    variance: 100000,
    categories: [
      { category: 'Marketing', allocated: 200000, actual: 220000, variance: 20000, variancePercentage: 10 },
      { category: 'Sales', allocated: 150000, actual: 170000, variance: 20000, variancePercentage: 13.3 },
      { category: 'Operations', allocated: 300000, actual: 320000, variance: 20000, variancePercentage: 6.7 },
      { category: 'R&D', allocated: 100000, actual: 120000, variance: 20000, variancePercentage: 20 },
      { category: 'HR', allocated: 150000, actual: 160000, variance: 10000, variancePercentage: 6.7 },
      { category: 'IT', allocated: 100000, actual: 108000, variance: 8000, variancePercentage: 8 },
    ]
  },
  {
    id: 4,
    name: 'Q3 Growth',
    description: 'Focused on Q3 growth initiatives',
    status: 'Active',
    startDate: new Date(2023, 6, 1),
    endDate: new Date(2023, 8, 30),
    budget: 800000,
    actual: 720000,
    variance: -80000,
    categories: [
      { category: 'Marketing', allocated: 200000, actual: 180000, variance: -20000, variancePercentage: -10 },
      { category: 'Sales', allocated: 150000, actual: 140000, variance: -10000, variancePercentage: -6.7 },
      { category: 'Operations', allocated: 250000, actual: 220000, variance: -30000, variancePercentage: -12 },
      { category: 'R&D', allocated: 100000, actual: 90000, variance: -10000, variancePercentage: -10 },
      { category: 'HR', allocated: 100000, actual: 90000, variance: -10000, variancePercentage: -10 },
    ]
  },
]);

const statuses = [
  { name: 'Draft', code: 'draft' },
  { name: 'Active', code: 'active' },
  { name: 'Inactive', code: 'inactive' },
  { name: 'Archived', code: 'archived' },
];

// Dialog state
const scenarioDialog = ref(false);
const deleteScenarioDialog = ref(false);
const selectedScenario = ref(null);
const editing = ref(false);
const submitted = ref(false);
const loading = ref(false);

// Computed
const scenarioDialogTitle = computed(() => {
  return (selectedScenario.value && selectedScenario.value.id) ? 'Edit Scenario' : 'New Scenario';
});

// Methods
const openNewScenarioDialog = () => {
  selectedScenario.value = {
    id: null,
    name: '',
    description: '',
    status: 'Draft',
    startDate: new Date(),
    endDate: new Date(new Date().setFullYear(new Date().getFullYear() + 1)),
    budget: 0,
    actual: 0,
    variance: 0,
    categories: [
      { category: 'Marketing', allocated: 0, actual: 0, variance: 0, variancePercentage: 0 },
      { category: 'Sales', allocated: 0, actual: 0, variance: 0, variancePercentage: 0 },
      { category: 'Operations', allocated: 0, actual: 0, variance: 0, variancePercentage: 0 },
      { category: 'R&D', allocated: 0, actual: 0, variance: 0, variancePercentage: 0 },
      { category: 'HR', allocated: 0, actual: 0, variance: 0, variancePercentage: 0 },
      { category: 'IT', allocated: 0, actual: 0, variance: 0, variancePercentage: 0 },
    ]
  };
  
  editing.value = true;
  scenarioDialog.value = true;
};

const viewScenario = (scenario) => {
  selectedScenario.value = { ...scenario };
  editing.value = false;
  scenarioDialog.value = true;
};

const editScenario = (scenario) => {
  selectedScenario.value = { ...scenario };
  editing.value = true;
  scenarioDialog.value = true;
};

const enableEditing = () => {
  editing.value = true;
};

const cancelEditing = () => {
  editing.value = false;
  if (selectedScenario.value.id) {
    // Reset to original values
    const originalScenario = scenarios.value.find(s => s.id === selectedScenario.value.id);
    selectedScenario.value = { ...originalScenario };
  } else {
    scenarioDialog.value = false;
  }
};

const saveScenario = () => {
  submitted.value = true;
  
  if (!selectedScenario.value.name || !selectedScenario.value.startDate || !selectedScenario.value.endDate) {
    return; // Validation failed
  }
  
  // Calculate totals
  const totalAllocated = selectedScenario.value.categories.reduce((sum, cat) => sum + (cat.allocated || 0), 0);
  const totalActual = selectedScenario.value.categories.reduce((sum, cat) => sum + (cat.actual || 0), 0);
  
  selectedScenario.value.budget = totalAllocated;
  selectedScenario.value.actual = totalActual;
  selectedScenario.value.variance = totalActual - totalAllocated;
  
  // Update or add scenario
  if (selectedScenario.value.id) {
    const index = scenarios.value.findIndex(s => s.id === selectedScenario.value.id);
    if (index !== -1) {
      scenarios.value[index] = { ...selectedScenario.value };
    }
  } else {
    // Generate new ID (in a real app, this would be handled by the backend)
    const newId = Math.max(...scenarios.value.map(s => s.id), 0) + 1;
    selectedScenario.value.id = newId;
    scenarios.value.push({ ...selectedScenario.value });
  }
  
  scenarioDialog.value = false;
  selectedScenario.value = null;
};

const confirmDeleteScenario = (scenario) => {
  selectedScenario.value = scenario;
  deleteScenarioDialog.value = true;
};

const deleteScenario = () => {
  const index = scenarios.value.findIndex(s => s.id === selectedScenario.value.id);
  if (index !== -1) {
    scenarios.value.splice(index, 1);
  }
  deleteScenarioDialog.value = false;
  selectedScenario.value = null;
};

const getScenarioCardClass = (scenario) => {
  return {
    'scenario-card-active': scenario.status === 'Active',
    'scenario-card-draft': scenario.status === 'Draft',
    'scenario-card-inactive': scenario.status === 'Inactive',
  };
};

const getStatusSeverity = (status) => {
  switch (status) {
    case 'Active':
      return 'success';
    case 'Draft':
      return 'warning';
    case 'Inactive':
      return 'danger';
    default:
      return 'info';
  }
};

const getVarianceClass = (variance) => {
  return variance >= 0 ? 'text-green-500' : 'text-red-500';
};
</script>

<style scoped>
.budget-scenarios {
  padding: 1rem;
}

.scenario-card {
  border-radius: 6px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  border: 1px solid var(--surface-border);
  background-color: var(--surface-card);
}

.scenario-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.scenario-card-active {
  border-left: 4px solid var(--green-500);
}

.scenario-card-draft {
  border-left: 4px solid var(--yellow-500);
}

.scenario-card-inactive {
  border-left: 4px solid var(--red-500);
  opacity: 0.8;
}

.scenario-stats {
  display: flex;
  justify-content: space-between;
  margin: 1rem 0;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-label {
  display: block;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin-bottom: 0.25rem;
}

.stat-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 600;
}

.status-tag {
  margin-left: 0.5rem;
}

.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.p-datatable) {
  font-size: 0.9rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f8f9fa;
  font-weight: 600;
}
</style>
