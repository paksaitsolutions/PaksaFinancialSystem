<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col cols="12" md="8">
        <v-card elevation="2" class="mb-6">
          <v-card-title class="d-flex align-center justify-space-between">
            <span class="text-h5 font-weight-bold">Bill #{{ bill?.bill_number }}</span>
            <v-chip :color="statusColor(bill?.status)" dark>{{ bill?.status }}</v-chip>
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item>
                <v-list-item-title>Vendor</v-list-item-title>
                <v-list-item-subtitle>{{ bill?.vendor_name }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>Issue Date</v-list-item-title>
                <v-list-item-subtitle>{{ bill?.issue_date }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>Due Date</v-list-item-title>
                <v-list-item-subtitle>{{ bill?.due_date }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>Total Amount</v-list-item-title>
                <v-list-item-subtitle>{{ formatCurrency(bill?.total_amount) }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
            <v-divider class="my-4" />
            <v-data-table :headers="itemHeaders" :items="bill?.bill_items || []" class="elevation-1">
              <template v-slot:item.total="{ item }">
                {{ formatCurrency(item.quantity * item.unit_price) }}
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card elevation="2" class="mb-6">
          <v-card-title class="font-weight-bold">Actions</v-card-title>
          <v-card-text>
            <v-btn color="primary" block class="mb-2">Send Reminder</v-btn>
            <v-btn color="error" block class="mb-2">Mark as Disputed</v-btn>
            <v-btn color="success" block>Record Payment</v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { getBill } from '@/services/accountsPayableService';

const route = useRoute();
const bill = ref<any>(null);

const itemHeaders = [
  { text: 'Description', value: 'description' },
  { text: 'Quantity', value: 'quantity' },
  { text: 'Unit Price', value: 'unit_price' },
  { text: 'Discount %', value: 'discount_percent' },
  { text: 'Tax Rate', value: 'tax_rate' },
  { text: 'Total', value: 'total', sortable: false },
];

function statusColor(status: string) {
  switch (status) {
    case 'PAID': return 'green';
    case 'OVERDUE': return 'red';
    case 'DRAFT': return 'grey';
    default: return 'primary';
  }
}
function formatCurrency(amount: number) {
  return `$${amount?.toFixed(2)}`;
}
onMounted(async () => {
  const { data } = await getBill(route.params.id as string);
  bill.value = data;
});
</script>

<style scoped>
.v-card-title {
  background: linear-gradient(90deg, #1976d2 0%, #42a5f5 100%);
  color: white;
}
</style>
