<template>
  <div class="location-management">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h3>Inventory Locations</h3>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateDialog">
          Add Location
        </v-btn>
      </v-card-title>
      
      <v-card-text>
        <!-- Search and filters -->
        <v-row>
          <v-col cols="12" sm="4">
            <v-text-field
              v-model="searchQuery"
              label="Search locations"
              prepend-inner-icon="mdi-magnify"
              density="compact"
              hide-details
              @update:model-value="debouncedFetchLocations"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="4">
            <v-select
              v-model="statusFilter"
              label="Status"
              :items="statusOptions"
              density="compact"
              hide-details
              clearable
              @update:model-value="fetchLocations"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="4">
            <v-btn
              color="secondary"
              variant="outlined"
              prepend-icon="mdi-filter-remove"
              @click="clearFilters"
            >
              Clear Filters
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
      
      <!-- Data table -->
      <v-data-table
        :headers="headers"
        :items="locations"
        :loading="loading"
        class="elevation-1"
      >
        <template v-slot:item.is_active="{ item }">
          <v-chip
            :color="item.is_active ? 'success' : 'error'"
            size="small"
            text-color="white"
          >
            {{ item.is_active ? 'Active' : 'Inactive' }}
          </v-chip>
        </template>
        
        <template v-slot:item.address="{ item }">
          <div v-if="item.address_line1">
            {{ formatAddress(item) }}
          </div>
          <span v-else class="text-grey">No address</span>
        </template>
        
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            variant="text"
            size="small"
            color="primary"
            @click="viewLocation(item)"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
          <v-btn
            icon
            variant="text"
            size="small"
            color="warning"
            @click="editLocation(item)"
          >
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn
            icon
            variant="text"
            size="small"
            color="error"
            @click="confirmDelete(item)"
          >
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>
    
    <!-- Create/Edit Dialog -->
    <v-dialog v-model="dialog.show" max-width="800px">
      <v-card>
        <v-card-title>{{ dialog.isEdit ? 'Edit' : 'Add' }} Location</v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="dialog.valid">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="dialog.formData.code"
                  label="Code*"
                  :rules="[v => !!v || 'Code is required']"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="dialog.formData.name"
                  label="Name*"
                  :rules="[v => !!v || 'Name is required']"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="dialog.formData.description"
                  label="Description"
                  rows="2"
                  auto-grow
                ></v-textarea>
              </v-col>
              <v-col cols="12" md="6">
                <v-switch
                  v-model="dialog.formData.is_active"
                  label="Active"
                  color="primary"
                ></v-switch>
              </v-col>
            </v-row>
            
            <v-divider class="my-4"></v-divider>
            <h4 class="mb-4">Address Information</h4>
            
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="dialog.formData.address_line1"
                  label="Address Line 1"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="dialog.formData.address_line2"
                  label="Address Line 2"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="dialog.formData.city"
                  label="City"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="dialog.formData.state"
                  label="State/Province"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="dialog.formData.postal_code"
                  label="Postal Code"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="dialog.formData.country"
                  label="Country"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="dialog.show = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="dialog.saving"
            :disabled="!dialog.valid"
            @click="saveLocation"
          >
            {{ dialog.isEdit ? 'Update' : 'Create' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog.show" max-width="500px">
      <v-card>
        <v-card-title>Delete Location</v-card-title>
        <v-card-text>
          Are you sure you want to delete location "{{ deleteDialog.location?.name }}"?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="deleteDialog.show = false">Cancel</v-btn>
          <v-btn color="error" @click="deleteLocation">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { debounce } from '@/utils/debounce';
import { apiClient } from '@/utils/apiClient';

// Composables
const { showSnackbar } = useSnackbar();

// Data
const locations = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const statusFilter = ref(null);

// Dialog state
const dialog = reactive({
  show: false,
  isEdit: false,
  valid: false,
  saving: false,
  formData: {
    code: '',
    name: '',
    description: '',
    is_active: true,
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
  },
  editId: null,
});

const deleteDialog = reactive({
  show: false,
  location: null,
});

// Table headers
const headers = [
  { title: 'Code', key: 'code', sortable: true },
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Status', key: 'is_active', sortable: true },
  { title: 'Address', key: 'address', sortable: false },
  { title: 'Description', key: 'description', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
];

// Options
const statusOptions = [
  { title: 'Active', value: true },
  { title: 'Inactive', value: false },
];

// Methods
const fetchLocations = async () => {
  loading.value = true;
  try {
    const params = {};
    if (searchQuery.value) {
      params.name = searchQuery.value;
    }
    if (statusFilter.value !== null) {
      params.is_active = statusFilter.value;
    }
    
    const response = await apiClient.get('/api/v1/inventory/locations', { params });
    locations.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load locations', 'error');
    console.error('Error fetching locations:', error);
  } finally {
    loading.value = false;
  }
};

const debouncedFetchLocations = debounce(fetchLocations, 300);

const clearFilters = () => {
  searchQuery.value = '';
  statusFilter.value = null;
  fetchLocations();
};

const openCreateDialog = () => {
  dialog.isEdit = false;
  dialog.editId = null;
  dialog.formData = {
    code: '',
    name: '',
    description: '',
    is_active: true,
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
  };
  dialog.show = true;
};

const viewLocation = (location) => {
  // Implement view functionality
  console.log('View location:', location);
};

const editLocation = (location) => {
  dialog.isEdit = true;
  dialog.editId = location.id;
  dialog.formData = {
    code: location.code,
    name: location.name,
    description: location.description || '',
    is_active: location.is_active,
    address_line1: location.address_line1 || '',
    address_line2: location.address_line2 || '',
    city: location.city || '',
    state: location.state || '',
    postal_code: location.postal_code || '',
    country: location.country || '',
  };
  dialog.show = true;
};

const saveLocation = async () => {
  if (!dialog.valid) return;
  
  dialog.saving = true;
  try {
    if (dialog.isEdit) {
      await apiClient.put(`/api/v1/inventory/locations/${dialog.editId}`, dialog.formData);
      showSnackbar('Location updated successfully', 'success');
    } else {
      await apiClient.post('/api/v1/inventory/locations', dialog.formData);
      showSnackbar('Location created successfully', 'success');
    }
    
    dialog.show = false;
    fetchLocations();
  } catch (error) {
    showSnackbar(error.response?.data?.message || 'Failed to save location', 'error');
    console.error('Error saving location:', error);
  } finally {
    dialog.saving = false;
  }
};

const confirmDelete = (location) => {
  deleteDialog.location = location;
  deleteDialog.show = true;
};

const deleteLocation = async () => {
  if (!deleteDialog.location) return;
  
  try {
    await apiClient.delete(`/api/v1/inventory/locations/${deleteDialog.location.id}`);
    showSnackbar('Location deleted successfully', 'success');
    fetchLocations();
  } catch (error) {
    showSnackbar(error.response?.data?.message || 'Failed to delete location', 'error');
    console.error('Error deleting location:', error);
  } finally {
    deleteDialog.show = false;
    deleteDialog.location = null;
  }
};

const formatAddress = (location) => {
  const parts = [
    location.address_line1,
    location.city,
    location.state,
    location.postal_code,
  ].filter(Boolean);
  return parts.join(', ');
};

// Lifecycle hooks
onMounted(() => {
  fetchLocations();
});
</script>

<style scoped>
.location-management {
  padding: 16px;
}
</style>