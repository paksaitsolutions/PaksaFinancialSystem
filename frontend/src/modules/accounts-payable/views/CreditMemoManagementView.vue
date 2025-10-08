<template>
  <div class="credit-memo-management">
    <div class="container">
      <div class="grid">
        <div class="col-12">
          <h1 class="mb-4">Credit Memo Management</h1>
          
          <Card v-if="selectedCreditMemo && !isCreating && !isApplying">
            <template #content>
              <div class="flex align-items-center p-3 surface-100">
                <Button
                  icon="pi pi-arrow-left"
                  label="Back to List"
                  class="p-button-text"
                  @click="clearSelection"
                />
                <div class="flex-1"></div>
                <div class="text-xl font-semibold">Credit Memo {{ selectedCreditMemo.credit_memo_number }}</div>
              </div>
              
              <div class="p-4">
                <p>Credit memo detail view will be implemented here.</p>
              </div>
            </template>
          </Card>
          
          <Card v-else-if="isCreating">
            <template #content>
              <div class="flex align-items-center p-3 surface-100">
                <Button
                  icon="pi pi-arrow-left"
                  label="Back to List"
                  class="p-button-text"
                  @click="clearSelection"
                />
                <div class="flex-1"></div>
                <div class="text-xl font-semibold">Create New Credit Memo</div>
              </div>
              
              <div class="p-4">
                <div class="grid">
                  <div class="col-12 md:col-6">
                    <div class="field">
                      <label for="vendor">Vendor *</label>
                      <Dropdown 
                        id="vendor" 
                        v-model="creditMemoForm.vendorId" 
                        :options="vendors" 
                        optionLabel="name" 
                        optionValue="id" 
                        placeholder="Select vendor"
                        class="w-full"
                      />
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field">
                      <label for="creditDate">Credit Date *</label>
                      <Calendar 
                        id="creditDate" 
                        v-model="creditMemoForm.creditDate" 
                        dateFormat="yy-mm-dd" 
                        :showIcon="true" 
                        class="w-full"
                      />
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field">
                      <label for="amount">Amount *</label>
                      <InputNumber 
                        id="amount" 
                        v-model="creditMemoForm.amount" 
                        mode="currency" 
                        currency="USD" 
                        locale="en-US" 
                        class="w-full"
                      />
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field">
                      <label for="reference">Reference</label>
                      <InputText 
                        id="reference" 
                        v-model="creditMemoForm.reference" 
                        class="w-full"
                      />
                    </div>
                  </div>
                  <div class="col-12">
                    <div class="field">
                      <label for="description">Description</label>
                      <Textarea 
                        id="description" 
                        v-model="creditMemoForm.description" 
                        rows="3" 
                        class="w-full"
                      />
                    </div>
                  </div>
                </div>
                <div class="flex gap-2 mt-4">
                  <Button label="Save" @click="handleCreditMemoSaved" />
                  <Button label="Cancel" severity="secondary" @click="clearSelection" />
                </div>
              </div>
            </template>
          </Card>
          
          <Card v-else-if="isApplying && selectedCreditMemo">
            <template #content>
              <div class="flex align-items-center p-3 surface-100">
                <Button
                  icon="pi pi-arrow-left"
                  label="Back to List"
                  class="p-button-text"
                  @click="clearSelection"
                />
                <div class="flex-1"></div>
                <div class="text-xl font-semibold">Apply Credit Memo {{ selectedCreditMemo.credit_memo_number }}</div>
              </div>
              
              <div class="p-4">
                <p>Credit memo application form will be implemented here.</p>
                <div class="flex gap-2 mt-4">
                  <Button label="Apply" @click="handleCreditMemoApplied" />
                  <Button label="Cancel" severity="secondary" @click="clearSelection" />
                </div>
              </div>
            </template>
          </Card>
          
          <div v-else>
            <TabView v-model:activeIndex="activeTabIndex">
              <TabPanel header="All Credit Memos">
                <CreditMemoList
                  @view="viewCreditMemo"
                  @create="createCreditMemo"
                  @apply="applyCreditMemo"
                />
              </TabPanel>
              
              <TabPanel header="Active">
                <CreditMemoList
                  :default-filters="{ status: 'active' }"
                  @view="viewCreditMemo"
                  @create="createCreditMemo"
                  @apply="applyCreditMemo"
                />
              </TabPanel>
              
              <TabPanel header="Fully Applied">
                <CreditMemoList
                  :default-filters="{ status: 'fully_applied' }"
                  @view="viewCreditMemo"
                  @create="createCreditMemo"
                  @apply="applyCreditMemo"
                />
              </TabPanel>
              
              <TabPanel header="Voided">
                <CreditMemoList
                  :default-filters="{ status: 'voided' }"
                  @view="viewCreditMemo"
                  @create="createCreditMemo"
                  @apply="applyCreditMemo"
                />
              </TabPanel>
            </TabView>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import CreditMemoList from '../components/credit-memo/CreditMemoList.vue';

type CreditMemo = {
  credit_memo_number: string;
  [key: string]: any;
};

// Data
const activeTabIndex = ref(0);
const selectedCreditMemo = ref<CreditMemo | null>(null);
const isCreating = ref(false);
const isApplying = ref(false);

const creditMemoForm = ref({
  vendorId: null,
  creditDate: new Date(),
  amount: 0,
  reference: '',
  description: ''
});

const vendors = ref([]);

// Methods
const viewCreditMemo = (creditMemo: CreditMemo) => {
  selectedCreditMemo.value = creditMemo;
  isCreating.value = false;
  isApplying.value = false;
};

const createCreditMemo = () => {
  selectedCreditMemo.value = null;
  isCreating.value = true;
  isApplying.value = false;
};

const applyCreditMemo = (creditMemo: CreditMemo) => {
  selectedCreditMemo.value = creditMemo;
  isCreating.value = false;
  isApplying.value = true;
};

const clearSelection = () => {
  selectedCreditMemo.value = null;
  isCreating.value = false;
  isApplying.value = false;
};

const handleCreditMemoSaved = () => {
  // Reset form
  creditMemoForm.value = {
    vendorId: null,
    creditDate: new Date(),
    amount: 0,
    reference: '',
    description: ''
  };
  clearSelection();
};

const handleCreditMemoApplied = () => {
  clearSelection();
};
</script>

<style scoped>
.credit-memo-management {
  padding: 1rem;
}

.flex-1 {
  flex: 1;
}
</style>