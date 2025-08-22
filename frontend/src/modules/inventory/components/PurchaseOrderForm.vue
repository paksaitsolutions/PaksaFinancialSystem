<template>
  <v-card>
    <v-card-title>Create Purchase Order</v-card-title>
    <v-card-text>
      <v-form ref="form" v-model="valid" @submit.prevent="submitPurchaseOrder">
        <v-row>
          <!-- Header Information -->
          <v-col cols="12" md="6">
            <v-select
              v-model="formData.vendor_id"
              label="Vendor*"
              :items="vendors"
              item-title="name"
              item-value="id"
              :rules="[v => !!v || 'Vendor is required']"
              required
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-menu
              ref="expectedDateMenu"
              v-model="expectedDateMenu"
              :close-on-content-click="false"
              transition="scale-transition"
              offset-y
              min-width="auto"
            >
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-model="formData.expected_date"
                  label="Expected Date"
                  prepend-inner-icon="mdi-calendar"
                  readonly
                  v-bind="props"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="formData.expected_date"
                @update:model-value="expectedDateMenu = false"
              ></v-date-picker>
            </v-menu>
          </v-col>
          
          <v-col cols="12">
            <v-textarea
              v-model="formData.notes"
              label="Notes"
              rows="2"
              auto-grow
            ></v-textarea>
          </v-col>
          
          <!-- Line Items -->
          <v-col cols="12">
            <div class="d-flex align-center justify-space-between mb-4">
              <h3>Line Items</h3>
              <v-btn color="primary" size="small" @click="addLineItem">
                <v-icon>mdi-plus</v-icon> Add Item
              </v-btn>
            </div>
            
            <v-card variant="outlined">
              <v-card-text>
                <div v-if="formData.line_items.length === 0" class="text-center py-4">
                  <p class="text-grey">No items added yet. Click "Add Item" to get started.</p>
                </div>
                
                <div v-else>
                  <v-row
                    v-for="(item, index) in formData.line_items"
                    :key="index"
                    class="align-center mb-2"
                  >
                    <v-col cols="12" md="4">
                      <v-select
                        v-model="item.item_id"
                        label="Item*"
                        :items="inventoryItems"
                        item-title="name"
                        item-value="id"
                        :rules="[v => !!v || 'Item is required']"
                        required
                        @update:model-value="updateLineTotal(index)"
                      ></v-select>
                    </v-col>
                    
                    <v-col cols="12" md="3">
                      <v-text-field
                        v-model="item.quantity_ordered"
                        label="Quantity*"
                        type="number"
                        step="0.0001"
                        min="0"
                        :rules="[
                          v => !!v || 'Quantity is required',
                          v => v > 0 || 'Quantity must be greater than 0'
                        ]"
                        required
                        @input="updateLineTotal(index)"
                      ></v-text-field>
                    </v-col>
                    
                    <v-col cols="12" md="3">
                      <v-text-field
                        v-model="item.unit_cost"
                        label="Unit Cost*"
                        type="number"
                        step="0.01"
                        min="0"
                        :rules="[
                          v => !!v || 'Unit cost is required',
                          v => v >= 0 || 'Unit cost must be non-negative'
                        ]"
                        required
                        @input="updateLineTotal(index)"
                      ></v-text-field>
                    </v-col>
                    
                    <v-col cols="12" md="2">
                      <div class="d-flex align-center">
                        <span class="text-body-2 mr-2">{{ formatCurrency(item.line_total || 0) }}</span>
                        <v-btn
                          icon
                          size="small"
                          color="error"
                          @click="removeLineItem(index)"
                        >
                          <v-icon>mdi-delete</v-icon>
                        </v-btn>
                      </div>
                    </v-col>
                  </v-row>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          
          <!-- Totals -->
          <v-col cols="12" md="6" offset-md="6">
            <v-card variant="outlined">
              <v-card-text>
                <div class="d-flex justify-space-between">
                  <span class="font-weight-bold">Total Amount:</span>
                  <span class="font-weight-bold">{{ formatCurrency(totalAmount) }}</span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>
    
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="primary" variant="text" @click="cancel">Cancel</v-btn>
      <v-btn
        color="primary"
        :loading="saving"
        :disabled="!valid || saving || formData.line_items.length === 0"
        @click="submitPurchaseOrder"
      >
        Create Purchase Order
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { formatCurrency } from '@/utils/formatters';
import { apiClient } from '@/utils/apiClient';

// Emits
const emit = defineEmits(['saved', 'cancelled']);

// Composables
const { showSnackbar } = useSnackbar();

// Refs
const form = ref(null);
const valid = ref(false);
const saving = ref(false);
const expectedDateMenu = ref(false);

// Data
const vendors = ref([]);
const inventoryItems = ref([]);

// Form data
const formData = reactive({
  vendor_id: null,
  expected_date: null,
  notes: '',
  line_items: [],
});

// Computed
const totalAmount = computed(() => {
  return formData.line_items.reduce((sum, item) => sum + (item.line_total || 0), 0);
});

// Methods
const fetchVendors = async () => {
  try {
    const response = await apiClient.get('/api/v1/accounts-payable/vendors');
    vendors.value = response.data;
  } catch (error) {
    console.error('Error fetching vendors:', error);
  }
};

const fetchInventoryItems = async () => {
  try {
    const response = await apiClient.get('/api/v1/inventory/items');
    inventoryItems.value = response.data;
  } catch (error) {
    console.error('Error fetching inventory items:', error);
  }
};

const addLineItem = () => {
  formData.line_items.push({
    item_id: null,
    quantity_ordered: 1,
    unit_cost: 0,
    line_total: 0,
  });
};

const removeLineItem = (index) => {
  formData.line_items.splice(index, 1);
};

const updateLineTotal = (index) => {
  const item = formData.line_items[index];
  const quantity = Number(item.quantity_ordered) || 0;
  const unitCost = Number(item.unit_cost) || 0;
  item.line_total = quantity * unitCost;
};

const submitPurchaseOrder = async () => {
  if (!valid.value || formData.line_items.length === 0) return;
  
  saving.value = true;
  try {
    const payload = {
      vendor_id: formData.vendor_id,
      expected_date: formData.expected_date,
      notes: formData.notes,
      line_items: formData.line_items.map(item => ({
        item_id: item.item_id,
        quantity_ordered: Number(item.quantity_ordered),
        unit_cost: Number(item.unit_cost),
      })),
    };
    
    await apiClient.post('/api/v1/inventory/purchase-orders', payload);
    showSnackbar('Purchase order created successfully', 'success');
    emit('saved');
  } catch (error) {
    showSnackbar(error.response?.data?.message || 'Failed to create purchase order', 'error');
    console.error('Error creating purchase order:', error);
  } finally {
    saving.value = false;
  }
};

const cancel = () => {
  emit('cancelled');
};

// Lifecycle hooks
onMounted(() => {
  fetchVendors();
  fetchInventoryItems();
  addLineItem(); // Start with one line item
});
</script>