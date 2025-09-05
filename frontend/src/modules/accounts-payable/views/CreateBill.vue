<template>
  <div class="create-bill">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Create Bill</h1>
        <p class="text-color-secondary">Create a new vendor bill</p>
      </div>
      <Button label="Back to Dashboard" icon="pi pi-arrow-left" class="p-button-secondary" @click="$router.push('/ap')" />
    </div>

    <Card>
      <template #content>
        <form @submit.prevent="saveBill">
          <div class="grid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Vendor</label>
                <Dropdown v-model="bill.vendor" :options="vendors" optionLabel="name" optionValue="name" placeholder="Select Vendor" class="w-full" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Bill Number</label>
                <InputText v-model="bill.billNumber" class="w-full" />
              </div>
            </div>
          </div>
          
          <div class="grid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Bill Date</label>
                <Calendar v-model="bill.billDate" class="w-full" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Due Date</label>
                <Calendar v-model="bill.dueDate" class="w-full" />
              </div>
            </div>
          </div>

          <div class="field">
            <label>Description</label>
            <Textarea v-model="bill.description" rows="3" class="w-full" />
          </div>

          <div class="field">
            <label>Amount</label>
            <InputNumber v-model="bill.amount" mode="currency" currency="USD" class="w-full" />
          </div>

          <div class="flex gap-2">
            <Button type="submit" label="Save Bill" icon="pi pi-save" />
            <Button type="button" label="Save & New" icon="pi pi-plus" class="p-button-secondary" @click="saveAndNew" />
            <Button type="button" label="Cancel" icon="pi pi-times" class="p-button-text" @click="$router.push('/ap')" />
          </div>
        </form>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const toast = useToast()

const bill = ref({
  vendor: '',
  billNumber: `BILL-${Date.now()}`,
  billDate: new Date(),
  dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
  description: '',
  amount: 0
})

const vendors = ref([
  { name: 'Office Supplies Co.' },
  { name: 'Tech Solutions Ltd.' },
  { name: 'Utility Company' },
  { name: 'Marketing Agency' },
  { name: 'Equipment Rental' }
])

const saveBill = () => {
  toast.add({ severity: 'success', summary: 'Success', detail: 'Bill created successfully', life: 3000 })
  router.push('/ap')
}

const saveAndNew = () => {
  toast.add({ severity: 'success', summary: 'Success', detail: 'Bill created successfully', life: 3000 })
  bill.value = {
    vendor: '',
    billNumber: `BILL-${Date.now()}`,
    billDate: new Date(),
    dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
    description: '',
    amount: 0
  }
}
</script>

<style scoped>
.create-bill {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>