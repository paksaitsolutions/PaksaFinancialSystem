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
          @click="showCreateDialog = true"
        >
          New Exemption
        </v-btn>
        <v-btn
          variant="tonal"
          class="ml-2"
          prepend-icon="mdi-cog"
          to="/finance/tax/policy"
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
              prepend-inner-icon="mdi-magnify"
              @update:model-value="loadTaxExemptions"
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
              clearable
              @update:model-value="loadTaxExemptions"
            />
          </v-col>
        </v-row>

        <v-data-table
          :headers="headers"
          :items="taxExemptions.items"
          :loading="loading"
          :items-per-page="filters.pageSize"
          :page="filters.page"
          :items-length="taxExemptions.total"
          :server-items-length="taxExemptions.total"
          @update:options="onTableOptionsChange"
        >
          <template #item.exemptionCode="{ item }">
            <span class="font-weight-medium">{{ item.raw.exemptionCode }}</span>
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
      :exemption="editingExemption"
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
      :message="`Are you sure you want to delete the exemption '${deletingExemption?.exemptionCode}'?`"
      confirm-text="Delete"
      confirm-color="error"
      @confirm="deleteExemption"
    />
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { VDataTable } from 'vuetify/labs/VDataTable';
import PageHeader from '@/components/layout/PageHeader.vue';
import ConfirmDialog from '@/components/common/ConfirmDialog.vue';
import TaxExemptionFormDialog from '@/components/tax/TaxExemptionFormDialog.vue';
import { taxPolicyService } from '@/services/taxPolicyService';
import type { TaxExemption, TaxType } from '@/types/tax';
import { format } from 'date-fns';

const router = useRouter();
const toast = useToast();

// Data
const loading = ref(false);
const taxExemptions = ref<{ items: TaxExemption[]; total: number }>({ items: [], total: 0 });
const filters = ref({
  search: '',
  taxTypes: [] as string[],
  countryCode: '',
  stateCode: '',
  page: 1,
  pageSize: 10,
  sortBy: 'exemptionCode',
  sortOrder: 'asc' as 'asc' | 'desc',
});

// Form dialogs
const showCreateDialog = ref(false);
const editingExemption = ref<TaxExemption | null>(null);
const showDeleteDialog = ref(false);
const deletingExemption = ref<TaxExemption | null>(null);

// Available tax types for filtering
const availableTaxTypes = [
  { type: 'sales', name: 'Sales Tax' },
  { type: 'vat', name: 'VAT' },
  { type: 'gst', name: 'GST' },
  { type: 'income', name: 'Income Tax' },
  { type: 'withholding', name: 'Withholding Tax' },
  { type: 'excise', name: 'Excise Tax' },
  { type: 'custom', name: 'Custom Tax' },
];

// TODO: Replace with actual country/state data from an API or i18n
const countries = [
  { code: 'US', name: 'United States' },
  { code: 'GB', name: 'United Kingdom' },
  { code: 'CA', name: 'Canada' },
  { code: 'AU', name: 'Australia' },
  { code: 'DE', name: 'Germany' },
  { code: 'FR', name: 'France' },
  { code: 'PK', name: 'Pakistan' },
  { code: 'SA', name: 'Saudi Arabia' },
  { code: 'AE', name: 'United Arab Emirates' },
];

const states = ref<{ code: string; name: string }[]>([]);

// Table headers
const headers = [
  { title: 'Exemption Code', key: 'exemptionCode', sortable: true },
  { title: 'Description', key: 'description', sortable: true },
  { title: 'Tax Types', key: 'taxTypes', sortable: false },
  { title: 'Certificate Required', key: 'certificateRequired', sortable: true, align: 'center' },
  { title: 'Validity', key: 'validity', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' },
];

// Computed
const isExemptionActive = (exemption: TaxExemption): boolean => {
  const now = new Date();
  const validFrom = new Date(exemption.validFrom);
  const validTo = exemption.validTo ? new Date(exemption.validTo) : null;
  
  return validFrom <= now && (!validTo || validTo >= now);
};

// Methods
const loadTaxExemptions = async () => {
  try {
    loading.value = true;
    const response = await taxPolicyService.getTaxExemptions({
      search: filters.value.search,
      taxTypes: filters.value.taxTypes,
      countryCode: filters.value.countryCode,
      stateCode: filters.value.stateCode,
      page: filters.value.page,
      pageSize: filters.value.pageSize,
      sortBy: filters.value.sortBy,
      sortOrder: filters.value.sortOrder,
    });
    taxExemptions.value = response;
  } catch (error) {
    console.error('Failed to load tax exemptions:', error);
    toast.error('Failed to load tax exemptions');
  } finally {
    loading.value = false;
  }
};

const onCountryChange = async (countryCode: string) => {
  // Reset state when country changes
  filters.value.stateCode = '';
  
  // Load states for the selected country
  // In a real app, this would be an API call
  if (countryCode === 'US') {
    states.value = [
      { code: 'CA', name: 'California' },
      { code: 'NY', name: 'New York' },
      { code: 'TX', name: 'Texas' },
    ];
  } else if (countryCode === 'CA') {
    states.value = [
      { code: 'ON', name: 'Ontario' },
      { code: 'QC', name: 'Quebec' },
      { code: 'BC', name: 'British Columbia' },
    ];
  } else {
    states.value = [];
  }
  
  await loadTaxExemptions();
};

const onTableOptionsChange = ({ page, itemsPerPage, sortBy }: any) => {
  filters.value.page = page;
  filters.value.pageSize = itemsPerPage;
  
  if (sortBy && sortBy.length > 0) {
    filters.value.sortBy = sortBy[0].key;
    filters.value.sortOrder = sortBy[0].order;
  }
  
  loadTaxExemptions();
};

const editExemption = (exemption: TaxExemption) => {
  editingExemption.value = { ...exemption };
  showCreateDialog.value = true;
};

const confirmDelete = (exemption: TaxExemption) => {
  deletingExemption.value = exemption;
  showDeleteDialog.value = true;
};

const deleteExemption = async () => {
  if (!deletingExemption.value) return;
  
  try {
    // TODO: Implement delete exemption in service
    // await taxPolicyService.deleteTaxExemption(deletingExemption.value.id);
    toast.success('Tax exemption deleted successfully');
    loadTaxExemptions();
  } catch (error) {
    console.error('Failed to delete tax exemption:', error);
    toast.error('Failed to delete tax exemption');
  } finally {
    showDeleteDialog.value = false;
    deletingExemption.value = null;
  }
};

const onExemptionSaved = (savedExemption: TaxExemption) => {
  toast.success(`Tax exemption "${savedExemption.exemptionCode}" saved successfully`);
  loadTaxExemptions();
};

const onDialogClosed = () => {
  editingExemption.value = null;
};

// Utility methods
const formatTaxType = (type: string) => {
  const typeMap: Record<string, string> = {
    sales: 'Sales Tax',
    vat: 'VAT',
    gst: 'GST',
    income: 'Income Tax',
    withholding: 'Withholding',
    excise: 'Excise Tax',
    custom: 'Custom',
  };
  return typeMap[type] || type;
};

const getTaxTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    sales: 'blue',
    vat: 'purple',
    gst: 'teal',
    income: 'orange',
    withholding: 'red',
    excise: 'deep-orange',
    custom: 'grey',
  };
  return colorMap[type] || 'grey';
};

const formatDate = (dateString: string) => {
  try {
    return format(new Date(dateString), 'MMM d, yyyy');
  } catch (error) {
    return 'Invalid date';
  }
};

// Lifecycle hooks
onMounted(() => {
  loadTaxExemptions();
});
</script>

<style scoped>
.tax-exemptions-view {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 16px;
}
</style>
