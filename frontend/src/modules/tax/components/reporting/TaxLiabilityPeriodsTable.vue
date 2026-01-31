<template>
  <div class="tax-liability-periods">
    <DataTable 
      :value="periods" 
      :loading="isLoading"
      :paginator="periods.length > 10"
      :rows="10"
      :rowsPerPageOptions="[10, 25, 50]"
      :totalRecords="periods.length"
      responsiveLayout="scroll"
      class="p-datatable-sm"
      :scrollable="true"
      scrollHeight="flex"
      dataKey="id"
    >
      <Column field="period_name" header="Period" :sortable="true">
        <template #body="{ data }">
          <span class="font-medium">{{ data.period_name }}</span>
        </template>
      </Column>
      
      <Column field="tax_type" header="Tax Type" :sortable="true">
        <template #body="{ data }">
          <Tag :value="formatTaxType(data.tax_type)" :severity="getTaxTypeSeverity(data.tax_type)" />
        </template>
      </Column>
      
      <Column field="jurisdiction_code" header="Jurisdiction" :sortable="true">
        <template #body="{ data }">
          <span class="font-medium">{{ formatJurisdiction(data.jurisdiction_code) }}</span>
        </template>
      </Column>
      
      <Column field="taxable_amount" header="Taxable Amount" :sortable="true">
        <template #body="{ data }">
          <span class="text-900">{{ formatCurrency(data.taxable_amount, currency) }}</span>
        </template>
        <template #footer v-if="periods.length > 0">
          <div class="font-bold">{{ formatCurrency(totalTaxableAmount, currency) }}</div>
        </template>
      </Column>
      
      <Column field="tax_amount" header="Tax Amount" :sortable="true">
        <template #body="{ data }">
          <span class="text-900">{{ formatCurrency(data.tax_amount, currency) }}</span>
        </template>
        <template #footer v-if="periods.length > 0">
          <div class="font-bold">{{ formatCurrency(totalTaxAmount, currency) }}</div>
        </template>
      </Column>
      
      <Column field="collected_amount" header="Collected" :sortable="true">
        <template #body="{ data }">
          <span :class="getAmountClass(data.collected_amount, true)">
            {{ formatCurrency(data.collected_amount, currency) }}
          </span>
        </template>
        <template #footer v-if="periods.length > 0">
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
        <template #footer v-if="periods.length > 0">
          <div :class="['font-bold', getAmountClass(totalOwed)]">
            {{ formatCurrency(totalOwed, currency) }}
          </div>
        </template>
      </Column>
      
      <Column field="transactions_count" header="Transactions" :sortable="true">
        <template #body="{ data }">
          <Tag :value="data.transactions_count" severity="info" />
        </template>
        <template #footer v-if="periods.length > 0">
          <div class="font-bold">{{ totalTransactions }}</div>
        </template>
      </Column>
      
      <Column header="Actions" style="width: 100px">
        <template #body="{ data }">
          <div class="flex gap-1">
            <Button 
              icon="pi pi-search" 
              class="p-button-text p-button-sm p-button-rounded" 
              @click="viewTransactions(data)"
              v-tooltip.top="'View Transactions'"
            />
            <Button 
              icon="pi pi-file-pdf" 
              class="p-button-text p-button-sm p-button-rounded p-button-danger" 
              @click="exportPeriodReport(data, 'pdf')"
              v-tooltip.top="'Export PDF'"
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
  periods: {
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

const emit = defineEmits(['view-transactions', 'export-period']);

// Computed properties for totals
const totalTaxableAmount = computed(() => {
  return props.periods.reduce((sum, item) => sum + (item.taxable_amount || 0), 0);
});

const totalTaxAmount = computed(() => {
  return props.periods.reduce((sum, item) => sum + (item.tax_amount || 0), 0);
});

const totalCollected = computed(() => {
  return props.periods.reduce((sum, item) => sum + (item.collected_amount || 0), 0);
});

const totalOwed = computed(() => {
  return props.periods.reduce((sum, item) => sum + (item.owed_amount || 0), 0);
});

const totalTransactions = computed(() => {
  return props.periods.reduce((sum, item) => sum + (item.transactions_count || 0), 0);
});

// Helper methods
const getAmountClass = (amount: number, isCollected = false) => {
  if (amount === 0) return 'text-500';
  if (isCollected) return 'text-green-500';
  return amount > 0 ? 'text-red-500' : 'text-green-500';
};

const formatTaxType = (taxType: string) => {
  // Format tax type for display
  return taxType
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

const getTaxTypeSeverity = (taxType: string) => {
  // Assign severity based on tax type
  const types: Record<string, string> = {
    vat: 'success',
    sales_tax: 'info',
    gst: 'help',
    hst: 'warning',
    pst: 'danger'
  };
  
  return types[taxType.toLowerCase()] || 'info';
};

const formatJurisdiction = (code: string) => {
  // Format jurisdiction code for display
  if (!code) return '';
  
  // Map of jurisdiction codes to display names
  const jurisdictions: Record<string, string> = {
    'US': 'United States',
    'US-CA': 'California',
    'US-NY': 'New York',
    'US-TX': 'Texas',
    'CA': 'Canada',
    'CA-ON': 'Ontario',
    'CA-BC': 'British Columbia',
    'GB': 'United Kingdom',
    'AU': 'Australia',
    'EU': 'European Union'
  };
  
  return jurisdictions[code] || code;
};

// Event handlers
const viewTransactions = (period: any) => {
  emit('view-transactions', period);
};

const exportPeriodReport = (period: any, format: string) => {
  emit('export-period', { period, format });
};
</script>

<style scoped>
.tax-liability-periods :deep(.p-datatable) {
  font-size: 0.9rem;
}

.tax-liability-periods :deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f8f9fa;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
  border: none;
  padding: 0.75rem 1rem;
}

.tax-liability-periods :deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.75rem 1rem;
  border: none;
  border-bottom: 1px solid #e9ecef;
}

.tax-liability-periods :deep(.p-datatable .p-datatable-tbody > tr:last-child > td) {
  border-bottom: none;
}

.tax-liability-periods :deep(.p-datatable .p-datatable-tbody > tr:hover > td) {
  background-color: #f8f9fa;
  cursor: pointer;
}

.tax-liability-periods :deep(.p-paginator) {
  border: none;
  background: transparent;
  padding: 1rem 0;
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .tax-liability-periods :deep(.p-datatable) {
    font-size: 0.85rem;
  }
  
  .tax-liability-periods :deep(.p-datatable .p-datatable-thead > tr > th),
  .tax-liability-periods :deep(.p-datatable .p-datatable-tbody > tr > td) {
    padding: 0.5rem;
  }
}
</style>
