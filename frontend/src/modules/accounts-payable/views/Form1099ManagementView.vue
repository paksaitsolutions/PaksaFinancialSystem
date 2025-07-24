<template>
  <div class="form-1099-management">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4 mb-4">1099 Reporting</h1>
          
          <v-card v-if="selectedForm">
            <v-card-text class="pa-0">
              <div class="d-flex align-center px-4 py-2 bg-grey-lighten-4">
                <v-btn
                  variant="text"
                  prepend-icon="mdi-arrow-left"
                  @click="clearSelection"
                >
                  Back to List
                </v-btn>
                <v-spacer></v-spacer>
                <div class="text-h6">1099 Form - {{ selectedForm.vendor?.name }} ({{ selectedForm.tax_year }})</div>
              </div>
              
              <!-- 1099 form detail view would go here -->
              <div class="pa-4">
                <p>1099 form detail view will be implemented here.</p>
              </div>
            </v-card-text>
          </v-card>
          
          <v-card v-else-if="isCreating">
            <v-card-text class="pa-0">
              <div class="d-flex align-center px-4 py-2 bg-grey-lighten-4">
                <v-btn
                  variant="text"
                  prepend-icon="mdi-arrow-left"
                  @click="clearSelection"
                >
                  Back to List
                </v-btn>
                <v-spacer></v-spacer>
                <div class="text-h6">Create New 1099 Form</div>
              </div>
              
              <!-- 1099 form creation would go here -->
              <div class="pa-4">
                <p>1099 form creation will be implemented here.</p>
              </div>
            </v-card-text>
          </v-card>
          
          <div v-else>
            <v-tabs v-model="activeTab" bg-color="primary">
              <v-tab value="current">Current Year</v-tab>
              <v-tab value="all">All Forms</v-tab>
              <v-tab value="filed">Filed</v-tab>
              <v-tab value="summary">Summary</v-tab>
            </v-tabs>
            
            <v-window v-model="activeTab" class="mt-4">
              <v-window-item value="current">
                <form-1099-list
                  :default-filters="{ taxYear: currentYear }"
                  @view="viewForm"
                  @create="createForm"
                />
              </v-window-item>
              
              <v-window-item value="all">
                <form-1099-list
                  @view="viewForm"
                  @create="createForm"
                />
              </v-window-item>
              
              <v-window-item value="filed">
                <form-1099-list
                  :default-filters="{ status: 'filed' }"
                  @view="viewForm"
                  @create="createForm"
                />
              </v-window-item>
              
              <v-window-item value="summary">
                <v-card>
                  <v-card-title>1099 Summary</v-card-title>
                  <v-card-text>
                    <v-row>
                      <v-col cols="12" md="4">
                        <v-select
                          v-model="summaryYear"
                          label="Tax Year"
                          :items="taxYearOptions"
                          @update:model-value="fetchSummary"
                        ></v-select>
                      </v-col>
                    </v-row>
                    
                    <div v-if="summary" class="mt-4">
                      <v-row>
                        <v-col cols="12" md="3">
                          <v-card variant="outlined">
                            <v-card-text class="text-center">
                              <div class="text-h4 text-primary">{{ summary.total_forms }}</div>
                              <div class="text-subtitle-1">Total Forms</div>
                            </v-card-text>
                          </v-card>
                        </v-col>
                        
                        <v-col cols="12" md="3">
                          <v-card variant="outlined">
                            <v-card-text class="text-center">
                              <div class="text-h4 text-success">{{ formatCurrency(summary.total_amount) }}</div>
                              <div class="text-subtitle-1">Total Amount</div>
                            </v-card-text>
                          </v-card>
                        </v-col>
                        
                        <v-col cols="12" md="3">
                          <v-card variant="outlined">
                            <v-card-title>By Status</v-card-title>
                            <v-card-text>
                              <div v-for="(count, status) in summary.forms_by_status" :key="status" class="d-flex justify-space-between">
                                <span>{{ formatStatus(status) }}:</span>
                                <span>{{ count }}</span>
                              </div>
                            </v-card-text>
                          </v-card>
                        </v-col>
                        
                        <v-col cols="12" md="3">
                          <v-card variant="outlined">
                            <v-card-title>By Type</v-card-title>
                            <v-card-text>
                              <div v-for="(count, type) in summary.forms_by_type" :key="type" class="d-flex justify-space-between">
                                <span>{{ type }}:</span>
                                <span>{{ count }}</span>
                              </div>
                            </v-card-text>
                          </v-card>
                        </v-col>
                      </v-row>
                    </div>
                  </v-card-text>
                </v-card>
              </v-window-item>
            </v-window>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { formatCurrency } from '@/utils/formatters';
import { apiClient } from '@/utils/apiClient';
import Form1099List from '../components/form-1099/Form1099List.vue';

// Composables
const { showSnackbar } = useSnackbar();

// Data
const activeTab = ref('current');
const selectedForm = ref(null);
const isCreating = ref(false);
const currentYear = new Date().getFullYear();
const summaryYear = ref(currentYear);
const summary = ref(null);

// Options
const taxYearOptions = Array.from({ length: 10 }, (_, i) => currentYear - i);

// Methods
const viewForm = (form) => {
  selectedForm.value = form;
  isCreating.value = false;
};

const createForm = () => {
  selectedForm.value = null;
  isCreating.value = true;
};

const clearSelection = () => {
  selectedForm.value = null;
  isCreating.value = false;
};

const fetchSummary = async () => {
  try {
    const response = await apiClient.get(`/api/v1/accounts-payable/1099/summary/${summaryYear.value}`);
    summary.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load 1099 summary', 'error');
    console.error('Error fetching 1099 summary:', error);
  }
};

const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1);
};

// Lifecycle hooks
onMounted(() => {
  fetchSummary();
});
</script>

<style scoped>
.form-1099-management {
  padding: 16px;
}
</style>