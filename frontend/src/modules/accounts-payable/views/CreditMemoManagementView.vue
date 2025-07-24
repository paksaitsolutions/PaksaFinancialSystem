<template>
  <div class="credit-memo-management">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4 mb-4">Credit Memo Management</h1>
          
          <v-card v-if="selectedCreditMemo && !isCreating && !isApplying">
            <v-card-text class="pa-0">
              <div class="d-flex align-center px-4 py-2 bg-grey-lighten-4">
                <v-btn
                  variant="text"
                  prepend-icon="mdi-arrow-left"
                  @click="clearSelection"
                >
                  Back to List
                </v-btn>
                <v-spacer></v-spacer>
                <div class="text-h6">Credit Memo {{ selectedCreditMemo.credit_memo_number }}</div>
              </div>
              
              <!-- Credit memo detail view would go here -->
              <div class="pa-4">
                <p>Credit memo detail view will be implemented here.</p>
              </div>
            </v-card-text>
          </v-card>
          
          <v-card v-else-if="isCreating">
            <v-card-text class="pa-0">
              <div class="d-flex align-center px-4 py-2 bg-grey-lighten-4">
                <v-btn
                  variant="text"
                  prepend-icon="mdi-arrow-left"
                  @click="clearSelection"
                >
                  Back to List
                </v-btn>
                <v-spacer></v-spacer>
                <div class="text-h6">Create New Credit Memo</div>
              </div>
              
              <credit-memo-form
                @saved="handleCreditMemoSaved"
                @cancelled="clearSelection"
              />
            </v-card-text>
          </v-card>
          
          <v-card v-else-if="isApplying && selectedCreditMemo">
            <v-card-text class="pa-0">
              <div class="d-flex align-center px-4 py-2 bg-grey-lighten-4">
                <v-btn
                  variant="text"
                  prepend-icon="mdi-arrow-left"
                  @click="clearSelection"
                >
                  Back to List
                </v-btn>
                <v-spacer></v-spacer>
                <div class="text-h6">Apply Credit Memo {{ selectedCreditMemo.credit_memo_number }}</div>
              </div>
              
              <credit-memo-application
                :credit-memo="selectedCreditMemo"
                @saved="handleCreditMemoApplied"
                @cancelled="clearSelection"
              />
            </v-card-text>
          </v-card>
          
          <div v-else>
            <v-tabs v-model="activeTab" bg-color="primary">
              <v-tab value="all">All Credit Memos</v-tab>
              <v-tab value="active">Active</v-tab>
              <v-tab value="applied">Fully Applied</v-tab>
              <v-tab value="voided">Voided</v-tab>
            </v-tabs>
            
            <v-window v-model="activeTab" class="mt-4">
              <v-window-item value="all">
                <credit-memo-list
                  @view="viewCreditMemo"
                  @create="createCreditMemo"
                  @apply="applyCreditMemo"
                />
              </v-window-item>
              
              <v-window-item value="active">
                <credit-memo-list
                  :default-filters="{ status: 'active' }"
                  @view="viewCreditMemo"
                  @create="createCreditMemo"
                  @apply="applyCreditMemo"
                />
              </v-window-item>
              
              <v-window-item value="applied">
                <credit-memo-list
                  :default-filters="{ status: 'fully_applied' }"
                  @view="viewCreditMemo"
                  @create="createCreditMemo"
                  @apply="applyCreditMemo"
                />
              </v-window-item>
              
              <v-window-item value="voided">
                <credit-memo-list
                  :default-filters="{ status: 'voided' }"
                  @view="viewCreditMemo"
                  @create="createCreditMemo"
                  @apply="applyCreditMemo"
                />
              </v-window-item>
            </v-window>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import CreditMemoList from '../components/credit-memo/CreditMemoList.vue';
import CreditMemoForm from '../components/credit-memo/CreditMemoForm.vue';
import CreditMemoApplication from '../components/credit-memo/CreditMemoApplication.vue';

// Data
const activeTab = ref('all');
const selectedCreditMemo = ref(null);
const isCreating = ref(false);
const isApplying = ref(false);

// Methods
const viewCreditMemo = (creditMemo) => {
  selectedCreditMemo.value = creditMemo;
  isCreating.value = false;
  isApplying.value = false;
};

const createCreditMemo = () => {
  selectedCreditMemo.value = null;
  isCreating.value = true;
  isApplying.value = false;
};

const applyCreditMemo = (creditMemo) => {
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
  clearSelection();
};

const handleCreditMemoApplied = () => {
  clearSelection();
};
</script>

<style scoped>
.credit-memo-management {
  padding: 16px;
}
</style>