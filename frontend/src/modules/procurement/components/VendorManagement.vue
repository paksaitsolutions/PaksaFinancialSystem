<template>
  <div class="vendor-management">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h3>Vendor Management</h3>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="openVendorDialog">
          Add Vendor
        </v-btn>
      </v-card-title>
      
      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="vendors"
          :loading="loading"
          class="elevation-1"
        >
          <template v-slot:item.vendor_name="{ item }">
            <div>
              <strong>{{ item.vendor_name }}</strong>
              <div class="text-caption">{{ item.vendor_code }}</div>
            </div>
          </template>
          
          <template v-slot:item.contact="{ item }">
            <div v-if="item.contact_person || item.email || item.phone">
              <div v-if="item.contact_person">{{ item.contact_person }}</div>
              <div v-if="item.email" class="text-caption">{{ item.email }}</div>
              <div v-if="item.phone" class="text-caption">{{ item.phone }}</div>
            </div>
            <span v-else class="text-grey">No contact info</span>
          </template>
          
          <template v-slot:item.is_active="{ item }">
            <v-chip :color="item.is_active ? 'success' : 'error'" size="small">
              {{ item.is_active ? 'Active' : 'Inactive' }}
            </v-chip>
          </template>
          
          <template v-slot:item.is_approved="{ item }">
            <v-chip :color="item.is_approved ? 'success' : 'warning'" size="small">
              {{ item.is_approved ? 'Approved' : 'Pending' }}
            </v-chip>
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-menu>
              <template v-slot:activator="{ props }">
                <v-btn icon size="small" v-bind="props">
                  <v-icon>mdi-dots-vertical</v-icon>
                </v-btn>
              </template>
              
              <v-list>
                <v-list-item @click="editVendor(item)">
                  <v-list-item-title>Edit</v-list-item-title>
                </v-list-item>
                
                <v-list-item @click="approveVendor(item)" v-if="!item.is_approved">
                  <v-list-item-title>Approve</v-list-item-title>
                </v-list-item>
                
                <v-list-item @click="viewPurchaseOrders(item)">
                  <v-list-item-title>View Orders</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
    
    <!-- Vendor Dialog -->
    <v-dialog v-model="vendorDialog.show" max-width="800px">
      <v-card>
        <v-card-title>{{ vendorDialog.isEdit ? 'Edit' : 'Add' }} Vendor</v-card-title>
        <v-card-text>
          <v-form ref="vendorForm" v-model="vendorDialog.valid">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="vendorDialog.formData.vendor_code"
                  label="Vendor Code*"
                  :rules="[v => !!v || 'Vendor code is required']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="vendorDialog.formData.vendor_name"
                  label="Vendor Name*"
                  :rules="[v => !!v || 'Vendor name is required']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="vendorDialog.formData.contact_person"
                  label="Contact Person"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="vendorDialog.formData.email"
                  label="Email"
                  type="email"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="vendorDialog.formData.phone"
                  label="Phone"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="vendorDialog.formData.tax_id"
                  label="Tax ID"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="vendorDialog.formData.address_line1"
                  label="Address Line 1"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="vendorDialog.formData.address_line2"
                  label="Address Line 2"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="vendorDialog.formData.city"
                  label="City"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="vendorDialog.formData.state"
                  label="State"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="vendorDialog.formData.postal_code"
                  label="Postal Code"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="vendorDialog.formData.payment_terms"
                  label="Payment Terms"
                  :items="paymentTerms"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="vendorDialog.formData.currency_code"
                  label="Currency"
                  :items="currencies"
                  item-title="name"
                  item-value="code"
                ></v-select>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="vendorDialog.formData.notes"
                  label="Notes"
                  rows="3"
                ></v-textarea>
              </v-col>
              
              <v-col cols="12">
                <v-checkbox
                  v-model="vendorDialog.formData.is_active"
                  label="Active"
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="vendorDialog.show = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="vendorDialog.saving"
            :disabled="!vendorDialog.valid"
            @click="saveVendor"
          >
            {{ vendorDialog.isEdit ? 'Update' : 'Create' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { apiClient } from '@/utils/apiClient';

const { showSnackbar } = useSnackbar();

// Data
const loading = ref(false);
const vendors = ref([]);

const vendorDialog = reactive({
  show: false,
  isEdit: false,
  valid: false,
  saving: false,
  formData: {
    vendor_code: '',
    vendor_name: '',
    contact_person: '',
    email: '',
    phone: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
    tax_id: '',
    payment_terms: 'Net 30',
    currency_code: 'USD',
    is_active: true,
    notes: ''
  },
  editId: null
});

// Options
const paymentTerms = [
  'Net 15', 'Net 30', 'Net 45', 'Net 60', 'Due on Receipt', '2/10 Net 30'
];

const currencies = [
  { code: 'USD', name: 'US Dollar' },
  { code: 'EUR', name: 'Euro' },
  { code: 'GBP', name: 'British Pound' },
  { code: 'CAD', name: 'Canadian Dollar' }
];

const headers = [
  { title: 'Vendor', key: 'vendor_name', sortable: true },
  { title: 'Contact', key: 'contact', sortable: false },
  { title: 'Payment Terms', key: 'payment_terms', sortable: true },
  { title: 'Currency', key: 'currency_code', sortable: true },
  { title: 'Status', key: 'is_active', sortable: true },
  { title: 'Approval', key: 'is_approved', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
];

// Methods
const fetchVendors = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get('/api/v1/procurement/vendors');
    vendors.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load vendors', 'error');
    console.error('Error fetching vendors:', error);
  } finally {
    loading.value = false;
  }
};

const openVendorDialog = () => {
  vendorDialog.isEdit = false;
  vendorDialog.editId = null;
  vendorDialog.formData = {
    vendor_code: '',
    vendor_name: '',
    contact_person: '',
    email: '',
    phone: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
    tax_id: '',
    payment_terms: 'Net 30',
    currency_code: 'USD',
    is_active: true,
    notes: ''
  };
  vendorDialog.show = true;
};

const editVendor = (vendor) => {
  vendorDialog.isEdit = true;
  vendorDialog.editId = vendor.id;
  vendorDialog.formData = { ...vendor };
  vendorDialog.show = true;
};

const saveVendor = async () => {
  if (!vendorDialog.valid) return;
  
  vendorDialog.saving = true;
  try {
    if (vendorDialog.isEdit) {
      await apiClient.put(
        `/api/v1/procurement/vendors/${vendorDialog.editId}`,
        vendorDialog.formData
      );
      showSnackbar('Vendor updated successfully', 'success');
    } else {
      await apiClient.post('/api/v1/procurement/vendors', vendorDialog.formData);
      showSnackbar('Vendor created successfully', 'success');
    }
    
    vendorDialog.show = false;
    fetchVendors();
  } catch (error) {
    showSnackbar('Failed to save vendor', 'error');
    console.error('Save vendor error:', error);
  } finally {
    vendorDialog.saving = false;
  }
};

const approveVendor = async (vendor) => {
  try {
    await apiClient.put(`/api/v1/procurement/vendors/${vendor.id}`, {
      is_approved: true
    });
    showSnackbar('Vendor approved successfully', 'success');
    fetchVendors();
  } catch (error) {
    showSnackbar('Failed to approve vendor', 'error');
    console.error('Approve vendor error:', error);
  }
};

const viewPurchaseOrders = (vendor) => {
  // Navigate to purchase orders filtered by vendor
  console.log('View purchase orders for vendor:', vendor);
};

// Lifecycle
onMounted(() => {
  fetchVendors();
});
</script>

<style scoped>
.vendor-management {
  padding: 16px;
}
</style>