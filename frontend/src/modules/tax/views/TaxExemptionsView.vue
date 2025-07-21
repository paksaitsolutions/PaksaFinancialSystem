<template>
  <div class="tax-exemptions-view">
    <PageHeader
      title="Tax Exemptions Management"
      subtitle="Manage tax exemptions and certificates"
      :breadcrumbs="[
        { title: 'Finance', to: '/finance' },
        { title: 'Tax', to: '/finance/tax' },
        { title: 'Exemptions' }
      ]"
    >
      <template #actions>
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          :loading="loading"
          @click="showCreateDialog = true"
        >
          New Exemption
        </v-btn>
        <v-btn
          variant="tonal"
          class="ml-2"
          prepend-icon="mdi-cog"
          to="/finance/tax/policy"
          :disabled="loading"
        >
          Tax Rules
        </v-btn>
      </template>
    </PageHeader>

    <v-card class="mt-4">
      <v-card-text>
        <v-row class="mb-4">
          <v-col cols="12" sm="6" md="4">
            <v-text-field
              v-model="filters.search"
              label="Search exemptions"
              density="comfortable"
              variant="outlined"
              hide-details
              clearable
              :disabled="loading"
              prepend-inner-icon="mdi-magnify"
              @update:model-value="debouncedLoadTaxExemptions"
              @keyup.enter="loadTaxExemptions"
            />
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="filters.taxTypes"
              :items="availableTaxTypes"
              item-title="name"
              item-value="type"
              label="Tax Types"
              density="comfortable"
              variant="outlined"
              hide-details
              :disabled="loading"
              multiple
              chips
              clearable
              @update:model-value="loadTaxExemptions"
            >
              <template #selection="{ item, index }">
                <v-chip
                  v-if="index < 2"
                  size="small"
                  class="mr-2"
                  :color="getTaxTypeColor(item.raw.type)"
                >
                  {{ item.title }}
                </v-chip>
                <span
                  v-else-if="index === 2"
                  class="text-grey text-caption align-self-center"
                >
                  (+{{ filters.taxTypes ? filters.taxTypes.length - 2 : 0 }} more)
                </span>
              </template>
            </v-select>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="filters.countryCode"
              :items="countries"
              item-title="name"
              item-value="code"
              label="Country"
              density="comfortable"
              variant="outlined"
              hide-details
              :disabled="loading"
              clearable
              @update:model-value="onCountryChange"
            />
          </v-col>
          <v-col v-if="filters.countryCode" cols="12" sm="6" md="2">
            <v-select
              v-model="filters.stateCode"
              :items="states"
              item-title="name"
              item-value="code"
              label="State/Region"
              density="comfortable"
              variant="outlined"
              hide-details
              :disabled="loading"
              clearable
              @update:model-value="loadTaxExemptions"
            />
          </v-col>
        </v-row>

        <v-data-table
          :headers="headers"
          :items="exemptions"
          :items-per-page="pagination.itemsPerPage"
          :page="pagination.page"
          :items-length="totalItems"
          :loading="loading"
          :loading-text="loading ? 'Loading tax exemptions...' : 'No data available'"
          :footer-props="{
            'items-per-page-options': [10, 25, 50, 100],
            'show-current-page': true,
            'show-first-last-page': true
          }"
          class="elevation-1"
          @update:options="onTableOptionsChange"
        >
          <template #item.exemptionCode="{ item }">
            <v-tooltip location="top">
              <template #activator="{ props }">
                <span 
                  v-bind="props"
                  class="font-weight-medium d-inline-flex align-center"
                  :class="{ 'text-primary': isExemptionActive(item.raw) }"
                >
                  {{ item.raw.exemptionCode }}
                  <v-icon 
                    v-if="isExemptionActive(item.raw)" 
                    color="success" 
                    size="small" 
                    class="ml-1"
                  >
                    mdi-check-circle
                  </v-icon>
                </span>
              </template>
              <span>{{ isExemptionActive(item.raw) ? 'Active' : 'Inactive' }}</span>
            </v-tooltip>
          </template>

          <template #item.description="{ item }">
            <div class="d-flex align-center">
              <span>{{ item.raw.description }}</span>
              <v-tooltip v-if="item.raw.certificateRequired" text="Certificate required" location="top">
                <template #activator="{ props }">
                  <v-icon v-bind="props" size="small" class="ml-1" color="primary">mdi-file-certificate-outline</v-icon>
                </template>
              </v-tooltip>
            </div>
          </template>

          <template #item.taxTypes="{ item }">
            <div class="d-flex flex-wrap" style="gap: 4px">
              <v-chip
                v-for="(type, index) in item.raw.taxTypes"
                :key="index"
                size="x-small"
                :color="getTaxTypeColor(type)"
                class="text-uppercase"
                label
              >
                {{ formatTaxType(type) }}
              </v-chip>
            </div>
          </template>

          <template #item.validity="{ item }">
            <div class="d-flex flex-column">
              <div>{{ formatDate(item.raw.validFrom) }}</div>
              <div class="text-caption text-grey">
                {{ item.raw.validTo ? `to ${formatDate(item.raw.validTo)}` : 'No expiration' }}
              </div>
            </div>
          </template>

          <template #item.status="{ item }">
            <v-chip
              :color="isExemptionActive(item.raw) ? 'success' : 'error'"
              size="small"
              variant="tonal"
              :text="isExemptionActive(item.raw) ? 'Active' : 'Expired'"
            />
          </template>

          <template #item.actions="{ item }">
            <v-btn
              icon
              variant="text"
              size="small"
              color="primary"
              @click="editExemption(item.raw)"
            >
              <v-icon>mdi-pencil</v-icon>
              <v-tooltip activator="parent" location="top">Edit</v-tooltip>
            </v-btn>
            <v-btn
              icon
              variant="text"
              size="small"
              color="error"
              @click="confirmDelete(item.raw)"
            >
              <v-icon>mdi-delete</v-icon>
              <v-tooltip activator="parent" location="top">Delete</v-tooltip>
            </v-btn>
          </template>

          <template #no-data>
            <div class="py-4 text-center">
              <p>No tax exemptions found</p>
              <v-btn
                color="primary"
                variant="text"
                prepend-icon="mdi-plus"
                @click="showCreateDialog = true"
              >
                Create New Exemption
              </v-btn>
            </div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Create/Edit Dialog -->
    <TaxExemptionFormDialog
      v-model="showCreateDialog"
      :exemption="selectedExemption"
      :countries="countries"
      :states="states"
      :tax-types="availableTaxTypes"
      @saved="onExemptionSaved"
      @closed="onDialogClosed"
    />

    <!-- Delete Confirmation -->
    <ConfirmDialog
      v-model="showDeleteDialog"
      title="Delete Tax Exemption"
      :message="`Are you sure you want to delete the exemption '${selectedExemption?.exemptionCode}'?`"
      confirm-text="Delete"
      confirm-color="error"
      @confirm="deleteExemption"
    />
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { taxPolicyService } from '@/services/taxPolicyService';
import { debounce } from 'lodash-es';
import PageHeader from '@/components/layout/PageHeader.vue';
import ConfirmDialog from '@/components/common/ConfirmDialog.vue';
import TaxExemptionFormDialog from '@/components/tax/TaxExemptionFormDialog.vue';
import type { TaxExemption } from '@/types/tax';

const router = useRouter();
const toast = useToast();

// State
const exemptions = ref<TaxExemption[]>([]);
const loading = ref(false);
const showCreateDialog = ref(false);
const showDeleteDialog = ref(false);
const selectedExemption = ref<TaxExemption | null>(null);
const deletingId = ref<string | null>(null);

// Filter state
const filters = ref({
  search: '',
  taxTypes: [] as string[],
  countryCode: null as string | null,
  stateCode: null as string | null,
  isActive: true as boolean | null
});

// Pagination state
const pagination = ref({
  page: 1,
  itemsPerPage: 10,
  totalItems: 0,
  sortBy: 'createdAt',
  descending: true
});

// Countries and states data - consider moving to a shared constants file
const countries = ref([
  { code: 'US', name: 'United States' },
  { code: 'CA', name: 'Canada' },
  { code: 'GB', name: 'United Kingdom' },
  { code: 'PK', name: 'Pakistan' },
  { code: 'SA', name: 'Saudi Arabia' },
  { code: 'AE', name: 'United Arab Emirates' },
  { code: 'IN', name: 'India' },
  { code: 'CN', name: 'China' },
  { code: 'JP', name: 'Japan' },
  { code: 'KR', name: 'South Korea' },
  { code: 'FR', name: 'France' },
  { code: 'DE', name: 'Germany' },
  { code: 'IT', name: 'Italy' },
  { code: 'ES', name: 'Spain' }
]);

// US States as an example - consider a more comprehensive solution
const usStates = [
  { code: 'AL', name: 'Alabama' }, { code: 'AK', name: 'Alaska' }, { code: 'AZ', name: 'Arizona' },
  { code: 'AR', name: 'Arkansas' }, { code: 'CA', name: 'California' }, { code: 'CO', name: 'Colorado' },
  // Add more states as needed
];

const states = ref<Array<{code: string; name: string}>>([]);

const availableTaxTypes = ref([
  { type: 'sales', name: 'Sales Tax' },
  { type: 'vat', name: 'VAT' },
  { type: 'gst', name: 'GST' },
  { type: 'withholding', name: 'Withholding Tax' },
  { type: 'income', name: 'Income Tax' },
  { type: 'excise', name: 'Excise Tax' },
  { type: 'custom', name: 'Custom Tax' }
]);

const headers = [
  { 
    title: 'Exemption Code', 
    key: 'exemptionCode', 
    sortable: true,
    width: '15%'
  },
  { 
    title: 'Description', 
    key: 'description', 
    sortable: true,
    width: '25%'
  },
  { 
    title: 'Tax Types', 
    key: 'taxTypes', 
    sortable: false,
    width: '20%'
  },
  { 
    title: 'Valid From', 
    key: 'validFrom', 
    sortable: true,
    width: '10%'
  },
  { 
    title: 'Valid To', 
    key: 'validTo', 
    sortable: true,
    width: '10%'
  },
  { 
    title: 'Status', 
    key: 'status', 
    sortable: true,
    width: '10%',
    align: 'center'
  },
  { 
    title: 'Actions', 
    key: 'actions', 
    sortable: false, 
    align: 'end',
    width: '10%'
  }
];

// Debounced search
const debouncedLoadTaxExemptions = debounce(loadTaxExemptions, 500);

// Computed
const isExemptionActive = (exemption: TaxExemption): boolean => {
  if (!exemption) return false;
  const today = new Date();
  const validFrom = new Date(exemption.validFrom);
  const validTo = exemption.validTo ? new Date(exemption.validTo) : null;
  
  return validFrom <= today && (!validTo || validTo >= today);
};

// Format tax types for display
const formatTaxTypes = (types: string[]): string => {
  if (!types || types.length === 0) return '—';
  return types.map(type => {
    const found = availableTaxTypes.value.find(t => t.type === type);
    return found ? found.name : type;
  }).join(', ');
};

// Utility functions
const utils = {
  getTaxTypeColor: (type: string): string => {
    const colors: Record<string, string> = {
      sales: 'blue',
      vat: 'indigo',
      gst: 'teal',
      withholding: 'orange',
      income: 'purple',
      excise: 'red',
      custom: 'brown'
    };
    return colors[type] || 'grey';
  },
  formatDate: (dateString: string): string => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch (e) {
      console.error('Error formatting date:', e);
      return 'Invalid date';
    }
  },
  getStatusText: (exemption: TaxExemption): string => {
    if (!isExemptionActive(exemption)) return 'Inactive';
    if (exemption.validTo) {
      const daysLeft = Math.ceil((new Date(exemption.validTo).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
      if (daysLeft <= 7) return 'Expiring';
    }
    return 'Active';
  },
  getStatusColor: (exemption: TaxExemption): string => {
    if (!isExemptionActive(exemption)) return 'grey';
    if (exemption.validTo) {
      const daysLeft = Math.ceil((new Date(exemption.validTo).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
      if (daysLeft <= 7) return 'orange';
    }
    return 'success';
  }
};

// Load tax exemptions with proper typing
const loadTaxExemptions = debounce(async () => {
  try {
    loading.value = true;
    
    // Build query parameters
    const params: Record<string, any> = {
      page: pagination.value.page,
      limit: pagination.value.itemsPerPage,
      sortBy: pagination.value.sortBy,
      sortOrder: pagination.value.descending ? 'desc' : 'asc',
      ...(filters.value.search && { search: filters.value.search }),
      ...(filters.value.taxTypes?.length && { taxTypes: filters.value.taxTypes }),
      ...(filters.value.countryCode && { countryCode: filters.value.countryCode }),
      ...(filters.value.stateCode && { stateCode: filters.value.stateCode }),
    };

    // Only include isActive in params if it's not null
    if (filters.value.isActive !== null) {
      params.isActive = filters.value.isActive;
    }

    // Make API call
    const response = await taxPolicyService.getTaxExemptions(params);
    
    // Update state with response data
    exemptions.value = response.data || [];
    pagination.value.totalItems = response.meta?.total || 0;
  } catch (error) {
    console.error('Error loading tax exemptions:', error);
    toast.error('Failed to load tax exemptions. Please try again.');
  } finally {
    loading.value = false;
  }
}, 300);

const onCountryChange = (countryCode: string | null) => {
  // Reset state when country changes
  filters.value.stateCode = null;
  
  // Load states for the selected country
  if (countryCode === 'US') {
    states.value = usStates;
  } else if (countryCode === 'CA') {
    states.value = [
      { code: 'ON', name: 'Ontario' },
      { code: 'QC', name: 'Quebec' },
      { code: 'BC', name: 'British Columbia' },
      { code: 'AB', name: 'Alberta' },
      { code: 'MB', name: 'Manitoba' }
    ];
  } else if (countryCode === 'GB') {
    states.value = [
      { code: 'ENG', name: 'England' },
      { code: 'SCT', name: 'Scotland' },
      { code: 'WLS', name: 'Wales' },
      { code: 'NIR', name: 'Northern Ireland' }
    ];
  } else {
    states.value = [];
  }
  
  loadTaxExemptions();
};

const onTableOptionsChange = (options: any) => {
  if (options.page !== undefined) pagination.value.page = options.page;
  if (options.itemsPerPage !== undefined) pagination.value.itemsPerPage = options.itemsPerPage;
  
  if (options.sortBy?.length) {
    pagination.value.sortBy = options.sortBy[0].key;
    pagination.value.descending = options.sortDesc?.[0] ?? false;
  }
  
  loadTaxExemptions();
};

const editExemption = (exemption: TaxExemption) => {
  selectedExemption.value = { ...exemption };
  showCreateDialog.value = true;
};

const confirmDelete = (exemption: TaxExemption) => {
  selectedExemption.value = exemption;
  showDeleteDialog.value = true;
};

const deleteExemption = async () => {
  if (!selectedExemption.value) return;
  
  try {
    deletingId.value = selectedExemption.value.id;
    await taxPolicyService.deleteTaxExemption(selectedExemption.value.id);
    
    toast.success('Tax exemption deleted successfully');
    await loadTaxExemptions();
    showDeleteDialog.value = false;
    selectedExemption.value = null;
  } catch (error) {
    console.error('Error deleting tax exemption:', error);
    toast.error('Failed to delete tax exemption. Please try again.');
  } finally {
    deletingId.value = null;
  }
};

const onExemptionSaved = (savedExemption: TaxExemption) => {
  toast.success(`Tax exemption "${savedExemption.exemptionCode}" saved successfully`);
  loadTaxExemptions();
};

const onDialogClosed = () => {
  selectedExemption.value = null;
};

// Watch for filter changes with debouncing
const debouncedFilterChange = debounce(() => {
  pagination.value.page = 1; // Reset to first page when filters change
  loadTaxExemptions();
}, 500);

watch(
  () => [
    filters.value.search,
    filters.value.taxTypes,
    filters.value.countryCode,
    filters.value.stateCode,
    filters.value.isActive
  ],
  () => {
    debouncedFilterChange();
  },
  { deep: true }
);

// Watch for pagination changes with debouncing
const debouncedPaginationChange = debounce(() => {
  if (!loading.value) {
    loadTaxExemptions();
  }
}, 300);

watch(
  [
    () => pagination.value.page,
    () => pagination.value.itemsPerPage,
    () => pagination.value.sortBy,
    () => pagination.value.descending
  ],
  () => {
    debouncedPaginationChange();
  },
  { immediate: true }
);

// Lifecycle hooks
onMounted(() => {
  loadTaxExemptions();
});

defineExpose({
  utils
});
</script>

<style scoped>
.tax-exemptions-view {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 16px;
}
</style>
