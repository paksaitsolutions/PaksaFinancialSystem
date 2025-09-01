<template>
  <div class="add-vendor">
    <Card>
      <template #title>Add New Vendor</template>
      <template #content>
        <form @submit.prevent="handleSubmit">
          <div class="p-fluid">
            <div class="field">
              <label for="name">Vendor Name</label>
              <InputText 
                id="name"
                v-model="form.name" 
                placeholder="Enter vendor name"
                :class="{ 'p-invalid': errors.name }"
              />
              <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
            </div>

            <div class="field">
              <label for="email">Email</label>
              <InputText 
                id="email"
                v-model="form.email" 
                type="email"
                placeholder="Enter email address"
                :class="{ 'p-invalid': errors.email }"
              />
              <small v-if="errors.email" class="p-error">{{ errors.email }}</small>
            </div>

            <div class="field">
              <label for="phone">Phone</label>
              <InputText 
                id="phone"
                v-model="form.phone" 
                placeholder="Enter phone number"
              />
            </div>

            <div class="field">
              <label for="address">Address</label>
              <Textarea 
                id="address"
                v-model="form.address" 
                rows="3"
                placeholder="Enter vendor address"
              />
            </div>

            <div class="field">
              <label for="taxId">Tax ID</label>
              <InputText 
                id="taxId"
                v-model="form.taxId" 
                placeholder="Enter tax ID"
              />
            </div>

            <div class="field">
              <label for="paymentTerms">Payment Terms</label>
              <Dropdown 
                id="paymentTerms"
                v-model="form.paymentTerms" 
                :options="paymentTermsOptions" 
                optionLabel="label" 
                optionValue="value"
                placeholder="Select payment terms"
              />
            </div>

            <div class="flex gap-2">
              <Button type="submit" label="Add Vendor" :loading="loading" />
              <Button type="button" label="Cancel" class="p-button-secondary" @click="$router.go(-1)" />
            </div>
          </div>
        </form>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  name: '',
  email: '',
  phone: '',
  address: '',
  taxId: '',
  paymentTerms: null
})

const errors = reactive({
  name: '',
  email: ''
})

const paymentTermsOptions = ref([
  { label: 'Net 30', value: 'net30' },
  { label: 'Net 15', value: 'net15' },
  { label: 'Due on Receipt', value: 'due_on_receipt' },
  { label: '2/10 Net 30', value: '2_10_net30' }
])

const handleSubmit = async () => {
  // Clear errors
  Object.keys(errors).forEach(key => errors[key] = '')
  
  // Validate
  if (!form.name) errors.name = 'Vendor name is required'
  if (!form.email) errors.email = 'Email is required'
  
  if (Object.values(errors).some(error => error)) return
  
  loading.value = true
  try {
    // Mock API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    router.push('/ap')
  } catch (error) {
    console.error('Failed to add vendor:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.add-vendor {
  max-width: 600px;
  margin: 0 auto;
}
</style>