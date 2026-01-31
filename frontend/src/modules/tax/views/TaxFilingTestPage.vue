<template>
  <div class="tax-filing-test-page">
    <div class="card">
      <TabView>
        <TabPanel header="Create New Filing">
          <div class="p-4">
            <h2>Create New Tax Filing</h2>
            <TaxFilingForm 
              :company-id="currentCompanyId"
              @saved="onFilingSaved"
              @cancel="$router.push('/tax/filings')"
            />
          </div>
        </TabPanel>
        
        <TabPanel header="Edit Existing Filing">
          <div class="p-4">
            <h2>Edit Tax Filing</h2>
            <div class="flex align-items-center gap-3 mb-4">
              <span class="p-float-label">
                <Dropdown
                  v-model="selectedFilingId"
                  :options="sampleFilings"
                  option-label="display"
                  option-value="id"
                  placeholder="Select a filing to edit"
                  class="w-full md:w-20rem"
                />
                <label>Select Filing</label>
              </span>
              <Button 
                label="Load" 
                icon="pi pi-search" 
                :disabled="!selectedFilingId"
                @click="loadFiling"
              />
            </div>
            
            <div v-if="editingFiling" class="mt-4">
              <TaxFilingForm 
                :filing-id="editingFiling.id"
                :company-id="currentCompanyId"
                @saved="onFilingSaved"
                @cancel="$router.push('/tax/filings')"
              />
            </div>
          </div>
        </TabPanel>
      </TabView>
    </div>
    
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';

const router = useRouter();
const toast = useToast();

// In a real app, this would come from auth store
const currentCompanyId = 'company-123';

// Sample data for testing
const sampleFilings = [
  { id: 'filing-1', display: 'Q1 2023 - Income Tax (PK)' },
  { id: 'filing-2', display: 'Q2 2023 - Sales Tax (KSA)' },
  { id: 'filing-3', display: 'March 2023 - VAT (UAE)' },
  { id: 'filing-4', display: 'Q1 2023 - Withholding Tax (US)' },
];

const selectedFilingId = ref<string | null>(null);
const editingFiling = ref<any>(null);

const loadFiling = () => {
  if (!selectedFilingId.value) return;
  
  // In a real app, this would be an API call to fetch the filing
  // For now, we'll use mock data
  setTimeout(() => {
    editingFiling.value = {
      id: selectedFilingId.value,
      company_id: currentCompanyId,
      tax_type: 'income',
      tax_period_id: '2023-q1',
      jurisdiction_id: 'pk',
      due_date: '2023-04-15',
      currency: 'USD',
      tax_amount: 12500,
      penalty_amount: 250,
      interest_amount: 187.5,
      notes: 'Q1 2023 corporate income tax filing',
      status: 'draft',
      created_at: '2023-03-01T10:00:00Z',
      updated_at: '2023-03-15T14:30:00Z',
      attachments: [
        {
          id: 'att-1',
          filing_id: selectedFilingId.value,
          file_name: 'tax_return_q1_2023.pdf',
          file_type: 'application/pdf',
          file_size: 2456789,
          file_url: '/documents/tax_returns/2023/q1.pdf',
          attachment_type: 'return',
          description: 'Q1 2023 Tax Return',
          uploaded_by: 'user-123',
          uploaded_at: '2023-03-10T11:30:00Z'
        }
      ]
    };
  }, 500);
};

const onFilingSaved = (filing: any) => {
  console.log('Filing saved:', filing);
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: `Tax filing ${filing.id ? 'updated' : 'created'} successfully`,
    life: 5000
  });
  
  // In a real app, you might want to navigate to the filing detail page
  // router.push(`/tax/filings/${filing.id}`);
};
</script>

<style scoped>
.tax-filing-test-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
}

h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: var(--primary-color);
}

:deep(.p-tabview .p-tabview-nav) {
  margin-bottom: 1.5rem;
}

:deep(.p-tabview .p-tabview-panels) {
  padding: 0;
  background: transparent;
  border: none;
}

:deep(.p-tabview .p-tabview-panel) {
  padding: 0;
}
</style>
