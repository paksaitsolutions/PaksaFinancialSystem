<template>
  <v-container fluid class="fill-height">
    <v-card class="flex-grow-1 d-flex flex-column">
      <v-card-title class="d-flex align-center">
        <span class="text-h5">Tax Exemption Certificates</span>
        <v-spacer />
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
          class="mr-4"
          style="max-width: 300px;"
          @input="debouncedSearch"
        />
        <v-btn
          color="primary"
          @click="openDialog()"
        >
          <v-icon left>mdi-plus</v-icon>
          New Certificate
        </v-btn>
      </v-card-title>
      
      <v-card-text class="pa-0 flex-grow-1" style="height: 0;">
        <v-data-table
          :headers="headers"
          :items="certificates"
          :loading="loading"
          :options.sync="options"
          :server-items-length="totalItems"
          :footer-props="{
            'items-per-page-options': [10, 25, 50, 100],
          }"
          class="elevation-1 flex-grow-1"
          fixed-header
          height="100%"
          calculate-widths
          @update:options="loadItems"
        >
          <template v-slot:item.customer="{ item }">
            <div class="d-flex flex-column">
              <div>{{ item.customer_name }}</div>
              <div class="caption text--secondary">{{ item.customer_tax_id }}</div>
            </div>
          </template>
          
          <template v-slot:item.validity="{ item }">
            <div class="d-flex flex-column">
              <div>Issued: {{ formatDate(item.issue_date) }}</div>
              <div :class="getExpiryClass(item.expiry_date)">
                Expires: {{ formatDate(item.expiry_date) }}
              </div>
            </div>
          </template>
          
          <template v-slot:item.tax_codes="{ item }">
            <v-chip
              v-for="(code, index) in item.tax_codes"
              :key="index"
              x-small
              class="mr-1 mb-1"
            >
              {{ code }}
            </v-chip>
          </template>
          
          <template v-slot:item.is_active="{ item }">
            <v-chip
              :color="item.is_active ? 'success' : 'error'"
              dark
              x-small
            >
              {{ item.is_active ? 'Active' : 'Inactive' }}
            </v-chip>
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <v-icon
                  small
                  class="mr-2"
                  v-bind="attrs"
                  v-on="on"
                  @click="downloadCertificate(item)"
                >
                  mdi-download
                </v-icon>
              </template>
              <span>Download Certificate</span>
            </v-tooltip>
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <v-icon
                  small
                  class="mr-2"
                  v-bind="attrs"
                  v-on="on"
                  @click="openDialog(item)"
                >
                  mdi-pencil
                </v-icon>
              </template>
              <span>Edit Certificate</span>
            </v-tooltip>
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <v-icon
                  small
                  v-bind="attrs"
                  v-on="on"
                  @click="confirmDelete(item)"
                >
                  mdi-delete
                </v-icon>
              </template>
              <span>Delete</span>
            </v-tooltip>
            
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <v-icon
                  small
                  class="ml-2"
                  v-bind="attrs"
                  v-on="on"
                  @click="downloadCertificate(item)"
                >
                  mdi-download
                </v-icon>
              </template>
              <span>Download</span>
            </v-tooltip>
          </template>
          
          <template v-slot:no-data>
            <div class="text-center py-4">
              <div class="mb-2">No tax exemption certificates found</div>
              <v-btn
                color="primary"
                small
                @click="openDialog()"
              >
                <v-icon left small>mdi-plus</v-icon>
                Add Certificate
              </v-btn>
            </div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
    
    <!-- Certificate Dialog -->
    <TaxExemptionCertificateDialog
      v-model="dialog"
      :certificate="editedItem"
      :loading="dialogLoading"
      @close="closeDialog"
      @save="saveCertificate"
    />
    
    <!-- Delete Confirmation Dialog -->
    <ConfirmationDialog
      v-model="deleteDialog"
      title="Delete Certificate"
      :loading="deleteLoading"
      @confirm="deleteItemConfirm"
    >
      <template v-slot:content>
        Are you sure you want to delete this certificate?
        <div class="text-subtitle-1 mt-2">
          <strong>Certificate Number:</strong> {{ editedItem.certificate_number }}
        </div>
        <div class="text-subtitle-1">
          <strong>Customer:</strong> {{ editedItem.customer_name }}
        </div>
        <div class="text-caption text--secondary mt-2">
          This action cannot be undone.
        </div>
      </template>
    </ConfirmationDialog>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch } from 'vue';
import { useApi } from '@/composables/useApi';
import { useSnackbar } from '@/composables/useSnackbar';
import { useTaxPolicyStore } from '@/stores/taxPolicy';
import { format } from 'date-fns';
import { debounce } from 'lodash-es';
import TaxExemptionCertificateDialog from '@/components/tax/TaxExemptionCertificateDialog.vue';
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue';

export default defineComponent({
  name: 'TaxExemptionCertificatesView',
  
  components: {
    TaxExemptionCertificateDialog,
    ConfirmationDialog,
  },
  
  setup() {
    const { get, post, del } = useApi();
    const { showSuccess, showError } = useSnackbar();
    const taxPolicyStore = useTaxPolicyStore();
    
    const loading = ref(false);
    const dialog = ref(false);
    const dialogLoading = ref(false);
    const deleteDialog = ref(false);
    const deleteLoading = ref(false);
    const search = ref('');
    const certificates = ref<any[]>([]);
    const totalItems = ref(0);
    const editedItem = ref<any>({
      certificate_number: '',
      customer_id: null,
      customer_tax_id: '',
      customer_name: '',
      exemption_type: '',
      issuing_jurisdiction: '',
      issue_date: new Date().toISOString().substr(0, 10),
      expiry_date: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString().substr(0, 10),
      tax_codes: [],
      notes: '',
      is_active: true,
    });
    const defaultItem = { ...editedItem.value };
    
    const options = ref({
      page: 1,
      itemsPerPage: 10,
      sortBy: ['issue_date'],
      sortDesc: [true],
    });
    
    const headers = [
      { text: 'Certificate Number', value: 'certificate_number', width: '15%' },
      { text: 'Customer', value: 'customer', width: '20%' },
      { text: 'Exemption Type', value: 'exemption_type', width: '15%' },
      { text: 'Jurisdiction', value: 'issuing_jurisdiction', width: '15%' },
      { text: 'Validity', value: 'validity', width: '20%' },
      { text: 'Tax Codes', value: 'tax_codes', width: '10%' },
      { text: 'Status', value: 'is_active', align: 'center', width: '10%' },
      { text: 'Actions', value: 'actions', sortable: false, align: 'center', width: '10%' },
    ];
    
    const loadItems = async () => {
      try {
        loading.value = true;
        const { sortBy, sortDesc, page, itemsPerPage } = options.value;
        
        const params: any = {
          page,
          limit: itemsPerPage,
          search: search.value || undefined,
        };
        
        if (sortBy && sortBy.length > 0) {
          params.sort_by = sortBy[0];
          params.sort_order = sortDesc[0] ? 'desc' : 'asc';
        }
        
        const response = await get('/api/tax/exemption-certificates', { params });
        certificates.value = response.data.items || [];
        totalItems.value = response.data.total || 0;
      } catch (error) {
        showError('Failed to load tax exemption certificates');
        console.error('Error loading tax exemption certificates:', error);
      } finally {
        loading.value = false;
      }
    };
    
    const debouncedSearch = debounce(() => {
      loadItems();
    }, 500);
    
    const openDialog = (item: any = null) => {
      if (item) {
        // Create a deep copy of the item to edit
        editedItem.value = JSON.parse(JSON.stringify(item));
      } else {
        // Reset to default for new item
        editedItem.value = { ...defaultItem };
        editedItem.value.issue_date = new Date().toISOString().substr(0, 10);
        editedItem.value.expiry_date = new Date(new Date().setFullYear(new Date().getFullYear() + 1))
          .toISOString()
          .substr(0, 10);
      }
      dialog.value = true;
    };
    
    const downloadCertificate = async (certificate: any) => {
      try {
        loading.value = true;
        const filename = `tax_exemption_certificate_${certificate.certificate_number || certificate.id}.pdf`;
        await taxPolicyStore.downloadTaxExemptionCertificate(certificate.id, filename);
        showSuccess('Certificate downloaded successfully');
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to download certificate';
        showError(errorMessage);
      } finally {
        loading.value = false;
      }
    };
    
    const closeDialog = () => {
      dialog.value = false;
      setTimeout(() => {
        editedItem.value = { ...defaultItem };
      }, 300);
    };
    
    const saveCertificate = async (data: any) => {
      try {
        dialogLoading.value = true;
        const isEdit = !!data.id;
        
        if (isEdit) {
          await post(`/api/tax/exemption-certificates/${data.id}`, data);
          showSuccess('Certificate updated successfully');
        } else {
          await post('/api/tax/exemption-certificates', data);
          showSuccess('Certificate created successfully');
        }
        
        closeDialog();
        loadItems();
      } catch (error) {
        const action = data.id ? 'updating' : 'creating';
        showError(`Error ${action} certificate`);
        console.error(`Error ${action} certificate:`, error);
      } finally {
        dialogLoading.value = false;
      }
    };
    
    const confirmDelete = (item: any) => {
      editedItem.value = { ...item };
      deleteDialog.value = true;
    };
    
    const deleteItemConfirm = async () => {
      try {
        deleteLoading.value = true;
        await del(`/api/tax/exemption-certificates/${editedItem.value.id}`);
        showSuccess('Certificate deleted successfully');
        loadItems();
      } catch (error) {
        showError('Error deleting certificate');
        console.error('Error deleting certificate:', error);
      } finally {
        deleteLoading.value = false;
        deleteDialog.value = false;
      }
    };
    
    const downloadCertificate = async (item: any) => {
      try {
        const filename = `tax-exemption-certificate-${item.certificate_number || item.id}.pdf`;
        await taxPolicyStore.downloadTaxExemptionCertificate(item.id, filename);
        showSuccess('Certificate downloaded successfully');
      } catch (error: any) {
        console.error('Error downloading certificate:', error);
        showError(error?.message || 'Failed to download certificate');
      }
    };
    
    const formatDate = (dateString: string) => {
      if (!dateString) return 'N/A';
      return format(new Date(dateString), 'MMM d, yyyy');
    };
    
    const getExpiryClass = (expiryDate: string) => {
      if (!expiryDate) return '';
      
      const expiry = new Date(expiryDate);
      const today = new Date();
      const oneMonthFromNow = new Date();
      oneMonthFromNow.setMonth(oneMonthFromNow.getMonth() + 1);
      
      if (expiry < today) {
        return 'error--text';
      } else if (expiry < oneMonthFromNow) {
        return 'warning--text';
      }
      return '';
    };
    
    // Watch for options changes to reload data
    watch(
      () => [options.value],
      () => {
        loadItems();
      },
      { deep: true }
    );
    
    // Initial load
    onMounted(() => {
      loadItems();
    });
    
    return {
      loading,
      dialog,
      dialogLoading,
      deleteDialog,
      deleteLoading,
      search,
      certificates,
      totalItems,
      options,
      headers,
      editedItem,
      debouncedSearch,
      loadItems,
      openDialog,
      closeDialog,
      saveCertificate,
      confirmDelete,
      deleteItemConfirm,
      downloadCertificate,
      formatDate,
      getExpiryClass,
    };
  },
});
</script>
