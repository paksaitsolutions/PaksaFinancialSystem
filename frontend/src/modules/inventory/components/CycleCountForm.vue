<template>
  <v-card>
    <v-card-title>{{ isEdit ? 'Update Count' : 'Create Cycle Count' }}</v-card-title>
    <v-card-text>
      <v-form ref="form" v-model="valid">
        <v-row v-if="!isEdit">
          <v-col cols="12" md="6">
            <v-select
              v-model="formData.location_id"
              label="Location*"
              :items="locations"
              item-title="name"
              item-value="id"
              :rules="[v => !!v || 'Location is required']"
              required
              @update:model-value="loadLocationItems"
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-text-field
              v-model="formData.counted_by"
              label="Counted By"
              prepend-inner-icon="mdi-account"
            ></v-text-field>
          </v-col>
          
          <v-col cols="12">
            <v-textarea
              v-model="formData.notes"
              label="Notes"
              rows="2"
              auto-grow
            ></v-textarea>
          </v-col>
        </v-row>
        
        <!-- Items to Count -->
        <div v-if="formData.location_id && !isEdit">
          <h3 class="mb-4">Items to Count</h3>
          <v-data-table
            v-model="selectedItems"
            :headers="itemHeaders"
            :items="locationItems"
            :loading="loadingItems"
            show-select
            class="elevation-1"
          >
            <template v-slot:item.quantity_on_hand="{ item }">
              {{ formatQuantity(item.quantity_on_hand) }}
            </template>
          </v-data-table>
        </div>
        
        <!-- Count Progress (Edit Mode) -->
        <div v-if="isEdit && cycleCount">
          <div class="d-flex align-center justify-space-between mb-4">
            <h3>Count Progress</h3>
            <v-chip
              :color="getStatusColor(cycleCount.status)"
              text-color="white"
            >
              {{ formatStatus(cycleCount.status) }}
            </v-chip>
          </div>
          
          <v-data-table
            :headers="countHeaders"
            :items="cycleCount.line_items"
            class="elevation-1"
          >
            <template v-slot:item.is_counted="{ item }">
              <v-icon :color="item.is_counted ? 'success' : 'grey'">
                {{ item.is_counted ? 'mdi-check-circle' : 'mdi-circle-outline' }}
              </v-icon>
            </template>
            
            <template v-slot:item.system_quantity="{ item }">
              {{ formatQuantity(item.system_quantity) }}
            </template>
            
            <template v-slot:item.counted_quantity="{ item }">
              <v-text-field
                v-if="!item.is_counted && cycleCount.status !== 'completed'"
                v-model="item.counted_quantity"
                type="number"
                step="0.0001"
                density="compact"
                hide-details
                @blur="updateLineItem(item)"
              ></v-text-field>
              <span v-else>{{ formatQuantity(item.counted_quantity) }}</span>
            </template>
            
            <template v-slot:item.variance="{ item }">
              <span :class="getVarianceColor(item.variance)">
                {{ formatQuantity(item.variance) }}
              </span>
            </template>
          </v-data-table>
          
          <div v-if="cycleCount.status === 'in_progress'" class="mt-4">
            <v-btn
              color="success"
              :disabled="!allItemsCounted"
              @click="completeCount"
            >
              Complete Count
            </v-btn>
          </div>
        </div>
      </v-form>
    </v-card-text>
    
    <v-card-actions v-if="!isEdit">
      <v-spacer></v-spacer>
      <v-btn color="primary" variant="text" @click="cancel">Cancel</v-btn>
      <v-btn
        color="primary"
        :loading="saving"
        :disabled="!valid || selectedItems.length === 0"
        @click="createCount"
      >
        Create Count
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { apiClient } from '@/utils/apiClient';

// Props
const props = defineProps({
  cycleCount: {
    type: Object,
    default: null
  }
});

// Emits
const emit = defineEmits(['saved', 'cancelled']);

// Composables
const { showSnackbar } = useSnackbar();

// Refs
const form = ref(null);
const valid = ref(false);
const saving = ref(false);
const loadingItems = ref(false);

// Data
const locations = ref([]);
const locationItems = ref([]);
const selectedItems = ref([]);

// Computed
const isEdit = computed(() => !!props.cycleCount);

const allItemsCounted = computed(() => {
  if (!props.cycleCount?.line_items) return false;
  return props.cycleCount.line_items.every(item => item.is_counted);
});

// Form data
const formData = reactive({
  location_id: null,
  counted_by: '',
  notes: '',
});

// Headers
const itemHeaders = [
  { title: 'SKU', key: 'sku', sortable: false },
  { title: 'Name', key: 'name', sortable: false },
  { title: 'Current Qty', key: 'quantity_on_hand', sortable: false, align: 'end' },
];

const countHeaders = [
  { title: 'Counted', key: 'is_counted', sortable: false, align: 'center' },
  { title: 'SKU', key: 'item_sku', sortable: false },
  { title: 'Name', key: 'item_name', sortable: false },
  { title: 'System Qty', key: 'system_quantity', sortable: false, align: 'end' },
  { title: 'Counted Qty', key: 'counted_quantity', sortable: false, align: 'end' },
  { title: 'Variance', key: 'variance', sortable: false, align: 'end' },
];

// Methods
const fetchLocations = async () => {
  try {
    const response = await apiClient.get('/api/v1/inventory/locations');
    locations.value = response.data || [];
  } catch (error) {
    console.error('Error fetching locations:', error);
  }
};

const loadLocationItems = async () => {
  if (!formData.location_id) return;
  
  loadingItems.value = true;
  try {
    const response = await apiClient.get('/api/v1/inventory/items', {
      params: { location_id: formData.location_id }
    });
    locationItems.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load location items', 'error');
    console.error('Error loading items:', error);
  } finally {
    loadingItems.value = false;
  }
};

const createCount = async () => {
  if (!valid.value || selectedItems.value.length === 0) return;
  
  saving.value = true;
  try {
    const payload = {
      location_id: formData.location_id,
      counted_by: formData.counted_by,
      notes: formData.notes,
      line_items: selectedItems.value.map(item => ({
        item_id: item.id,
        system_quantity: item.quantity_on_hand,
      })),
    };
    
    await apiClient.post('/api/v1/inventory/cycle-counts', payload);
    showSnackbar('Cycle count created successfully', 'success');
    emit('saved');
  } catch (error) {
    showSnackbar(error.response?.data?.message || 'Failed to create cycle count', 'error');
    console.error('Error creating cycle count:', error);
  } finally {
    saving.value = false;
  }
};

const updateLineItem = async (item) => {
  if (!item.counted_quantity) return;
  
  try {
    await apiClient.put(`/api/v1/inventory/cycle-counts/line-items/${item.id}`, {
      counted_quantity: Number(item.counted_quantity),
      notes: item.notes || '',
    });
    
    // Update local data
    item.variance = Number(item.counted_quantity) - Number(item.system_quantity);
    item.is_counted = true;
    
    showSnackbar('Count updated', 'success');
  } catch (error) {
    showSnackbar('Failed to update count', 'error');
    console.error('Error updating line item:', error);
  }
};

const completeCount = async () => {
  try {
    await apiClient.post(`/api/v1/inventory/cycle-counts/${props.cycleCount.id}/complete`);
    showSnackbar('Cycle count completed successfully', 'success');
    emit('saved');
  } catch (error) {
    showSnackbar(error.response?.data?.message || 'Failed to complete count', 'error');
    console.error('Error completing count:', error);
  }
};

const cancel = () => {
  emit('cancelled');
};

// Helper methods
const formatQuantity = (quantity) => {
  return Number(quantity || 0).toLocaleString();
};

const formatStatus = (status) => {
  return status.replace('_', ' ').toUpperCase();
};

const getStatusColor = (status) => {
  const colors = {
    pending: 'warning',
    in_progress: 'info',
    completed: 'success',
    cancelled: 'error',
  };
  return colors[status] || 'grey';
};

const getVarianceColor = (variance) => {
  const num = Number(variance || 0);
  if (num > 0) return 'text-success';
  if (num < 0) return 'text-error';
  return '';
};

// Lifecycle hooks
onMounted(() => {
  fetchLocations();
});
</script>