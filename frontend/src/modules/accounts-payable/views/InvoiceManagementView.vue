<template>
  <div class="invoice-management">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4 mb-4">Invoice Management</h1>
          
          <v-tabs v-model="activeTab" bg-color="primary">
            <v-tab value="invoices">Invoices</v-tab>
            <v-tab value="approvals">Approvals</v-tab>
            <v-tab value="reports">Reports</v-tab>
          </v-tabs>
          
          <v-window v-model="activeTab" class="mt-4">
            <v-window-item value="invoices">
              <v-card v-if="selectedInvoiceId && !isCreating">
                <v-card-text class="pa-0">
                  <div class="d-flex align-center px-4 py-2 bg-grey-lighten-4">
                    <v-btn
                      variant="text"
                      prepend-icon="mdi-arrow-left"
                      @click="clearSelectedInvoice"
                    >
                      Back to List
                    </v-btn>
                    <v-spacer></v-spacer>
                    <div class="text-h6">Invoice {{ selectedInvoiceNumber }}</div>
                  </div>
                  
                  <invoice-detail
                    :invoice-id="selectedInvoiceId"
                    @updated="handleInvoiceUpdated"
                  />
                </v-card-text>
              </v-card>
              
              <v-card v-else-if="isCreating">
                <v-card-text class="pa-0">
                  <div class="d-flex align-center px-4 py-2 bg-grey-lighten-4">
                    <v-btn
                      variant="text"
                      prepend-icon="mdi-arrow-left"
                      @click="clearSelectedInvoice"
                    >
                      Back to List
                    </v-btn>
                    <v-spacer></v-spacer>
                    <div class="text-h6">Create New Invoice</div>
                  </div>
                  
                  <invoice-form
                    @saved="handleInvoiceSaved"
                    @cancelled="clearSelectedInvoice"
                  />
                </v-card-text>
              </v-card>
              
              <div v-else>
                <invoice-list
                  @view="viewInvoice"
                  @create="createInvoice"
                />
              </div>
            </v-window-item>
            
            <v-window-item value="approvals">
              <v-card>
                <v-card-text>
                  <h3 class="text-h6 mb-4">Pending Approvals</h3>
                  <invoice-list
                    :default-filters="{ status: 'pending' }"
                    @view="viewInvoice"
                  />
                </v-card-text>
              </v-card>
            </v-window-item>
            
            <v-window-item value="reports">
              <v-card>
                <v-card-text>
                  <h3 class="text-h6 mb-4">Invoice Reports</h3>
                  <p>Invoice reporting features will be implemented in a future update.</p>
                </v-card-text>
              </v-card>
            </v-window-item>
          </v-window>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

// Data
const activeTab = ref('invoices');
const selectedInvoiceId = ref(null);
const selectedInvoiceNumber = ref('');
const isCreating = ref(false);

// Computed
const showList = computed(() => !selectedInvoiceId.value && !isCreating.value);

// Methods
const viewInvoice = (invoice) => {
  selectedInvoiceId.value = invoice.id;
  selectedInvoiceNumber.value = invoice.invoice_number;
  isCreating.value = false;
};

const createInvoice = () => {
  selectedInvoiceId.value = null;
  isCreating.value = true;
};

const clearSelectedInvoice = () => {
  selectedInvoiceId.value = null;
  selectedInvoiceNumber.value = '';
  isCreating.value = false;
};

const handleInvoiceSaved = () => {
  clearSelectedInvoice();
};

const handleInvoiceUpdated = () => {
  // Optionally refresh data or perform other actions
};
</script>

<style scoped>
.invoice-management {
  padding: 16px;
}
</style>