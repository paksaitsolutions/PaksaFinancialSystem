<template>
  <v-card>
    <v-card-title>Stock Adjustment</v-card-title>
    <v-card-text>
      <v-form ref="form" v-model="valid" @submit.prevent="submitAdjustment">
        <v-row>
          <v-col cols="12" md="6">
            <v-select
              v-model="formData.item_id"
              label="Item*"
              :items="items"
              item-title="name"
              item-value="id"
              :rules="[v => !!v || 'Item is required']"
              required
              @update:model-value="handleItemChange"
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-select
              v-model="formData.location_id"
              label="Location*"
              :items="locations"
              item-title="name"
              item-value="id"
              :rules="[v => !!v || 'Location is required']"
              required
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-text-field
              v-model="currentQuantity"
              label="Current Quantity"
              readonly
              variant="outlined"
            ></v-text-field>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-text-field
              v-model="formData.quantity_adjustment"
              label="Adjustment Quantity*"
              type="number"
              step="0.0001"
              :rules="[
                v => !!v || 'Adjustment quantity is required',
                v => v != 0 || 'Adjustment quantity cannot be zero'
              ]"
              required
              hint="Use negative values to decrease stock"
            ></v-text-field>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-select
              v-model="formData.reason"
              label="Reason*"
              :items="reasonOptions"
              :rules="[v => !!v || 'Reason is required']"
              required
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-text-field
              v-model="formData.reference"
              label="Reference"
              placeholder="Document number, etc."
            ></v-text-field>
          </v-col>
          
          <v-col cols="12">
            <v-textarea
              v-model="formData.notes"
              label="Notes"
              rows="3"
              auto-grow
            ></v-textarea>
          </v-col>
          
          <v-col cols="12">
            <div class="text-subtitle-2 mb-2">Adjustment Summary:</div>
            <v-card variant="outlined">
              <v-card-text>
                <div class="d-flex justify-space-between">
                  <span>Current Quantity:</span>
                  <span>{{ formatQuantity(currentQuantity) }}</span>
                </div>
                <div class="d-flex justify-space-between">
                  <span>Adjustment:</span>
                  <span :class="adjustmentColor">{{ formatQuantity(formData.quantity_adjustment) }}</span>
                </div>
                <v-divider class="my-2"></v-divider>
                <div class="d-flex justify-space-between font-weight-bold">
                  <span>New Quantity:</span>
                  <span>{{ formatQuantity(newQuantity) }}</span>
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
        :disabled="!valid || saving"
        @click="submitAdjustment"
      >
        Create Adjustment
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { apiClient } from '@/utils/apiClient';

// Emits
const emit = defineEmits(['saved', 'cancelled']);

// Composables
const { showSnackbar } = useSnackbar();

// Refs
const form = ref(null);
const valid = ref(false);
const saving = ref(false);

// Data
const items = ref([]);
const locations = ref([]);
const currentQuantity = ref(0);

// Form data
const formData = reactive({
  item_id: null,
  location_id: null,
  quantity_adjustment: 0,
  reason: '',
  reference: '',
  notes: '',
});

// Reason options
const reasonOptions = [
  'Physical Count Adjustment',
  'Damaged Goods',
  'Expired Items',
  'Theft/Loss',
  'Found Items',
  'System Correction',
  'Other',
];

// Computed
const newQuantity = computed(() => {
  return Number(currentQuantity.value) + Number(formData.quantity_adjustment || 0);
});

const adjustmentColor = computed(() => {
  const adj = Number(formData.quantity_adjustment || 0);
  if (adj > 0) return 'text-success';
  if (adj < 0) return 'text-error';
  return '';
});

// Methods
const fetchItems = async () => {
  try {
    const response = await apiClient.get('/api/v1/inventory/items');
    items.value = response.data;
  } catch (error) {
    console.error('Error fetching items:', error);
  }
};

const fetchLocations = async () => {
  try {
    const response = await apiClient.get('/api/v1/inventory/locations');
    locations.value = response.data || [];
  } catch (error) {
    console.error('Error fetching locations:', error);
  }
};

const handleItemChange = (itemId) => {
  const item = items.value.find(i => i.id === itemId);
  if (item) {
    currentQuantity.value = item.quantity_on_hand;
  }
};

const submitAdjustment = async () => {
  if (!valid.value) return;
  
  saving.value = true;
  try {
    const payload = {
      ...formData,
      quantity_adjustment: Number(formData.quantity_adjustment),
    };
    
    await apiClient.post('/api/v1/inventory/adjustments', payload);
    showSnackbar('Stock adjustment created successfully', 'success');
    emit('saved');
  } catch (error) {
    showSnackbar(error.response?.data?.message || 'Failed to create adjustment', 'error');
    console.error('Error creating adjustment:', error);
  } finally {
    saving.value = false;
  }
};

const cancel = () => {
  emit('cancelled');
};

const formatQuantity = (quantity) => {
  return Number(quantity || 0).toLocaleString();
};

// Lifecycle hooks
onMounted(() => {
  fetchItems();
  fetchLocations();
});
</script>