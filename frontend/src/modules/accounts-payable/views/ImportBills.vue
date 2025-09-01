<template>
  <div class="import-bills">
    <Card>
      <template #title>Import Bills</template>
      <template #content>
        <div class="import-section">
          <div class="upload-area">
            <FileUpload
              mode="basic"
              name="billsFile"
              :maxFileSize="1000000"
              accept=".csv,.xlsx,.xls"
              :customUpload="true"
              @uploader="handleFileUpload"
              :auto="true"
              chooseLabel="Choose File"
            />
            <p class="upload-help">
              Upload a CSV or Excel file containing bill data. 
              <a href="#" @click="downloadTemplate">Download template</a>
            </p>
          </div>

          <Divider />

          <div v-if="importData.length > 0" class="preview-section">
            <h4>Preview Import Data</h4>
            <DataTable :value="importData" responsiveLayout="scroll" class="preview-table">
              <Column field="vendor" header="Vendor"></Column>
              <Column field="billNumber" header="Bill Number"></Column>
              <Column field="amount" header="Amount">
                <template #body="slotProps">
                  ${{ slotProps.data.amount.toLocaleString() }}
                </template>
              </Column>
              <Column field="dueDate" header="Due Date"></Column>
              <Column field="status" header="Status">
                <template #body="slotProps">
                  <Tag 
                    :value="slotProps.data.status" 
                    :severity="getStatusSeverity(slotProps.data.status)"
                  />
                </template>
              </Column>
            </DataTable>

            <div class="import-actions">
              <Button 
                label="Import Bills" 
                icon="pi pi-upload"
                :loading="importing"
                @click="importBills"
              />
              <Button 
                label="Clear" 
                icon="pi pi-times"
                class="p-button-secondary"
                @click="clearImport"
              />
            </div>
          </div>

          <div v-if="importResults.length > 0" class="results-section">
            <h4>Import Results</h4>
            <div class="results-summary">
              <div class="result-stat success">
                <i class="pi pi-check-circle"></i>
                <span>{{ successCount }} Successful</span>
              </div>
              <div class="result-stat error">
                <i class="pi pi-times-circle"></i>
                <span>{{ errorCount }} Failed</span>
              </div>
            </div>
            
            <DataTable :value="importResults" responsiveLayout="scroll">
              <Column field="row" header="Row"></Column>
              <Column field="vendor" header="Vendor"></Column>
              <Column field="billNumber" header="Bill Number"></Column>
              <Column field="status" header="Status">
                <template #body="slotProps">
                  <Tag 
                    :value="slotProps.data.status" 
                    :severity="slotProps.data.status === 'Success' ? 'success' : 'danger'"
                  />
                </template>
              </Column>
              <Column field="message" header="Message"></Column>
            </DataTable>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const importing = ref(false)
const importData = ref([])
const importResults = ref([])

const successCount = computed(() => 
  importResults.value.filter(r => r.status === 'Success').length
)

const errorCount = computed(() => 
  importResults.value.filter(r => r.status === 'Error').length
)

const handleFileUpload = (event: any) => {
  const file = event.files[0]
  if (!file) return

  // Mock file parsing
  const mockData = [
    {
      vendor: 'ABC Supplies Co.',
      billNumber: 'BILL-101',
      amount: 2500,
      dueDate: '2024-02-15',
      status: 'Valid'
    },
    {
      vendor: 'XYZ Services Ltd.',
      billNumber: 'BILL-102',
      amount: 1800,
      dueDate: '2024-02-20',
      status: 'Valid'
    },
    {
      vendor: 'Invalid Vendor',
      billNumber: '',
      amount: 0,
      dueDate: '2024-02-25',
      status: 'Invalid'
    }
  ]
  
  importData.value = mockData
}

const downloadTemplate = () => {
  // Mock template download
  const csvContent = "Vendor,Bill Number,Amount,Due Date,Description\nABC Supplies Co.,BILL-001,2500.00,2024-02-15,Office supplies\n"
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'bills_import_template.csv'
  a.click()
  window.URL.revokeObjectURL(url)
}

const importBills = async () => {
  importing.value = true
  
  try {
    // Mock import process
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    importResults.value = importData.value.map((item, index) => ({
      row: index + 1,
      vendor: item.vendor,
      billNumber: item.billNumber,
      status: item.status === 'Valid' ? 'Success' : 'Error',
      message: item.status === 'Valid' ? 'Bill imported successfully' : 'Invalid data'
    }))
    
    importData.value = []
  } catch (error) {
    console.error('Import failed:', error)
  } finally {
    importing.value = false
  }
}

const clearImport = () => {
  importData.value = []
  importResults.value = []
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'Valid': return 'success'
    case 'Invalid': return 'danger'
    default: return null
  }
}
</script>

<style scoped>
.import-bills {
  max-width: 800px;
  margin: 0 auto;
}

.upload-area {
  text-align: center;
  padding: 2rem;
  border: 2px dashed var(--surface-border);
  border-radius: var(--border-radius);
  margin-bottom: 2rem;
}

.upload-help {
  margin-top: 1rem;
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}

.upload-help a {
  color: var(--primary-color);
  text-decoration: none;
}

.preview-section,
.results-section {
  margin-top: 2rem;
}

.preview-table {
  margin: 1rem 0;
}

.import-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.results-summary {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
}

.result-stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius);
}

.result-stat.success {
  background: var(--green-50);
  color: var(--green-700);
}

.result-stat.error {
  background: var(--red-50);
  color: var(--red-700);
}
</style>