<template>
  <div class="payment-management">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4 mb-4">Payment Management</h1>
          
          <v-card v-if="selectedPaymentId">
            <v-card-text class="pa-0">
              <div class="d-flex align-center px-4 py-2 bg-grey-lighten-4">
                <v-btn
                  variant="text"
                  prepend-icon="mdi-arrow-left"
                  @click="clearSelectedPayment"
                >
                  Back to List
                </v-btn>
                <v-spacer></v-spacer>
                <div class="text-h6">Payment {{ selectedPaymentNumber }}</div>
              </div>
              
              <payment-detail
                :payment-id="selectedPaymentId"
                @updated="handlePaymentUpdated"
              />
            </v-card-text>
          </v-card>
          
          <v-card v-else-if="isCreating">
            <v-card-text class="pa-0">
              <div class="d-flex align-center px-4 py-2 bg-grey-lighten-4">
                <v-btn
                  variant="text"
                  prepend-icon="mdi-arrow-left"
                  @click="clearSelectedPayment"
                >
                  Back to List
                </v-btn>
                <v-spacer></v-spacer>
                <div class="text-h6">Create New Payment</div>
              </div>
              
              <payment-form
                @saved="handlePaymentSaved"
                @cancelled="clearSelectedPayment"
              />
            </v-card-text>
          </v-card>
          
          <div v-else>
            <v-tabs v-model="activeTab" bg-color="primary">
              <v-tab value="all">All Payments</v-tab>
              <v-tab value="completed">Completed</v-tab>
              <v-tab value="voided">Voided</v-tab>
            </v-tabs>
            
            <v-window v-model="activeTab" class="mt-4">
              <v-window-item value="all">
                <payment-list
                  @view="viewPayment"
                  @create="createPayment"
                />
              </v-window-item>
              
              <v-window-item value="completed">
                <payment-list
                  :default-filters="{ status: 'completed' }"
                  @view="viewPayment"
                  @create="createPayment"
                />
              </v-window-item>
              
              <v-window-item value="voided">
                <payment-list
                  :default-filters="{ status: 'voided' }"
                  @view="viewPayment"
                  @create="createPayment"
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
import PaymentList from '../components/payment/PaymentList.vue';
import PaymentDetail from '../components/payment/PaymentDetail.vue';
import PaymentForm from '../components/payment/PaymentForm.vue';

// Data
const activeTab = ref('all');
const selectedPaymentId = ref(null);
const selectedPaymentNumber = ref('');
const isCreating = ref(false);

// Methods
const viewPayment = (payment) => {
  selectedPaymentId.value = payment.id;
  selectedPaymentNumber.value = payment.payment_number;
  isCreating.value = false;
};

const createPayment = () => {
  selectedPaymentId.value = null;
  isCreating.value = true;
};

const clearSelectedPayment = () => {
  selectedPaymentId.value = null;
  selectedPaymentNumber.value = '';
  isCreating.value = false;
};

const handlePaymentSaved = () => {
  clearSelectedPayment();
};

const handlePaymentUpdated = () => {
  // Optionally refresh data or perform other actions
};
</script>

<style scoped>
.payment-management {
  padding: 16px;
}
</style>