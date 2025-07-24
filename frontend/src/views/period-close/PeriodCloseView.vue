<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <h2>Period Close Management</h2>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              @click="openPeriodDialog()"
            >
              New Period
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-data-table
              :headers="periodHeaders"
              :items="periods"
              :loading="loading"
              class="elevation-1"
            >
              <template v-slot:item.period_type="{ item }">
                <v-chip
                  :color="getTypeColor(item.period_type)"
                  size="small"
                >
                  {{ item.period_type.toUpperCase() }}
                </v-chip>
              </template>
              
              <template v-slot:item.status="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  size="small"
                >
                  {{ item.status.toUpperCase() }}
                </v-chip>
              </template>
              
              <template v-slot:item.start_date="{ item }">
                {{ formatDate(item.start_date) }}
              </template>
              
              <template v-slot:item.end_date="{ item }">
                {{ formatDate(item.end_date) }}
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn
                  v-if="item.status === 'open'"
                  icon
                  variant="text"
                  @click="initiatePeriodClose(item)"
                >
                  <v-icon>mdi-lock</v-icon>
                </v-btn>
                <v-btn
                  v-if="item.status === 'closing'"
                  icon
                  variant="text"
                  @click="viewPeriodClose(item)"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Period Dialog -->
    <v-dialog v-model="periodDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="text-h5">New Accounting Period</span>
        </v-card-title>
        
        <v-card-text>
          <v-form ref="periodForm">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="editedPeriod.period_name"
                  label="Period Name"
                  :rules="[v => !!v || 'Period name is required']"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-select
                  v-model="editedPeriod.period_type"
                  :items="periodTypes"
                  label="Period Type"
                  :rules="[v => !!v || 'Period type is required']"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedPeriod.start_date"
                  label="Start Date"
                  type="date"
                  :rules="[v => !!v || 'Start date is required']"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedPeriod.end_date"
                  label="End Date"
                  type="date"
                  :rules="[v => !!v || 'End date is required']"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="blue-darken-1"
            variant="text"
            @click="closePeriodDialog"
          >
            Cancel
          </v-btn>
          <v-btn
            color="blue-darken-1"
            variant="text"
            @click="savePeriod"
            :loading="saving"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { ref, onMounted } from 'vue';
import { format } from 'date-fns';
import periodCloseService from '@/services/periodCloseService';
import { useSnackbar } from '@/composables/useSnackbar';

export default {
  name: 'PeriodCloseView',
  
  setup() {
    const { showSnackbar } = useSnackbar();
    
    const periodHeaders = [
      { title: 'Period Name', key: 'period_name', sortable: true },
      { title: 'Type', key: 'period_type', sortable: true },
      { title: 'Start Date', key: 'start_date', sortable: true },
      { title: 'End Date', key: 'end_date', sortable: true },
      { title: 'Status', key: 'status', sortable: true },
      { title: 'Actions', key: 'actions', sortable: false }
    ];
    
    const periods = ref([]);
    const loading = ref(false);
    const saving = ref(false);
    
    const periodDialog = ref(false);
    
    const editedPeriod = ref({
      period_name: '',
      period_type: 'monthly',
      start_date: '',
      end_date: ''
    });
    
    const periodForm = ref(null);
    
    const periodTypes = ['monthly', 'quarterly', 'yearly'];
    
    const loadPeriods = async () => {
      loading.value = true;
      try {
        const response = await periodCloseService.listAccountingPeriods();
        periods.value = response.data;
      } catch (error) {
        console.error('Failed to load periods:', error);
        showSnackbar('Failed to load periods', 'error');
      } finally {
        loading.value = false;
      }
    };
    
    const openPeriodDialog = () => {
      editedPeriod.value = {
        period_name: '',
        period_type: 'monthly',
        start_date: '',
        end_date: ''
      };
      periodDialog.value = true;
    };
    
    const closePeriodDialog = () => {
      periodDialog.value = false;
    };
    
    const savePeriod = async () => {
      if (!periodForm.value.validate()) return;
      
      saving.value = true;
      try {
        await periodCloseService.createAccountingPeriod({
          ...editedPeriod.value,
          start_date: new Date(editedPeriod.value.start_date),
          end_date: new Date(editedPeriod.value.end_date)
        });
        
        showSnackbar('Period created successfully', 'success');
        closePeriodDialog();
        loadPeriods();
      } catch (error) {
        console.error('Failed to save period:', error);
        showSnackbar(`Failed to save period: ${error.response?.data?.detail || error.message}`, 'error');
      } finally {
        saving.value = false;
      }
    };
    
    const initiatePeriodClose = async (period) => {
      try {
        await periodCloseService.initiatePeriodClose(period.id);
        showSnackbar('Period close initiated successfully', 'success');
        loadPeriods();
      } catch (error) {
        console.error('Failed to initiate close:', error);
        showSnackbar(`Failed to initiate close: ${error.response?.data?.detail || error.message}`, 'error');
      }
    };
    
    const viewPeriodClose = (period) => {
      // Navigate to close details view
      console.log('View period close:', period);
    };
    
    const getTypeColor = (type) => {
      const colors = {
        monthly: 'primary',
        quarterly: 'success',
        yearly: 'warning'
      };
      return colors[type] || 'grey';
    };
    
    const getStatusColor = (status) => {
      const colors = {
        open: 'success',
        closing: 'warning',
        closed: 'error',
        reopened: 'info'
      };
      return colors[status] || 'grey';
    };
    
    const formatDate = (dateString) => {
      if (!dateString) return '';
      return format(new Date(dateString), 'MMM dd, yyyy');
    };
    
    onMounted(() => {
      loadPeriods();
    });
    
    return {
      periodHeaders,
      periods,
      loading,
      saving,
      periodDialog,
      editedPeriod,
      periodForm,
      periodTypes,
      loadPeriods,
      openPeriodDialog,
      closePeriodDialog,
      savePeriod,
      initiatePeriodClose,
      viewPeriodClose,
      getTypeColor,
      getStatusColor,
      formatDate
    };
  }
};
</script>