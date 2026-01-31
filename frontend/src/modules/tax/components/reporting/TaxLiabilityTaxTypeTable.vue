<template>
  <div class="tax-liability-tax-type">
    <DataTable 
      :value="items" 
      :loading="isLoading"
      :paginator="items.length > 10"
      :rows="10"
      :rowsPerPageOptions="[10, 25, 50]"
      :totalRecords="items.length"
      responsiveLayout="scroll"
      class="p-datatable-sm"
      :scrollable="true"
      scrollHeight="flex"
      dataKey="id"
    >
      <Column field="tax_type" header="Tax Type" :sortable="true">
        <template #body="{ data }">
          <div class="flex align-items-center">
            <div class="mr-3" :style="{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: getTaxTypeColor(data.tax_type) }"></div>
            <span class="font-medium">{{ formatTaxType(data.tax_type) }}</span>
          </div>
        </template>
      </Column>
      
      <Column field="jurisdiction_name" header="Jurisdiction" :sortable="true">
        <template #body="{ data }">
          <Tag :value="data.jurisdiction_name" severity="info" />
        </template>
      </Column>
      
      <Column field="taxable_amount" header="Taxable Amount" :sortable="true">
        <template #body="{ data }">
          <span class="text-900">{{ formatCurrency(data.taxable_amount, currency) }}</span>
        </template>
        <template #footer v-if="items.length > 0">
          <div class="font-bold">{{ formatCurrency(totalTaxableAmount, currency) }}</div>
        </template>
      </Column>
      
      <Column field="tax_amount" header="Tax Amount" :sortable="true">
        <template #body="{ data }">
          <span class="font-medium" :style="{ color: getTaxTypeColor(data.tax_type) }">
            {{ formatCurrency(data.tax_amount, currency) }}
          </span>
        </template>
        <template #footer v-if="items.length > 0">
          <div class="font-bold">{{ formatCurrency(totalTaxAmount, currency) }}</div>
        </template>
      </Column>
      
      <Column field="collected_amount" header="Collected" :sortable="true">
        <template #body="{ data }">
          <span :class="getAmountClass(data.collected_amount, true)">
            {{ formatCurrency(data.collected_amount, currency) }}
          </span>
        </template>
        <template #footer v-if="items.length > 0">
          <div :class="['font-bold', getAmountClass(totalCollected, true)]">
            {{ formatCurrency(totalCollected, currency) }}
          </div>
        </template>
      </Column>
      
      <Column field="owed_amount" header="Owed" :sortable="true">
        <template #body="{ data }">
          <span :class="getAmountClass(data.owed_amount)">
            {{ formatCurrency(data.owed_amount, currency) }}
          </span>
        </template>
        <template #footer v-if="items.length > 0">
          <div :class="['font-bold', getAmountClass(totalOwed)]">
            {{ formatCurrency(totalOwed, currency) }}
          </div>
        </template>
      </Column>
      
      <Column field="compliance_status" header="Status" :sortable="true">
        <template #body="{ data }">
          <Tag :value="formatStatus(data.compliance_status)" :severity="getStatusSeverity(data.compliance_status)" />
        </template>
      </Column>
      
      <Column header="Actions" style="width: 120px">
        <template #body="{ data }">
          <div class="flex gap-1">
            <Button 
              icon="pi pi-search" 
              class="p-button-text p-button-sm p-button-rounded" 
              @click="viewDetails(data)"
              v-tooltip.top="'View Details'"
            />
            <Button 
              icon="pi pi-chart-line" 
              class="p-button-text p-button-sm p-button-rounded p-button-success" 
              @click="viewTrends(data)"
              v-tooltip.top="'View Trends'"
            />
          </div>
        </template>
      </Column>
      
      <template #empty>
        <div class="p-4 text-center">
          <i class="pi pi-inbox text-4xl text-400 mb-3" />
          <p class="text-600">No records found</p>
        </div>
      </template>
      
      <template #loading>
        <div class="p-4 text-center">
          <i class="pi pi-spin pi-spinner text-4xl text-400 mb-3" />
          <p class="text-600">Loading data...</p>
        </div>
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  currency: {
    type: String,
    default: 'USD'
  }
});

const emit = defineEmits(['view-details', 'view-trends']);

// Computed properties for totals
const totalTaxableAmount = computed(() => {
  return props.items.reduce((sum, item) => sum + (item.taxable_amount || 0), 0);
});

const totalTaxAmount = computed(() => {
  return props.items.reduce((sum, item) => sum + (item.tax_amount || 0), 0);
});

const totalCollected = computed(() => {
  return props.items.reduce((sum, item) => sum + (item.collected_amount || 0), 0);
});

const totalOwed = computed(() => {
  return props.items.reduce((sum, item) => sum + (item.owed_amount || 0), 0);
});

// Helper methods
const getAmountClass = (amount: number, isCollected = false) => {
  if (amount === 0) return 'text-500';
  if (isCollected) return 'text-green-500';
  return amount > 0 ? 'text-red-500' : 'text-green-500';
};

const formatTaxType = (taxType: string) => {
  // Format tax type for display
  if (!taxType) return '';
  return taxType
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

const getTaxTypeColor = (taxType: string) => {
  // Assign colors to tax types
  const colors: Record<string, string> = {
    vat: '#4CAF50',
    sales_tax: '#2196F3',
    gst: '#9C27B0',
    hst: '#FF9800',
    pst: '#F44336',
    default: '#607D8B'
  };
  
  return colors[taxType.toLowerCase()] || colors.default;
};

const formatStatus = (status: string) => {
  if (!status) return 'Unknown';
  return status
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

const getStatusSeverity = (status: string) => {
  const statuses: Record<string, string> = {
    compliant: 'success',
    non_compliant: 'danger',
    warning: 'warning',
    pending: 'info',
    overdue: 'danger',
    filed: 'success',
    not_filed: 'danger',
    in_progress: 'info',
    default: 'help'
  };
  
  return statuses[status.toLowerCase()] || statuses.default;
};

// Event handlers
const viewDetails = (item: any) => {
  emit('view-details', item);
};

const viewTrends = (item: any) => {
  emit('view-trends', item);
};
</script>

<style scoped>
.tax-liability-tax-type :deep(.p-datatable) {
  font-size: 0.9rem;
}

.tax-liability-tax-type :deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f8f9fa;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
  border: none;
  padding: 0.75rem 1rem;
}

.tax-liability-tax-type :deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.75rem 1rem;
  border: none;
  border-bottom: 1px solid #e9ecef;
}

.tax-liability-tax-type :deep(.p-datatable .p-datatable-tbody > tr:last-child > td) {
  border-bottom: none;
}

.tax-liability-tax-type :deep(.p-datatable .p-datatable-tbody > tr:hover > td) {
  background-color: #f8f9fa;
  cursor: pointer;
}

.tax-liability-tax-type :deep(.p-paginator) {
  border: none;
  background: transparent;
  padding: 1rem 0;
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .tax-liability-tax-type :deep(.p-datatable) {
    font-size: 0.85rem;
  }
  
  .tax-liability-tax-type :deep(.p-datatable .p-datatable-thead > tr > th),
  .tax-liability-tax-type :deep(.p-datatable .p-datatable-tbody > tr > td) {
    padding: 0.5rem;
  }
}
</style>
