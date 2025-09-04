<template>
  <div class="company-profile">
    <div class="dashboard-header">
      <h1>Company Profile Setup</h1>
      <p>Configure your company information and business details</p>
    </div>

    <Card>
      <template #title>Company Information</template>
      <template #content>
        <div class="grid p-fluid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label>Company Name</label>
              <InputText v-model="companyProfile.name" />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label>Legal Name</label>
              <InputText v-model="companyProfile.legalName" />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label>Tax ID</label>
              <InputText v-model="companyProfile.taxId" />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label>Industry</label>
              <Dropdown v-model="companyProfile.industry" :options="industries" />
            </div>
          </div>
          <div class="col-12">
            <div class="field">
              <label>Address</label>
              <Textarea v-model="companyProfile.address" rows="3" />
            </div>
          </div>
          <div class="col-12 md:col-4">
            <div class="field">
              <label>Phone</label>
              <InputText v-model="companyProfile.phone" />
            </div>
          </div>
          <div class="col-12 md:col-4">
            <div class="field">
              <label>Email</label>
              <InputText v-model="companyProfile.email" />
            </div>
          </div>
          <div class="col-12 md:col-4">
            <div class="field">
              <label>Website</label>
              <InputText v-model="companyProfile.website" />
            </div>
          </div>
        </div>
      </template>
      <template #footer>
        <Button label="Save Changes" icon="pi pi-check" @click="saveProfile" />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const companyProfile = ref({
  name: 'Paksa Financial Solutions',
  legalName: 'Paksa Financial Solutions LLC',
  taxId: '12-3456789',
  industry: 'Financial Services',
  address: '123 Business Ave\nSuite 100\nNew York, NY 10001',
  phone: '+1 (555) 123-4567',
  email: 'info@paksa.com',
  website: 'https://paksa.com'
})

const industries = ref([
  'Financial Services',
  'Technology',
  'Manufacturing',
  'Retail',
  'Healthcare',
  'Real Estate',
  'Other'
])

const saveProfile = () => {
  console.log('Saving company profile:', companyProfile.value)
}
</script>

<style scoped>
.company-profile {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.dashboard-header p {
  color: #6b7280;
  margin: 0;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
}

@media (max-width: 768px) {
  .company-profile {
    padding: 1rem;
  }
}
</style>