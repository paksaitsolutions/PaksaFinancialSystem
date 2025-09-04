<template>
  <div class="custom-report-builder">
    <Card>
      <template #title>Custom Report Builder</template>
      <template #content>
        <div class="grid">
          <!-- Report Configuration -->
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="reportName">Report Name</label>
              <InputText id="reportName" v-model="reportConfig.name" class="w-full" />
            </div>
            
            <div class="field">
              <label>Available Fields</label>
              <div class="available-fields">
                <div v-for="(fields, table) in availableFields" :key="table" class="field-group">
                  <h4>{{ formatTableName(table) }}</h4>
                  <div class="field-list">
                    <div 
                      v-for="field in fields" 
                      :key="`${table}.${field.column}`"
                      class="field-item"
                      draggable="true"
                      @dragstart="onDragStart($event, table, field)"
                    >
                      <i class="pi pi-grip-vertical"></i>
                      {{ field.label }}
                      <small>({{ field.type }})</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Report Design Area -->
          <div class="col-12 md:col-6">
            <div class="field">
              <label>Selected Fields</label>
              <div 
                class="drop-zone"
                @drop="onDrop($event)"
                @dragover.prevent
                @dragenter.prevent
              >
                <div v-if="reportConfig.fields.length === 0" class="drop-placeholder">
                  Drag fields here to build your report
                </div>
                <div v-else class="selected-fields">
                  <div 
                    v-for="(field, index) in reportConfig.fields" 
                    :key="index"
                    class="selected-field"
                  >
                    <span>{{ field.label }}</span>
                    <Button 
                      icon="pi pi-times" 
                      class="p-button-text p-button-sm"
                      @click="removeField(index)"
                    />
                  </div>
                </div>
              </div>
            </div>
            
            <div class="field">
              <label>Filters</label>
              <div class="filters-section">
                <div v-for="(filter, index) in reportConfig.filters" :key="index" class="filter-row">
                  <Dropdown 
                    v-model="filter.field" 
                    :options="getFieldOptions()" 
                    optionLabel="label" 
                    optionValue="value"
                    placeholder="Select Field"
                    class="filter-field"
                  />
                  <Dropdown 
                    v-model="filter.operator" 
                    :options="operatorOptions" 
                    optionLabel="label" 
                    optionValue="value"
                    placeholder="Operator"
                    class="filter-operator"
                  />
                  <InputText 
                    v-model="filter.value" 
                    placeholder="Value"
                    class="filter-value"
                  />
                  <Button 
                    icon="pi pi-times" 
                    class="p-button-danger p-button-sm"
                    @click="removeFilter(index)"
                  />
                </div>
                <Button 
                  label="Add Filter" 
                  icon="pi pi-plus" 
                  class="p-button-sm"
                  @click="addFilter"
                />
              </div>
            </div>
          </div>
        </div>
        
        <!-- Actions -->
        <div class="actions">
          <Button 
            label="Preview Report" 
            icon="pi pi-eye" 
            class="p-button-secondary"
            @click="previewReport"
            :disabled="reportConfig.fields.length === 0"
          />
          <Button 
            label="Save Template" 
            icon="pi pi-save" 
            @click="saveTemplate"
            :disabled="!reportConfig.name || reportConfig.fields.length === 0"
          />
          <Button 
            label="Generate PDF" 
            icon="pi pi-file-pdf" 
            class="p-button-success"
            @click="generateReport('pdf')"
            :disabled="reportConfig.fields.length === 0"
          />
          <Button 
            label="Generate Excel" 
            icon="pi pi-file-excel" 
            class="p-button-success"
            @click="generateReport('excel')"
            :disabled="reportConfig.fields.length === 0"
          />
        </div>
      </template>
    </Card>
    
    <!-- Preview Dialog -->
    <Dialog v-model:visible="showPreview" header="Report Preview" :style="{width: '80vw'}" maximizable>
      <DataTable :value="previewData" :paginator="true" :rows="10" class="p-datatable-sm">
        <Column 
          v-for="field in reportConfig.fields" 
          :key="field.alias"
          :field="field.alias" 
          :header="field.label"
        />
      </DataTable>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const availableFields = ref({
  chart_of_accounts: [
    { column: 'account_code', label: 'Account Code', type: 'string' },
    { column: 'account_name', label: 'Account Name', type: 'string' },
    { column: 'account_type', label: 'Account Type', type: 'string' },
    { column: 'current_balance', label: 'Current Balance', type: 'decimal' }
  ],
  vendors: [
    { column: 'vendor_code', label: 'Vendor Code', type: 'string' },
    { column: 'vendor_name', label: 'Vendor Name', type: 'string' },
    { column: 'current_balance', label: 'Balance', type: 'decimal' }
  ],
  customers: [
    { column: 'customer_code', label: 'Customer Code', type: 'string' },
    { column: 'customer_name', label: 'Customer Name', type: 'string' },
    { column: 'current_balance', label: 'Balance', type: 'decimal' }
  ]
})

const reportConfig = ref({
  name: '',
  fields: [],
  filters: []
})

const showPreview = ref(false)
const previewData = ref([])

const operatorOptions = [
  { label: 'Equals', value: '=' },
  { label: 'Not Equals', value: '!=' },
  { label: 'Greater Than', value: '>' },
  { label: 'Less Than', value: '<' },
  { label: 'Contains', value: 'LIKE' }
]

const formatTableName = (tableName) => {
  return tableName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const onDragStart = (event, table, field) => {
  event.dataTransfer.setData('application/json', JSON.stringify({
    table,
    column: field.column,
    label: field.label,
    type: field.type,
    alias: `${table}_${field.column}`
  }))
}

const onDrop = (event) => {
  event.preventDefault()
  const fieldData = JSON.parse(event.dataTransfer.getData('application/json'))
  
  const exists = reportConfig.value.fields.some(f => f.alias === fieldData.alias)
  if (!exists) {
    reportConfig.value.fields.push(fieldData)
  }
}

const removeField = (index) => {
  reportConfig.value.fields.splice(index, 1)
}

const addFilter = () => {
  reportConfig.value.filters.push({
    field: '',
    operator: '=',
    value: ''
  })
}

const removeFilter = (index) => {
  reportConfig.value.filters.splice(index, 1)
}

const getFieldOptions = () => {
  const options = []
  for (const [table, fields] of Object.entries(availableFields.value)) {
    for (const field of fields) {
      options.push({
        label: `${formatTableName(table)} - ${field.label}`,
        value: `${table}.${field.column}`
      })
    }
  }
  return options
}

const previewReport = () => {
  previewData.value = [
    { chart_of_accounts_account_code: '1000', chart_of_accounts_account_name: 'Cash', chart_of_accounts_current_balance: 50000 },
    { chart_of_accounts_account_code: '1200', chart_of_accounts_account_name: 'Accounts Receivable', chart_of_accounts_current_balance: 25000 }
  ]
  showPreview.value = true
}

const saveTemplate = () => {
  console.log('Saving template:', reportConfig.value)
}

const generateReport = (format) => {
  console.log(`Generating ${format} report:`, reportConfig.value)
}
</script>

<style scoped>
.custom-report-builder {
  padding: 1rem;
}

.available-fields {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 1rem;
}

.field-group {
  margin-bottom: 1rem;
}

.field-group h4 {
  margin: 0 0 0.5rem 0;
  color: #2196f3;
  font-size: 0.9rem;
  text-transform: uppercase;
}

.field-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.field-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: grab;
  transition: all 0.2s;
}

.field-item:hover {
  background: #e3f2fd;
  border-color: #2196f3;
}

.field-item small {
  color: #666;
  margin-left: auto;
}

.drop-zone {
  min-height: 200px;
  border: 2px dashed #ccc;
  border-radius: 6px;
  padding: 1rem;
  transition: all 0.2s;
}

.drop-zone:hover {
  border-color: #2196f3;
  background: #e3f2fd;
}

.drop-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  font-style: italic;
}

.selected-fields {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.selected-field {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem;
  background: #e3f2fd;
  border: 1px solid #2196f3;
  border-radius: 4px;
}

.filters-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.filter-field {
  flex: 2;
}

.filter-operator {
  flex: 1;
}

.filter-value {
  flex: 2;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}
</style>