<template>
  <div class="create-bill">
    <!-- Header Section -->
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div class="header-text">
            <h1>
              <i class="pi pi-file-plus mr-2"></i>
              Create Bill
            </h1>
            <p class="text-600">Create a new vendor bill and manage payment details</p>
          </div>
          <div class="header-actions">
            <Button 
              label="Back to AP" 
              icon="pi pi-arrow-left" 
              @click="$router.push('/ap')"
              severity="secondary"
              outlined
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container">
      <form @submit.prevent="saveBill">
        <!-- Vendor Information -->
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-building mr-2 text-primary"></i>
              Vendor Information
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="vendor-select" class="block mb-2 font-medium">Vendor *</label>
                  <Dropdown 
                    v-model="bill.vendor" 
                    :options="vendors" 
                    optionLabel="name" 
                    optionValue="id"
                    placeholder="Select Vendor" 
                    class="w-full"
                    inputId="vendor-select"
                    :filter="true"
                    filterPlaceholder="Search vendors..."
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="reference" class="block mb-2 font-medium">Vendor Reference</label>
                  <InputText 
                    v-model="bill.reference" 
                    class="w-full"
                    inputId="reference"
                    placeholder="Enter vendor reference"
                  />
                </div>
              </div>
            </div>
          </template>
        </Card>

        <!-- Bill Details -->
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-file mr-2 text-primary"></i>
              Bill Details
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-4">
                <div class="field">
                  <label for="bill-number" class="block mb-2 font-medium">Bill Number *</label>
                  <InputText 
                    v-model="bill.billNumber" 
                    class="w-full"
                    inputId="bill-number"
                    placeholder="Enter bill number"
                  />
                </div>
              </div>
              <div class="col-12 md:col-4">
                <div class="field">
                  <label for="bill-date" class="block mb-2 font-medium">Bill Date *</label>
                  <Calendar 
                    v-model="bill.billDate" 
                    class="w-full"
                    inputId="bill-date"
                    dateFormat="mm/dd/yy"
                    placeholder="Select bill date"
                  />
                </div>
              </div>
              <div class="col-12 md:col-4">
                <div class="field">
                  <label for="due-date" class="block mb-2 font-medium">Due Date *</label>
                  <Calendar 
                    v-model="bill.dueDate" 
                    class="w-full"
                    inputId="due-date"
                    dateFormat="mm/dd/yy"
                    placeholder="Select due date"
                  />
                </div>
              </div>
            </div>
            <div class="grid mt-3">
              <div class="col-12">
                <div class="field">
                  <label for="description" class="block mb-2 font-medium">Description</label>
                  <Textarea 
                    v-model="bill.description" 
                    rows="3" 
                    class="w-full"
                    inputId="description"
                    placeholder="Enter bill description"
                  />
                </div>
              </div>
            </div>
          </template>
        </Card>

        <!-- Line Items -->
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center justify-content-between">
              <div class="flex align-items-center">
                <i class="pi pi-list mr-2 text-primary"></i>
                Line Items
              </div>
              <Button 
                label="Add Line" 
                icon="pi pi-plus" 
                @click="addLineItem"
                size="small"
              />
            </div>
          </template>
          <template #content>
            <DataTable :value="bill.lineItems" class="p-datatable-sm">
              <Column field="description" header="Description">
                <template #body="{ data, index }">
                  <InputText 
                    v-model="data.description" 
                    class="w-full"
                    placeholder="Enter description"
                  />
                </template>
              </Column>
              <Column field="account" header="Account">
                <template #body="{ data, index }">
                  <Dropdown 
                    v-model="data.account" 
                    :options="accounts" 
                    optionLabel="name" 
                    optionValue="id"
                    placeholder="Select Account"
                    class="w-full"
                  />
                </template>
              </Column>
              <Column field="amount" header="Amount">
                <template #body="{ data, index }">
                  <InputNumber 
                    v-model="data.amount" 
                    mode="currency" 
                    currency="USD" 
                    class="w-full"
                    @input="calculateTotal"
                  />
                </template>
              </Column>
              <Column header="Actions" style="width: 5rem">
                <template #body="{ index }">
                  <Button 
                    icon="pi pi-trash" 
                    @click="removeLineItem(index)"
                    severity="danger"
                    text
                    size="small"
                  />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>

        <!-- Totals -->
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-calculator mr-2 text-primary"></i>
              Totals
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-4">
                <div class="field">
                  <label for="subtotal" class="block mb-2 font-medium">Subtotal</label>
                  <InputNumber 
                    v-model="bill.subtotal" 
                    mode="currency" 
                    currency="USD" 
                    class="w-full"
                    inputId="subtotal"
                    :readonly="true"
                  />
                </div>
              </div>
              <div class="col-12 md:col-4">
                <div class="field">
                  <label for="tax-amount" class="block mb-2 font-medium">Tax Amount</label>
                  <InputNumber 
                    v-model="bill.taxAmount" 
                    mode="currency" 
                    currency="USD" 
                    class="w-full"
                    inputId="tax-amount"
                    @input="calculateTotal"
                    placeholder="0.00"
                  />
                </div>
              </div>
              <div class="col-12 md:col-4">
                <div class="field">
                  <label for="total-amount" class="block mb-2 font-medium">Total Amount</label>
                  <InputNumber 
                    v-model="bill.totalAmount" 
                    mode="currency" 
                    currency="USD" 
                    class="w-full"
                    inputId="total-amount"
                    :readonly="true"
                  />
                </div>
              </div>
            </div>
          </template>
        </Card>

        <!-- Actions -->
        <Card>
          <template #content>
            <div class="flex gap-2 justify-content-end">
              <Button 
                type="button" 
                label="Cancel" 
                icon="pi pi-times" 
                @click="$router.push('/ap')"
                severity="secondary"
                outlined
              />
              <Button 
                type="button" 
                label="Save as Draft" 
                icon="pi pi-save" 
                @click="saveDraft"
                severity="secondary"
              />
              <Button 
                type="submit" 
                label="Save Bill" 
                icon="pi pi-check" 
              />
            </div>
          </template>
        </Card>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const toast = useToast()

const bill = ref({
  vendor: '',
  reference: '',
  billNumber: `BILL-${Date.now()}`,
  billDate: new Date(),
  dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
  description: '',
  lineItems: [
    { description: '', account: '', amount: 0 }
  ],
  subtotal: 0,
  taxAmount: 0,
  totalAmount: 0
})

const vendors = ref([
  { id: '1', name: 'Office Supplies Co.' },
  { id: '2', name: 'Tech Solutions Ltd.' },
  { id: '3', name: 'Utility Company' },
  { id: '4', name: 'Marketing Agency' },
  { id: '5', name: 'Equipment Rental' }
])

const accounts = ref([
  { id: '1', name: 'Office Expenses' },
  { id: '2', name: 'Professional Services' },
  { id: '3', name: 'Utilities' },
  { id: '4', name: 'Marketing & Advertising' },
  { id: '5', name: 'Equipment Rental' },
  { id: '6', name: 'Travel & Entertainment' },
  { id: '7', name: 'Software & Subscriptions' }
])

const addLineItem = () => {
  bill.value.lineItems.push({ description: '', account: '', amount: 0 })
}

const removeLineItem = (index: number) => {
  if (bill.value.lineItems.length > 1) {
    bill.value.lineItems.splice(index, 1)
    calculateTotal()
  }
}

const calculateTotal = () => {
  bill.value.subtotal = bill.value.lineItems.reduce((sum, item) => sum + (item.amount || 0), 0)
  bill.value.totalAmount = bill.value.subtotal + (bill.value.taxAmount || 0)
}

const saveBill = () => {
  if (!bill.value.vendor || !bill.value.billNumber) {
    toast.add({ 
      severity: 'error', 
      summary: 'Validation Error', 
      detail: 'Please fill in all required fields', 
      life: 3000 
    })
    return
  }
  
  toast.add({ 
    severity: 'success', 
    summary: 'Success', 
    detail: 'Bill created successfully', 
    life: 3000 
  })
  router.push('/ap')
}

const saveDraft = () => {
  toast.add({ 
    severity: 'info', 
    summary: 'Draft Saved', 
    detail: 'Bill saved as draft', 
    life: 3000 
  })
}

onMounted(() => {
  calculateTotal()
})
</script>

<style scoped>
.create-bill {
  padding: 1rem;
}

.page-header {
  padding: 1.5rem 0;
  margin-bottom: 2rem;
  border-bottom: 1px solid #e9ecef;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-text h1 {
  margin: 0;
  display: flex;
  align-items: center;
  font-size: 1.75rem;
  font-weight: 600;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
}

@media screen and (max-width: 960px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>