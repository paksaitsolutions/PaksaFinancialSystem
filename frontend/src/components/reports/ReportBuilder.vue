<template>
  <div class="report-builder">
    <div class="grid">
      <div class="col-12 md:col-8">
        <div class="card p-4">
          <h3 class="mt-0">Report Details</h3>
          
          <div class="field grid">
            <label for="reportName" class="col-12 mb-2">
              Report Name <span class="text-red-500">*</span>
            </label>
            <div class="col-12">
              <InputText 
                id="reportName" 
                v-model="report.name" 
                class="w-full"
                placeholder="Enter report name"
              />
              <small class="text-500">A descriptive name for your report</small>
            </div>
          </div>
          
          <div class="field grid">
            <label for="reportDescription" class="col-12 mb-2">
              Description
            </label>
            <div class="col-12">
              <Textarea 
                id="reportDescription" 
                v-model="report.description" 
                :autoResize="true" 
                rows="3" 
                class="w-full"
                placeholder="Enter a description for this report"
              />
            </div>
          </div>
          
          <div class="field grid">
            <label class="col-12 mb-2">Report Type</label>
            <div class="col-12">
              <div class="flex flex-wrap gap-3">
                <div v-for="type in reportTypes" :key="type.value" class="flex align-items-center">
                  <RadioButton 
                    :id="type.value" 
                    v-model="report.type" 
                    :value="type.value" 
                    name="reportType"
                  />
                  <label :for="type.value" class="ml-2">{{ type.name }}</label>
                </div>
              </div>
            </div>
          </div>
          
          <div class="field grid">
            <label for="reportCategory" class="col-12 mb-2">Category</label>
            <div class="col-12">
              <Dropdown 
                id="reportCategory"
                v-model="report.category"
                :options="reportCategories"
                optionLabel="name"
                optionValue="id"
                placeholder="Select a category"
                class="w-full"
              />
            </div>
          </div>
          
          <Divider />
          
          <h4>Data Source</h4>
          <div class="field grid">
            <div class="col-12">
              <div class="flex flex-column gap-2">
                <div v-for="source in dataSources" :key="source.id" class="flex align-items-center">
                  <RadioButton 
                    :id="source.id" 
                    v-model="report.dataSource" 
                    :value="source.id" 
                    name="dataSource"
                  />
                  <label :for="source.id" class="ml-2">
                    <div class="font-medium">{{ source.name }}</div>
                    <small class="text-500">{{ source.description }}</small>
                  </label>
                </div>
              </div>
            </div>
          </div>
          
          <Divider />
          
          <h4>Filters</h4>
          <div class="filters">
            <div v-for="(filter, index) in report.filters" :key="index" class="filter-item mb-3 p-3 border-round border-1 border-200">
              <div class="flex justify-content-between align-items-center mb-2">
                <span class="font-medium">Filter {{ index + 1 }}</span>
                <Button 
                  icon="pi pi-times" 
                  class="p-button-text p-button-sm p-button-rounded p-button-danger"
                  @click="removeFilter(index)"
                />
              </div>
              <div class="grid">
                <div class="col-12 md:col-5">
                  <label class="block mb-2">Field</label>
                  <Dropdown 
                    v-model="filter.field"
                    :options="filterFields"
                    optionLabel="name"
                    optionValue="id"
                    placeholder="Select field"
                    class="w-full"
                  />
                </div>
                <div class="col-12 md:col-3">
                  <label class="block mb-2">Operator</label>
                  <Dropdown 
                    v-model="filter.operator"
                    :options="filterOperators"
                    optionLabel="name"
                    optionValue="value"
                    class="w-full"
                  />
                </div>
                <div class="col-12 md:col-4">
                  <label class="block mb-2">Value</label>
                  <InputText 
                    v-model="filter.value" 
                    class="w-full"
                    placeholder="Enter value"
                  />
                </div>
              </div>
            </div>
            
            <Button 
              icon="pi pi-plus" 
              label="Add Filter" 
              class="p-button-text"
              @click="addFilter"
            />
          </div>
          
          <Divider />
          
          <h4>Columns</h4>
          <DataTable 
            :value="report.columns" 
            class="p-datatable-sm" 
            :scrollable="true"
            scrollHeight="200px"
          >
            <Column field="field" header="Field" :sortable="true">
              <template #body="{ data }">
                <Dropdown 
                  v-model="data.field"
                  :options="availableColumns"
                  optionLabel="name"
                  optionValue="id"
                  placeholder="Select field"
                  class="w-full"
                />
              </template>
            </Column>
            <Column field="header" header="Header" :sortable="true">
              <template #body="{ data }">
                <InputText v-model="data.header" class="w-full" />
              </template>
            </Column>
            <Column field="width" header="Width" style="width: 100px">
              <template #body="{ data }">
                <InputNumber v-model="data.width" mode="decimal" :min="50" :max="500" class="w-full" />
              </template>
            </Column>
            <Column header="Actions" style="width: 80px">
              <template #body="{ index }">
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-danger p-button-sm"
                  @click="removeColumn(index)"
                />
              </template>
            </Column>
            <template #footer>
              <div class="p-2">
                <Button 
                  icon="pi pi-plus" 
                  label="Add Column" 
                  class="p-button-text p-button-sm"
                  @click="addColumn"
                />
              </div>
            </template>
          </DataTable>
          
          <Divider />
          
          <h4>Sorting</h4>
          <div class="sorting">
            <div v-for="(sort, index) in report.sorting" :key="index" class="sort-item mb-3 p-3 border-round border-1 border-200">
              <div class="flex justify-content-between align-items-center mb-2">
                <span class="font-medium">Sort {{ index + 1 }}</span>
                <Button 
                  icon="pi pi-times" 
                  class="p-button-text p-button-sm p-button-rounded p-button-danger"
                  @click="removeSort(index)"
                />
              </div>
              <div class="grid">
                <div class="col-12 md:col-8">
                  <label class="block mb-2">Field</label>
                  <Dropdown 
                    v-model="sort.field"
                    :options="availableColumns"
                    optionLabel="name"
                    optionValue="id"
                    placeholder="Select field to sort"
                    class="w-full"
                  />
                </div>
                <div class="col-12 md:col-4">
                  <label class="block mb-2">Direction</label>
                  <Dropdown 
                    v-model="sort.direction"
                    :options="sortDirections"
                    optionLabel="name"
                    optionValue="value"
                    class="w-full"
                  />
                </div>
              </div>
            </div>
            
            <Button 
              icon="pi pi-plus" 
              label="Add Sort" 
              class="p-button-text"
              @click="addSort"
            />
          </div>
        </div>
      </div>
      
      <div class="col-12 md:col-4">
        <div class="sticky-sidebar">
          <div class="card p-4 mb-4">
            <h3 class="mt-0">Preview</h3>
            <div class="preview-container p-3 border-round border-1 border-200" style="min-height: 200px;">
              <div class="text-center text-500">
                <i class="pi pi-eye text-4xl mb-2"></i>
                <p>Report preview will appear here</p>
              </div>
            </div>
            
            <div class="flex flex-column gap-3 mt-4">
              <div class="flex align-items-center justify-content-between">
                <span>Columns</span>
                <Tag :value="report.columns.length" />
              </div>
              <div class="flex align-items-center justify-content-between">
                <span>Filters</span>
                <Tag :value="report.filters.length" />
              </div>
              <div class="flex align-items-center justify-content-between">
                <span>Sorting</span>
                <Tag :value="report.sorting.length" />
              </div>
            </div>
          </div>
          
          <div class="card p-4">
            <h4>Settings</h4>
            
            <div class="field-checkbox mb-3">
              <Checkbox 
                id="showGridLines" 
                v-model="report.settings.showGridLines" 
                :binary="true"
              />
              <label for="showGridLines" class="ml-2">Show grid lines</label>
            </div>
            
            <div class="field-checkbox mb-3">
              <Checkbox 
                id="showRowNumbers" 
                v-model="report.settings.showRowNumbers" 
                :binary="true"
              />
              <label for="showRowNumbers" class="ml-2">Show row numbers</label>
            </div>
            
            <div class="field-checkbox mb-3">
              <Checkbox 
                id="allowExport" 
                v-model="report.settings.allowExport" 
                :binary="true"
              />
              <label for="allowExport" class="ml-2">Allow export</label>
            </div>
            
            <div class="field-checkbox mb-3">
              <Checkbox 
                id="allowPrint" 
                v-model="report.settings.allowPrint" 
                :binary="true"
              />
              <label for="allowPrint" class="ml-2">Allow print</label>
            </div>
            
            <div class="field">
              <label for="rowsPerPage" class="block mb-2">Rows per page</label>
              <InputNumber 
                id="rowsPerPage" 
                v-model="report.settings.rowsPerPage" 
                :min="10" 
                :max="1000" 
                :step="10"
                class="w-full"
              />
            </div>
          </div>
          
          <div class="flex justify-content-end gap-2 mt-4">
            <Button 
              label="Cancel" 
              class="p-button-text" 
              @click="$emit('close')"
            />
            <Button 
              label="Save as Draft" 
              class="p-button-outlined" 
              @click="saveDraft"
            />
            <Button 
              label="Save & Run" 
              icon="pi pi-play" 
              @click="saveAndRun"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'vue/usetoast';
import Button from 'vue/button';
import InputText from 'vue/inputtext';
import Textarea from 'vue/textarea';
import Dropdown from 'vue/dropdown';
import RadioButton from 'vue/radiobutton';
import Checkbox from 'vue/checkbox';
import InputNumber from 'vue/inputnumber';
import DataTable from 'vue/datatable';
import Column from 'vue/column';
import Divider from 'vue/divider';
import Tag from 'vue/tag';

const emit = defineEmits(['close']);
const toast = useToast();

// Report types
const reportTypes = [
  { name: 'Table', value: 'table' },
  { name: 'Chart', value: 'chart' },
  { name: 'Pivot Table', value: 'pivot' },
  { name: 'Summary', value: 'summary' },
];

// Report categories
const reportCategories = [
  { id: 'financial', name: 'Financial Statements' },
  { id: 'operational', name: 'Operational' },
  { id: 'sales', name: 'Sales' },
  { id: 'inventory', name: 'Inventory' },
  { id: 'payroll', name: 'Payroll' },
  { id: 'custom', name: 'Custom' },
];

// Data sources
const dataSources = [
  { 
    id: 'gl', 
    name: 'General Ledger', 
    description: 'Financial transactions and account balances' 
  },
  { 
    id: 'ap', 
    name: 'Accounts Payable', 
    description: 'Vendor invoices and payments' 
  },
  { 
    id: 'ar', 
    name: 'Accounts Receivable', 
    description: 'Customer invoices and payments' 
  },
  { 
    id: 'inventory', 
    name: 'Inventory', 
    description: 'Product stock levels and movements' 
  },
  { 
    id: 'sales', 
    name: 'Sales', 
    description: 'Customer orders and revenue' 
  },
];

// Available columns (dynamically loaded based on data source)
const availableColumns = ref([
  { id: 'date', name: 'Date', type: 'date' },
  { id: 'account', name: 'Account', type: 'string' },
  { id: 'description', name: 'Description', type: 'string' },
  { id: 'debit', name: 'Debit', type: 'currency' },
  { id: 'credit', name: 'Credit', type: 'currency' },
  { id: 'balance', name: 'Balance', type: 'currency' },
  { id: 'reference', name: 'Reference', type: 'string' },
  { id: 'status', name: 'Status', type: 'string' },
]);

// Filter fields
const filterFields = computed(() => {
  return availableColumns.value.map(col => ({
    id: col.id,
    name: col.name
  }));
});

// Filter operators
const filterOperators = [
  { name: 'Equals', value: 'equals' },
  { name: 'Not equals', value: 'notEquals' },
  { name: 'Contains', value: 'contains' },
  { name: 'Starts with', value: 'startsWith' },
  { name: 'Ends with', value: 'endsWith' },
  { name: 'Greater than', value: 'gt' },
  { name: 'Less than', value: 'lt' },
  { name: 'Between', value: 'between' },
];

// Sort directions
const sortDirections = [
  { name: 'Ascending', value: 'asc' },
  { name: 'Descending', value: 'desc' },
];

// Default report settings
const defaultReport = {
  id: '',
  name: '',
  description: '',
  type: 'table',
  category: 'financial',
  dataSource: 'gl',
  filters: [],
  columns: [],
  sorting: [],
  settings: {
    showGridLines: true,
    showRowNumbers: true,
    allowExport: true,
    allowPrint: true,
    rowsPerPage: 50,
  },
  created: new Date(),
  modified: new Date(),
};

// Current report being edited
const report = ref(JSON.parse(JSON.stringify(defaultReport)));

// Add a new filter
const addFilter = () => {
  report.value.filters.push({
    field: '',
    operator: 'equals',
    value: '',
    id: Date.now().toString(),
  });
};

// Remove a filter
const removeFilter = (index: number) => {
  report.value.filters.splice(index, 1);
};

// Add a new column
const addColumn = () => {
  report.value.columns.push({
    field: '',
    header: '',
    width: 150,
    visible: true,
  });
};

// Remove a column
const removeColumn = (index: number) => {
  report.value.columns.splice(index, 1);
};

// Add a new sort
const addSort = () => {
  report.value.sorting.push({
    field: '',
    direction: 'asc',
  });
};

// Remove a sort
const removeSort = (index: number) => {
  report.value.sorting.splice(index, 1);
};

// Save as draft
const saveDraft = () => {
  // In a real app, this would save to a database
  console.log('Saving as draft:', report.value);
  
  toast.add({
    severity: 'success',
    summary: 'Draft Saved',
    detail: 'Your report has been saved as a draft.',
    life: 3000,
  });
  
  emit('close');
};

// Save and run the report
const saveAndRun = () => {
  // In a real app, this would save to a database and then run the report
  console.log('Saving and running:', report.value);
  
  toast.add({
    severity: 'success',
    summary: 'Report Generated',
    detail: 'Your report has been generated successfully.',
    life: 3000,
  });
  
  // In a real app, this would navigate to the report results
  // router.push({ name: 'ReportViewer', params: { id: report.value.id } });
  
  emit('close');
};

// Initialize with a default column if none exist
onMounted(() => {
  if (report.value.columns.length === 0) {
    addColumn();
  }
  
  // Add a default filter
  addFilter();
  
  // Add a default sort
  addSort();
});
</script>

<style scoped>
.sticky-sidebar {
  position: sticky;
  top: 1rem;
}

.preview-container {
  background-color: var(--surface-card);
  border: 1px dashed var(--surface-border);
}

.filter-item,
.sort-item {
  background-color: var(--surface-ground);
}

:deep(.p-datatable) {
  font-size: 0.875rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  padding: 0.5rem;
  font-weight: 600;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.5rem;
}
</style>
