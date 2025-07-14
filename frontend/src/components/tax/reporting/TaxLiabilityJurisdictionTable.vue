<template>
  <div class="tax-liability-jurisdiction">
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
      <Column field="jurisdiction_name" header="Jurisdiction" :sortable="true">
        <template #body="{ data }">
          <div class="flex align-items-center">
            <i class="pi pi-map-marker mr-2" :style="{ color: getJurisdictionColor(data.jurisdiction_code) }"></i>
            <span class="font-medium">{{ data.jurisdiction_name }}</span>
            <Tag v-if="isCountry(data.jurisdiction_code)" value="Country" severity="success" class="ml-2" />
            <Tag v-else value="Region" severity="info" class="ml-2" />
          </div>
        </template>
      </Column>
      
      <Column field="tax_type" header="Tax Type" :sortable="true">
        <template #body="{ data }">
          <Tag :value="formatTaxType(data.tax_type)" :severity="getTaxTypeSeverity(data.tax_type)" />
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
      
      <Column field="filing_status" header="Filing Status" :sortable="true">
        <template #body="{ data }">
          <div class="flex align-items-center">
            <div 
              class="w-2 h-2 rounded-full mr-2" 
              :class="getStatusDotClass(data.filing_status)"
            ></div>
            <span>{{ formatFilingStatus(data.filing_status) }}</span>
          </div>
        </template>
      </Column>
      
      <Column header="Actions" style="width: 140px">
        <template #body="{ data }">
          <div class="flex gap-1">
            <Button 
              icon="pi pi-search" 
              class="p-button-text p-button-sm p-button-rounded" 
              @click="viewDetails(data)"
              v-tooltip.top="'View Details'"
            />
            <Button 
              icon="pi pi-calendar" 
              class="p-button-text p-button-sm p-button-rounded p-button-warning" 
              @click="viewFilingCalendar(data)"
              v-tooltip.top="'Filing Calendar'"
            />
            <Button 
              icon="pi pi-file-pdf" 
              class="p-button-text p-button-sm p-button-rounded p-button-danger" 
              @click="exportReport(data, 'pdf')"
              v-tooltip.top="'Export Report'"
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
import { formatCurrency } from '@/utils/formatters';

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

const emit = defineEmits(['view-details', 'view-filing-calendar', 'export-report']);

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
  if (!taxType) return '';
  return taxType
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

const getTaxTypeSeverity = (taxType: string) => {
  const types: Record<string, string> = {
    vat: 'success',
    sales_tax: 'info',
    gst: 'help',
    hst: 'warning',
    pst: 'danger'
  };
  
  return types[taxType.toLowerCase()] || 'info';
};

const getTaxTypeColor = (taxType: string) => {
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

const getJurisdictionColor = (code: string) => {
  if (!code) return '#607D8B';
  
  // Simple hash function to generate consistent colors
  let hash = 0;
  for (let i = 0; i < code.length; i++) {
    hash = code.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  const hue = Math.abs(hash) % 360;
  return `hsl(${hue}, 70%, 60%)`;
};

const isCountry = (code: string) => {
  if (!code) return false;
  return code.length === 2 || !code.includes('-');
};

const formatFilingStatus = (status: string) => {
  if (!status) return 'Not Filed';
  return status
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

const getStatusDotClass = (status: string) => {
  const statusClasses: Record<string, string> = {
    filed: 'bg-green-500',
    not_filed: 'bg-red-500',
    pending: 'bg-yellow-500',
    overdue: 'bg-pink-500',
    in_progress: 'bg-blue-500',
    extension_granted: 'bg-purple-500',
    payment_pending: 'bg-orange-500',
    default: 'bg-gray-500'
  };
  
  return statusClasses[status?.toLowerCase()] || statusClasses.default;
};

// Event handlers
const viewDetails = (item: any) => {
  emit('view-details', item);
};

const viewFilingCalendar = (item: any) => {
  emit('view-filing-calendar', item);
};

const exportReport = (item: any, format: string) => {
  emit('export-report', { item, format });
};
</script>

<style scoped>
.tax-liability-jurisdiction :deep(.p-datatable) {
  font-size: 0.9rem;
}

.tax-liability-jurisdiction :deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f8f9fa;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
  border: none;
  padding: 0.75rem 1rem;
}

.tax-liability-jurisdiction :deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.75rem 1rem;
  border: none;
  border-bottom: 1px solid #e9ecef;
}

.tax-liability-jurisdiction :deep(.p-datatable .p-datatable-tbody > tr:last-child > td) {
  border-bottom: none;
}

.tax-liability-jurisdiction :deep(.p-datatable .p-datatable-tbody > tr:hover > td) {
  background-color: #f8f9fa;
  cursor: pointer;
}

.tax-liability-jurisdiction :deep(.p-paginator) {
  border: none;
  background: transparent;
  padding: 1rem 0;
}

/* Status dot */
.w-2 { width: 0.5rem; }
.h-2 { height: 0.5rem; }
.rounded-full { border-radius: 9999px; }

/* Responsive adjustments */
@media (max-width: 960px) {
  .tax-liability-jurisdiction :deep(.p-datatable) {
    font-size: 0.85rem;
  }
  
  .tax-liability-jurisdiction :deep(.p-datatable .p-datatable-thead > tr > th),
  .tax-liability-jurisdiction :deep(.p-datatable .p-datatable-tbody > tr > td) {
    padding: 0.5rem;
  }
}
</style>
