<template>
  <div class="tax-policy-view">
    <PageHeader
      title="Tax Policy Management"
      subtitle="Manage tax rules, rates, and exemptions"
      :breadcrumbs="[
        { title: 'Finance', to: '/finance' },
        { title: 'Tax', to: '/finance/tax' },
        { title: 'Policy Management' }
      ]"
    >
      <template #actions>
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          @click="showCreateDialog = true"
        >
          New Tax Rule
        </v-btn>
        <v-btn
          variant="tonal"
          class="ml-2"
          prepend-icon="mdi-shield-account"
          to="/finance/tax/exemptions"
        >
          Manage Exemptions
        </v-btn>
      </template>
    </PageHeader>

    <v-card class="mt-4">
      <v-card-text>
        <v-row class="mb-4">
          <v-col cols="12" sm="6" md="4">
            <v-text-field
              v-model="filters.search"
              label="Search rules"
              density="comfortable"
              variant="outlined"
              hide-details
              clearable
              prepend-inner-icon="mdi-magnify"
              @update:model-value="loadTaxRules"
            />
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="filters.taxType"
              :items="taxTypes"
              item-title="name"
              item-value="type"
              label="Tax Type"
              density="comfortable"
              variant="outlined"
              hide-details
              clearable
              @update:model-value="loadTaxRules"
            />
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
              @update:model-value="loadTaxRules"
            />
          </v-col>
        </v-row>

        <v-data-table
          :headers="headers"
          :items="taxRules.items"
          :loading="loading"
          :items-per-page="filters.pageSize"
          :page="filters.page"
          :items-length="taxRules.total"
          :server-items-length="taxRules.total""
          @update:options="onTableOptionsChange"
        >
          <template #item.taxType="{ item }">
            <v-chip
              :color="getTaxTypeColor(item.raw.type)"
              size="small"
              class="text-uppercase"
              label
            >
              {{ formatTaxType(item.raw.type) }}
            </v-chip>
          </template>

          <template #item.jurisdiction="{ item }">
            {{ formatJurisdiction(item.raw.jurisdiction) }}
          </template>

          <template #item.rates="{ item }">
            <div v-for="(rate, index) in item.raw.rates" :key="index" class="d-flex align-center">
              <span class="font-weight-medium">{{ rate.rate }}%</span>
              <v-tooltip v-if="rate.description" :text="rate.description" location="top">
                <template #activator="{ props }">
                  <v-icon v-bind="props" size="small" class="ml-1">mdi-information-outline</v-icon>
                </template>
              </v-tooltip>
              <v-chip
                v-if="rate.isStandardRate"
                size="x-small"
                color="primary"
                class="ml-1"
                label
              >
                Standard
              </v-chip>
            </div>
          </template>

          <template #item.status="{ item }">
            <v-chip
              :color="item.raw.isActive ? 'success' : 'error'"
              size="small"
              variant="tonal"
            >
              {{ item.raw.isActive ? 'Active' : 'Inactive' }}
            </v-chip>
          </template>

          <template #item.actions="{ item }">
            <v-btn
              icon
              variant="text"
              size="small"
              color="primary"
              @click="editTaxRule(item.raw)"
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
              <p>No tax rules found</p>
              <v-btn
                color="primary"
                variant="text"
                prepend-icon="mdi-plus"
                @click="showCreateDialog = true"
              >
                Create New Rule
              </v-btn>
            </div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Create/Edit Dialog -->
    <TaxRuleFormDialog
      v-model="showCreateDialog"
      :tax-rule="editingRule"
      :countries="countries"
      :states="states"
      :tax-types="taxTypes"
      @saved="onTaxRuleSaved"
      @closed="onDialogClosed"
    />

    <!-- Delete Confirmation -->
    <ConfirmDialog
      v-model="showDeleteDialog"
      title="Delete Tax Rule"
      :message="`Are you sure you want to delete the tax rule '${deletingRule?.name}'?`"
      confirm-text="Delete"
      confirm-color="error"
      @confirm="deleteTaxRule"
    />
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { taxPolicyService } from '@/services/taxPolicyService';
import type { TaxRule, TaxType, TaxRuleFormData } from '@/types/tax';

const router = useRouter();
const toast = useToast();

// Data
const loading = ref(false);
const taxRules = ref<{ items: TaxRule[]; total: number }>({ items: [], total: 0 });
const filters = ref({
  search: '',
  taxType: undefined as TaxType | undefined,
  countryCode: '',
  stateCode: '',
  page: 1,
  pageSize: 10,
  sortBy: 'name',
  sortOrder: 'asc' as 'asc' | 'desc',
});

// Form dialogs
const showCreateDialog = ref(false);
const editingRule = ref<TaxRule | null>(null);
const showDeleteDialog = ref(false);
const deletingRule = ref<TaxRule | null>(null);

// Static data
const taxTypes = [
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
  { title: 'Code', key: 'code', sortable: true },
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Type', key: 'taxType', sortable: true },
  { title: 'Jurisdiction', key: 'jurisdiction', sortable: true },
  { title: 'Rates', key: 'rates', sortable: false },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' },
];

// Methods
const loadTaxRules = async () => {
  try {
    loading.value = true;
    const response = await taxPolicyService.getTaxRules({
      search: filters.value.search,
      taxType: filters.value.taxType,
      countryCode: filters.value.countryCode,
      stateCode: filters.value.stateCode,
      page: filters.value.page,
      pageSize: filters.value.pageSize,
      sortBy: filters.value.sortBy,
      sortOrder: filters.value.sortOrder,
    });
    taxRules.value = response;
  } catch (error) {
    console.error('Failed to load tax rules:', error);
    toast.error('Failed to load tax rules');
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
      // Add more states as needed
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
  
  await loadTaxRules();
};

const onTableOptionsChange = ({ page, itemsPerPage, sortBy }: any) => {
  filters.value.page = page;
  filters.value.pageSize = itemsPerPage;
  
  if (sortBy && sortBy.length > 0) {
    filters.value.sortBy = sortBy[0].key;
    filters.value.sortOrder = sortBy[0].order;
  }
  
  loadTaxRules();
};

const editTaxRule = (rule: TaxRule) => {
  editingRule.value = { ...rule };
  showCreateDialog.value = true;
};

const confirmDelete = (rule: TaxRule) => {
  deletingRule.value = rule;
  showDeleteDialog.value = true;
};

const deleteTaxRule = async () => {
  if (!deletingRule.value) return;
  
  try {
    await taxPolicyService.deleteTaxRule(deletingRule.value.id);
    toast.success('Tax rule deleted successfully');
    loadTaxRules();
  } catch (error) {
    console.error('Failed to delete tax rule:', error);
    toast.error('Failed to delete tax rule');
  } finally {
    showDeleteDialog.value = false;
    deletingRule.value = null;
  }
};

const onTaxRuleSaved = (savedRule: TaxRule) => {
  toast.success(`Tax rule "${savedRule.name}" saved successfully`);
  loadTaxRules();
};

const onDialogClosed = () => {
  editingRule.value = null;
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

const formatJurisdiction = (jurisdiction: any) => {
  let result = jurisdiction.countryCode;
  if (jurisdiction.stateCode) {
    result += `, ${jurisdiction.stateCode}`;
  }
  if (jurisdiction.city) {
    result += `, ${jurisdiction.city}`;
  }
  return result;
};

// Lifecycle hooks
onMounted(() => {
  loadTaxRules();
});
</script>

<style scoped>
.tax-policy-view {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 16px;
}
</style>
