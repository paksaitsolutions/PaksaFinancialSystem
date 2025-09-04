<template>
  <div class="test-layout-page">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">Layout Test Page</h1>
      <p class="page-subtitle">Testing the new layout system and styling</p>
    </div>

    <!-- KPI Cards Row -->
    <div class="grid">
      <div class="col-12 sm:col-6 lg:col-3">
        <Card>
          <template #title>Revenue</template>
          <template #content>
            <div class="metric-value">$125,430</div>
            <div class="metric-change text-success">+12.5%</div>
          </template>
        </Card>
      </div>
      <div class="col-12 sm:col-6 lg:col-3">
        <Card>
          <template #title>Expenses</template>
          <template #content>
            <div class="metric-value">$89,250</div>
            <div class="metric-change text-danger">+5.2%</div>
          </template>
        </Card>
      </div>
      <div class="col-12 sm:col-6 lg:col-3">
        <Card>
          <template #title>Profit</template>
          <template #content>
            <div class="metric-value">$36,180</div>
            <div class="metric-change text-success">+18.3%</div>
          </template>
        </Card>
      </div>
      <div class="col-12 sm:col-6 lg:col-3">
        <Card>
          <template #title>Cash Flow</template>
          <template #content>
            <div class="metric-value">$42,890</div>
            <div class="metric-change text-success">+8.7%</div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Data Table Section -->
    <div class="grid">
      <div class="col-12">
        <Card>
          <template #title>Sample Data Table</template>
          <template #content>
            <DataTable :value="sampleData" responsiveLayout="scroll">
              <Column field="id" header="ID" sortable></Column>
              <Column field="name" header="Name" sortable></Column>
              <Column field="amount" header="Amount" sortable>
                <template #body="slotProps">
                  {{ formatCurrency(slotProps.data.amount) }}
                </template>
              </Column>
              <Column field="status" header="Status">
                <template #body="slotProps">
                  <Badge 
                    :value="slotProps.data.status" 
                    :severity="getStatusSeverity(slotProps.data.status)"
                  />
                </template>
              </Column>
              <Column field="date" header="Date" sortable>
                <template #body="slotProps">
                  {{ formatDate(slotProps.data.date) }}
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <!-- Form Section -->
    <div class="grid">
      <div class="col-12 md:col-6">
        <Card>
          <template #title>Sample Form</template>
          <template #content>
            <div class="form-grid">
              <div class="field">
                <label for="name">Name</label>
                <InputText id="name" v-model="form.name" />
              </div>
              <div class="field">
                <label for="email">Email</label>
                <InputText id="email" v-model="form.email" type="email" />
              </div>
              <div class="field">
                <label for="amount">Amount</label>
                <InputNumber id="amount" v-model="form.amount" mode="currency" currency="USD" />
              </div>
              <div class="field">
                <label for="date">Date</label>
                <Calendar id="date" v-model="form.date" />
              </div>
              <div class="field">
                <label for="status">Status</label>
                <Dropdown 
                  id="status" 
                  v-model="form.status" 
                  :options="statusOptions" 
                  optionLabel="label" 
                  optionValue="value"
                />
              </div>
            </div>
            <div class="form-actions">
              <Button label="Save" icon="pi pi-check" class="p-button-primary" />
              <Button label="Cancel" icon="pi pi-times" class="p-button-secondary" />
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6">
        <Card>
          <template #title>Chart Example</template>
          <template #content>
            <div class="chart-placeholder">
              <i class="pi pi-chart-bar"></i>
              <p>Chart would go here</p>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Button Examples -->
    <div class="grid">
      <div class="col-12">
        <Card>
          <template #title>Button Examples</template>
          <template #content>
            <div class="button-showcase">
              <Button label="Primary" class="p-button-primary" />
              <Button label="Secondary" class="p-button-secondary" />
              <Button label="Success" class="p-button-success" />
              <Button label="Warning" class="p-button-warning" />
              <Button label="Danger" class="p-button-danger" />
              <Button label="Info" class="p-button-info" />
              <Button icon="pi pi-plus" class="p-button-rounded" />
              <Button label="Outlined" class="p-button-outlined" />
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const form = ref({
  name: '',
  email: '',
  amount: null,
  date: null,
  status: null
})

const statusOptions = ref([
  { label: 'Active', value: 'active' },
  { label: 'Pending', value: 'pending' },
  { label: 'Completed', value: 'completed' },
  { label: 'Cancelled', value: 'cancelled' }
])

const sampleData = ref([
  { id: 1, name: 'John Doe', amount: 1250.00, status: 'completed', date: '2024-01-15' },
  { id: 2, name: 'Jane Smith', amount: 2340.50, status: 'pending', date: '2024-01-16' },
  { id: 3, name: 'Bob Johnson', amount: 890.25, status: 'active', date: '2024-01-17' },
  { id: 4, name: 'Alice Brown', amount: 3450.75, status: 'completed', date: '2024-01-18' },
  { id: 5, name: 'Charlie Wilson', amount: 567.80, status: 'cancelled', date: '2024-01-19' }
])

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const formatDate = (value) => {
  return new Date(value).toLocaleDateString()
}

const getStatusSeverity = (status) => {
  switch (status) {
    case 'completed': return 'success'
    case 'pending': return 'warning'
    case 'active': return 'info'
    case 'cancelled': return 'danger'
    default: return 'secondary'
  }
}
</script>

<style scoped>
.test-layout-page {
  padding: 0;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: var(--spacing-2);
}

.metric-change {
  font-size: 0.875rem;
  font-weight: 600;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.field label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.875rem;
}

.form-actions {
  display: flex;
  gap: var(--spacing-3);
  margin-top: var(--spacing-6);
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  background: var(--surface-section);
  border-radius: var(--border-radius-md);
  color: var(--text-color-secondary);
}

.chart-placeholder i {
  font-size: 3rem;
  margin-bottom: var(--spacing-3);
}

.button-showcase {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-3);
  align-items: center;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .metric-value {
    font-size: 1.75rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .button-showcase {
    flex-direction: column;
    align-items: stretch;
  }
  
  .chart-placeholder {
    height: 150px;
  }
}
</style>