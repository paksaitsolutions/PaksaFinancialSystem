<template>
  <v-dialog v-model="modelValue" max-width="700px">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <span class="text-h6 font-weight-bold">{{ bill ? 'Edit Bill' : 'New Bill' }}</span>
        <v-btn icon @click="close"><v-icon>mdi-close</v-icon></v-btn>
      </v-card-title>
      <v-card-text>
        <v-form @submit.prevent="saveBill">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field v-model="form.vendor_name" label="Vendor" required />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field v-model="form.issue_date" label="Issue Date" type="date" required />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field v-model="form.due_date" label="Due Date" type="date" required />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-textarea v-model="form.notes" label="Notes" rows="2" />
            </v-col>
          </v-row>
          <!-- Bill Items Table (modern, responsive) -->
          <v-row>
            <v-col cols="12">
              <v-data-table :headers="itemHeaders" :items="form.bill_items" class="elevation-1">
                <template v-slot:item.actions="{ item }">
                  <v-btn icon @click="removeItem(item)"><v-icon>mdi-delete</v-icon></v-btn>
                </template>
              </v-data-table>
              <v-btn color="primary" class="mt-2" @click="addItem">Add Item</v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="saveBill">Save</v-btn>
        <v-btn text @click="close">Cancel</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue';
import { createBill, updateBill } from '@/services/accountsPayableService';

const props = defineProps<{ modelValue: boolean; bill?: any }>();
const emit = defineEmits(['update:modelValue', 'saved']);

const form = ref({
  vendor_name: '',
  issue_date: '',
  due_date: '',
  notes: '',
  bill_items: [],
});

watch(() => props.bill, (val) => {
  if (val) {
    form.value = { ...val };
  } else {
    form.value = {
      vendor_name: '',
      issue_date: '',
      due_date: '',
      notes: '',
      bill_items: [],
    };
  }
});

const itemHeaders = [
  { text: 'Description', value: 'description' },
  { text: 'Quantity', value: 'quantity' },
  { text: 'Unit Price', value: 'unit_price' },
  { text: 'Discount %', value: 'discount_percent' },
  { text: 'Tax Rate', value: 'tax_rate' },
  { text: 'Actions', value: 'actions', sortable: false },
];

function addItem() {
  form.value.bill_items.push({ description: '', quantity: 1, unit_price: 0, discount_percent: 0, tax_rate: 0 });
}
function removeItem(item: any) {
  form.value.bill_items = form.value.bill_items.filter(i => i !== item);
}
function close() {
  emit('update:modelValue', false);
}
async function saveBill() {
  if (props.bill) {
    await updateBill(props.bill.id, form.value);
  } else {
    await createBill(form.value);
  }
  emit('saved');
  close();
}
</script>

<style scoped>
.v-card-title {
  background: linear-gradient(90deg, #1976d2 0%, #42a5f5 100%);
  color: white;
}
.v-data-table {
  font-size: 0.95rem;
}
</style>
