<template>
  <div class="add-vendor">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Add Vendor</h1>
        <p class="text-color-secondary">Add a new vendor to your system</p>
      </div>
      <Button label="Back to Dashboard" icon="pi pi-arrow-left" class="p-button-secondary" @click="$router.push('/ap')" />
    </div>

    <Card>
      <template #content>
        <form @submit.prevent="saveVendor">
          <div class="grid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Vendor Name</label>
                <InputText v-model="vendor.name" class="w-full" :class="{'p-invalid': submitted && !vendor.name}" />
                <small class="p-error" v-if="submitted && !vendor.name">Name is required.</small>
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Vendor Code</label>
                <InputText v-model="vendor.code" class="w-full" />
              </div>
            </div>
          </div>
          
          <div class="grid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Email</label>
                <InputText v-model="vendor.email" type="email" class="w-full" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Phone</label>
                <InputText v-model="vendor.phone" class="w-full" />
              </div>
            </div>
          </div>

          <div class="field">
            <label>Address</label>
            <Textarea v-model="vendor.address" rows="3" class="w-full" />
          </div>

          <div class="grid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Payment Terms</label>
                <Dropdown v-model="vendor.paymentTerms" :options="paymentTerms" placeholder="Select Terms" class="w-full" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Tax ID</label>
                <InputText v-model="vendor.taxId" class="w-full" />
              </div>
            </div>
          </div>

          <div class="flex gap-2">
            <Button type="submit" label="Save Vendor" icon="pi pi-save" />
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
const submitted = ref(false)

const vendor = ref({
  name: '',
  code: `VEN-${Date.now()}`,
  email: '',
  phone: '',
  address: '',
  paymentTerms: '',
  taxId: ''
})

const paymentTerms = ref(['Net 30', 'Net 15', 'Due on Receipt', 'Net 60', '2/10 Net 30'])

const saveVendor = () => {
  submitted.value = true
  if (vendor.value.name) {
    toast.add({ severity: 'success', summary: 'Success', detail: 'Vendor created successfully', life: 3000 })
    router.push('/ap')
  }
}

const saveAndNew = () => {
  submitted.value = true
  if (vendor.value.name) {
    toast.add({ severity: 'success', summary: 'Success', detail: 'Vendor created successfully', life: 3000 })
    vendor.value = {
      name: '',
      code: `VEN-${Date.now()}`,
      email: '',
      phone: '',
      address: '',
      paymentTerms: '',
      taxId: ''
    }
    submitted.value = false
  }
}
</script>

<style scoped>
.add-vendor {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>