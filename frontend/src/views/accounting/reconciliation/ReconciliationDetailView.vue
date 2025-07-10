<template>
  <div v-if="loading" class="d-flex justify-center align-center" style="height: 400px;">
    <v-progress-circular indeterminate size="64"></v-progress-circular>
  </div>
  
  <div v-else-if="!reconciliation" class="text-center pa-8">
    <v-icon size="64" color="grey lighten-1">mdi-alert-circle-outline</v-icon>
    <h3 class="text-h6 mt-4">Reconciliation not found</h3>
    <v-btn color="primary" class="mt-4" @click="$router.push('/accounting/reconciliations')">
      Back to Reconciliations
    </v-btn>
  </div>
  
  <div v-else class="reconciliation-detail">
    <!-- Header -->
    <v-card class="mb-6">
      <v-card-title class="d-flex align-center">
        <v-btn
          icon
          class="mr-4"
          @click="$router.push('/accounting/reconciliations')"
        >
          <v-icon>mdi-arrow-left</v-icon>
        </v-btn>
        <span class="text-h5">Reconciliation: {{ reconciliation.reference }}</span>
        
        <v-spacer></v-spacer>
        
        <v-chip
          :color="getStatusColor(reconciliation.status)"
          class="mr-2"
          label
        >
          {{ formatStatus(reconciliation.status) }}
        </v-chip>
        
        <v-menu v-if="canEdit">
          <template v-slot:activator="{ props: menu }">
            <v-btn
              v-bind="menu"
              variant="text"
              icon="mdi-dots-vertical"
            ></v-btn>
          </template>
          
          <v-list>
            <v-list-item @click="exportReconciliation">
              <template v-slot:prepend>
                <v-icon>mdi-file-export</v-icon>
              </template>
              <v-list-item-title>Export</v-list-item-title>
            </v-list-item>
            
            <v-divider v-if="canEdit"></v-divider>
            
            <v-list-item 
              v-if="canEdit"
              @click="editReconciliation"
            >
              <template v-slot:prepend>
                <v-icon>mdi-pencil</v-icon>
              </template>
              <v-list-item-title>Edit</v-list-item-title>
            </v-list-item>
            
            <v-list-item 
              v-if="canDelete"
              @click="confirmDelete = true"
              class="text-error"
            >
              <template v-slot:prepend>
                <v-icon color="error">mdi-delete</v-icon>
              </template>
              <v-list-item-title>Delete</v-list-item-title>
            </v-list-item>
            
            <v-list-item 
              v-if="canComplete && reconciliation.status === 'IN_PROGRESS'"
              @click="completeReconciliation"
            >
              <template v-slot:prepend>
                <v-icon color="success">mdi-check-circle</v-icon>
              </template>
              <v-list-item-title>Mark as Complete</v-list-item-title>
            </v-list-item>
            
            <v-list-item 
              v-if="canReopen && reconciliation.status === 'COMPLETED'"
              @click="reopenReconciliation"
            >
              <template v-slot:prepend>
                <v-icon color="warning">mdi-backup-restore</v-icon>
              </template>
              <v-list-item-title>Reopen</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-card-title>
      
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <div class="text-subtitle-2 text-medium-emphasis">Account</div>
            <div class="text-body-1">{{ reconciliation.account?.name || 'N/A' }}</div>
          </v-col>
          <v-col cols="12" md="4">
            <div class="text-subtitle-2 text-medium-emphasis">Period</div>
            <div class="text-body-1">
              {{ formatDate(reconciliation.startDate) }} to {{ formatDate(reconciliation.endDate) }}
            </div>
          </v-col>
          <v-col cols="12" md="4">
            <div class="text-subtitle-2 text-medium-emphasis">Statement Reference</div>
            <div class="text-body-1">{{ reconciliation.statementReference || 'N/A' }}</div>
          </v-col>
        </v-row>
        
        <v-row class="mt-4">
          <v-col cols="12" md="4">
            <div class="text-subtitle-2 text-medium-emphasis">Statement Balance</div>
            <div class="text-h6">
              {{ formatCurrency(reconciliation.statementBalance, reconciliation.statementCurrency) }}
            </div>
          </v-col>
          <v-col cols="12" md="4">
            <div class="text-subtitle-2 text-medium-emphasis">Calculated Balance</div>
            <div class="text-h6">
              {{ formatCurrency(reconciliation.calculatedBalance, reconciliation.statementCurrency) }}
            </div>
          </v-col>
          <v-col cols="12" md="4">
            <div class="text-subtitle-2 text-medium-emphasis">Difference</div>
            <div 
              class="text-h6" 
              :class="getDifferenceClass(reconciliation.difference)"
            >
              {{ formatCurrency(reconciliation.difference, reconciliation.statementCurrency) }}
            </div>
          </v-col>
        </v-row>
        
        <v-row v-if="reconciliation.notes" class="mt-4">
          <v-col cols="12">
            <div class="text-subtitle-2 text-medium-emphasis">Notes</div>
            <div class="text-body-1">{{ reconciliation.notes }}</div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    
    <!-- Reconciliation Items -->
    <v-card class="mb-6">
      <v-card-title class="d-flex align-center">
        <span class="text-h6">Reconciliation Items</span>
        <v-spacer></v-spacer>
        <v-btn
          v-if="canEdit"
          color="primary"
          prepend-icon="mdi-plus"
          @click="showAddItemDialog = true"
        >
          Add Item
        </v-btn>
      </v-card-title>
      
      <v-card-text>
        <v-data-table
          :headers="itemHeaders"
          :items="reconciliationItems"
          :loading="loadingItems"
          :items-per-page="10"
          class="elevation-1"
        >
          <template v-slot:item.date="{ item }">
            {{ formatDate(item.date) }}
          </template>
          
          <template v-slot:item.amount="{ item }">
            {{ formatCurrency(item.amount, reconciliation.statementCurrency) }}
          </template>
          
          <template v-slot:item.type="{ item }">
            <v-chip :color="getItemTypeColor(item.type)" size="small">
              {{ formatItemType(item.type) }}
            </v-chip>
          </template>
          
          <template v-slot:item.status="{ item }">
            <v-chip :color="getItemStatusColor(item.status)" size="small">
              {{ formatItemStatus(item.status) }}
            </v-chip>
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-tooltip location="top">
              <template v-slot:activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon
                  size="small"
                  variant="text"
                  color="primary"
                  @click="viewItem(item)"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
              </template>
              <span>View Details</span>
            </v-tooltip>
            
            <v-tooltip v-if="canEdit" location="top">
              <template v-slot:activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon
                  size="small"
                  variant="text"
                  color="warning"
                  @click="editItem(item)"
                >
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
              </template>
              <span>Edit</span>
            </v-tooltip>
            
            <v-tooltip v-if="canEdit" location="top">
              <template v-slot:activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon
                  size="small"
                  variant="text"
                  color="error"
                  @click="confirmDeleteItem = item"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>
              <span>Delete</span>
            </v-tooltip>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
    
    <!-- Audit Logs -->
    <v-card>
      <v-card-title class="text-h6">
        Audit Log
      </v-card-title>
      
      <v-card-text>
        <v-timeline density="compact" align="start">
          <v-timeline-item
            v-for="log in auditLogs"
            :key="log.id"
            :dot-color="getLogColor(log.action)"
            size="small"
          >
            <div class="d-flex justify-space-between">
              <div>
                <strong>{{ log.action }}</strong>
                <div class="text-caption">{{ log.description }}</div>
              </div>
              <div class="text-caption text-medium-emphasis">
                {{ formatDateTime(log.createdAt) }}
              </div>
            </div>
            <div v-if="log.details" class="text-caption text-medium-emphasis mt-1">
              {{ log.details }}
            </div>
            <div class="text-caption mt-1">
              By {{ log.user?.name || 'System' }}
            </div>
          </v-timeline-item>
        </v-timeline>
      </v-card-text>
    </v-card>
    
    <!-- Add/Edit Item Dialog -->
    <v-dialog v-model="showItemDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ editingItem ? 'Edit' : 'Add' }} Reconciliation Item</span>
        </v-card-title>
        
        <v-card-text>
          <v-form ref="itemForm" v-model="validItemForm">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="itemForm.reference"
                  label="Reference"
                  :rules="[v => !!v || 'Reference is required']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-menu
                  v-model="itemDateMenu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template v-slot:activator="{ props }">
                    <v-text-field
                      v-model="itemForm.date"
                      label="Date"
                      readonly
                      v-bind="props"
                      :rules="[v => !!v || 'Date is required']"
                      required
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="itemForm.date"
                    @input="itemDateMenu = false"
                  ></v-date-picker>
                </v-menu>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="itemForm.amount"
                  label="Amount"
                  type="number"
                  step="0.01"
                  :rules="[v => !!v || 'Amount is required', v => v > 0 || 'Amount must be greater than 0']"
                  required
                  prefix="$"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="itemForm.type"
                  :items="itemTypes"
                  label="Type"
                  :rules="[v => !!v || 'Type is required']"
                  required
                ></v-select>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="itemForm.description"
                  label="Description"
                  rows="2"
                ></v-textarea>
              </v-col>
              
              <v-col cols="12">
                <v-checkbox
                  v-model="itemForm.isReconciled"
                  label="Mark as reconciled"
                  hide-details
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" text @click="showItemDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="saveItem" :loading="savingItem">
            {{ editingItem ? 'Update' : 'Add' }} Item
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="confirmDelete" max-width="400px">
      <v-card>
        <v-card-title class="text-h6">Confirm Delete</v-card-title>
        <v-card-text>
          Are you sure you want to delete this reconciliation? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" text @click="confirmDelete = false">Cancel</v-btn>
          <v-btn color="primary" @click="deleteReconciliation" :loading="deleting">
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Delete Item Confirmation Dialog -->
    <v-dialog v-model="!!confirmDeleteItem" max-width="400px">
      <v-card>
        <v-card-title class="text-h6">Delete Item</v-card-title>
        <v-card-text>
          Are you sure you want to delete this item? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" text @click="confirmDeleteItem = null">Cancel</v-btn>
          <v-btn color="primary" @click="deleteItem" :loading="deletingItem">
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { format, parseISO } from 'date-fns';
import reconciliationService from '@/services/accounting/reconciliationService';

const route = useRoute();
const router = useRouter();
const toast = useToast();

// Data
const loading = ref(true);
const loadingItems = ref(false);
const savingItem = ref(false);
const deleting = ref(false);
const deletingItem = ref(false);
const reconciliation = ref(null);
const reconciliationItems = ref([]);
const auditLogs = ref([]);
const showItemDialog = ref(false);
const showAddItemDialog = ref(false);
const confirmDelete = ref(false);
const confirmDeleteItem = ref(null);
const itemDateMenu = ref(false);
const validItemForm = ref(false);
const editingItem = ref(null);

// Form data
const itemForm = ref({
  reference: '',
  date: format(new Date(), 'yyyy-MM-dd'),
  amount: 0,
  type: 'CHECK',
  description: '',
  isReconciled: true
});

// Table headers
const itemHeaders = [
  { title: 'Reference', key: 'reference', sortable: true },
  { title: 'Date', key: 'date', sortable: true },
  { title: 'Description', key: 'description', sortable: true },
  { title: 'Type', key: 'type', sortable: true },
  { title: 'Amount', key: 'amount', sortable: true, align: 'end' },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
];

// Item types
const itemTypes = [
  { title: 'Check', value: 'CHECK' },
  { title: 'Deposit', value: 'DEPOSIT' },
  { title: 'Service Charge', value: 'SERVICE_CHARGE' },
  { title: 'Interest', value: 'INTEREST' },
  { title: 'Adjustment', value: 'ADJUSTMENT' },
  { title: 'Other', value: 'OTHER' }
];

// Computed properties
const canEdit = computed(() => {
  return reconciliation.value && 
         (reconciliation.value.status === 'DRAFT' || reconciliation.value.status === 'IN_PROGRESS');
});

const canDelete = computed(() => {
  return reconciliation.value && reconciliation.value.status === 'DRAFT';
});

const canComplete = computed(() => {
  return reconciliation.value && reconciliation.value.status === 'IN_PROGRESS';
});

const canReopen = computed(() => {
  return reconciliation.value && reconciliation.value.status === 'COMPLETED';
});

// Methods
const fetchReconciliation = async () => {
  try {
    loading.value = true;
    const response = await reconciliationService.getReconciliation(route.params.id);
    reconciliation.value = response;
    fetchReconciliationItems();
    fetchAuditLogs();
  } catch (error) {
    console.error('Error fetching reconciliation:', error);
    toast.error('Failed to load reconciliation');
  } finally {
    loading.value = false;
  }
};

const fetchReconciliationItems = async () => {
  try {
    loadingItems.value = true;
    const response = await reconciliationService.getReconciliationItems(route.params.id);
    reconciliationItems.value = response.items || [];
  } catch (error) {
    console.error('Error fetching reconciliation items:', error);
    toast.error('Failed to load reconciliation items');
  } finally {
    loadingItems.value = false;
  }
};

const fetchAuditLogs = async () => {
  try {
    const response = await reconciliationService.getReconciliationAuditLogs(route.params.id);
    auditLogs.value = response || [];
  } catch (error) {
    console.error('Error fetching audit logs:', error);
    toast.error('Failed to load audit logs');
  }
};

const editReconciliation = () => {
  router.push(`/accounting/reconciliations/${route.params.id}/edit`);
};

const deleteReconciliation = async () => {
  try {
    deleting.value = true;
    await reconciliationService.deleteReconciliation(route.params.id);
    toast.success('Reconciliation deleted successfully');
    router.push('/accounting/reconciliations');
  } catch (error) {
    console.error('Error deleting reconciliation:', error);
    toast.error('Failed to delete reconciliation');
  } finally {
    deleting.value = false;
    confirmDelete.value = false;
  }
};

const completeReconciliation = async () => {
  try {
    await reconciliationService.completeReconciliation(route.params.id);
    toast.success('Reconciliation marked as complete');
    fetchReconciliation();
  } catch (error) {
    console.error('Error completing reconciliation:', error);
    toast.error(error.response?.data?.message || 'Failed to complete reconciliation');
  }
};

const reopenReconciliation = async () => {
  try {
    await reconciliationService.reopenReconciliation(route.params.id);
    toast.success('Reconciliation reopened');
    fetchReconciliation();
  } catch (error) {
    console.error('Error reopening reconciliation:', error);
    toast.error('Failed to reopen reconciliation');
  }
};

const exportReconciliation = async () => {
  try {
    const response = await reconciliationService.portReconciliation(route.params.id, 'pdf');
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `reconciliation-${route.params.id}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    toast.success('Export started successfully');
  } catch (error) {
    console.error('Error exporting reconciliation:', error);
    toast.error('Failed to export reconciliation');
  }
};

const addItem = () => {
  editingItem.value = null;
  itemForm.value = {
    reference: '',
    date: format(new Date(), 'yyyy-MM-dd'),
    amount: 0,
    type: 'CHECK',
    description: '',
    isReconciled: true
  };
  showItemDialog.value = true;
};

const editItem = (item) => {
  editingItem.value = item;
  itemForm.value = {
    reference: item.reference,
    date: format(new Date(item.date), 'yyyy-MM-dd'),
    amount: Math.abs(item.amount),
    type: item.type,
    description: item.description,
    isReconciled: item.status === 'RECONCILED'
  };
  showItemDialog.value = true;
};

const viewItem = (item) => {
  // Implement view item details if needed
  console.log('View item:', item);
};

const saveItem = async () => {
  if (!validItemForm.value) return;
  
  try {
    savingItem.value = true;
    const itemData = {
      ...itemForm.value,
      amount: parseFloat(itemForm.value.amount),
      status: itemForm.value.isReconciled ? 'RECONCILED' : 'PENDING'
    };
    
    if (editingItem.value) {
      await reconciliationService.updateReconciliationItem(
        route.params.id,
        editingItem.value.id,
        itemData
      );
      toast.success('Item updated successfully');
    } else {
      await reconciliationService.addReconciliationItem(route.params.id, itemData);
      toast.success('Item added successfully');
    }
    
    showItemDialog.value = false;
    fetchReconciliationItems();
  } catch (error) {
    console.error('Error saving reconciliation item:', error);
    toast.error(error.response?.data?.message || 'Failed to save item');
  } finally {
    savingItem.value = false;
  }
};

const deleteItem = async () => {
  if (!confirmDeleteItem.value) return;
  
  try {
    deletingItem.value = true;
    await reconciliationService.deleteReconciliationItem(
      route.params.id,
      confirmDeleteItem.value.id
    );
    
    toast.success('Item deleted successfully');
    fetchReconciliationItems();
  } catch (error) {
    console.error('Error deleting reconciliation item:', error);
    toast.error('Failed to delete item');
  } finally {
    deletingItem.value = false;
    confirmDeleteItem.value = null;
  }
};

// Formatting helpers
const formatDate = (date) => {
  if (!date) return 'N/A';
  return format(parseISO(date), 'MMM d, yyyy');
};

const formatDateTime = (dateTime) => {
  if (!dateTime) return 'N/A';
  return format(parseISO(dateTime), 'MMM d, yyyy h:mm a');
};

const formatCurrency = (amount, currency = 'USD') => {
  if (amount === null || amount === undefined) return '';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency || 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
};

const formatStatus = (status) => {
  const statusMap = {
    DRAFT: 'Draft',
    IN_PROGRESS: 'In Progress',
    COMPLETED: 'Completed',
    VOIDED: 'Voided'
  };
  return statusMap[status] || status;
};

const formatItemType = (type) => {
  const typeMap = {
    CHECK: 'Check',
    DEPOSIT: 'Deposit',
    SERVICE_CHARGE: 'Service Charge',
    INTEREST: 'Interest',
    ADJUSTMENT: 'Adjustment',
    OTHER: 'Other'
  };
  return typeMap[type] || type;
};

const formatItemStatus = (status) => {
  const statusMap = {
    PENDING: 'Pending',
    RECONCILED: 'Reconciled',
    VOIDED: 'Voided'
  };
  return statusMap[status] || status;
};

// Color helpers
const getStatusColor = (status) => {
  const colors = {
    DRAFT: 'grey',
    IN_PROGRESS: 'blue',
    COMPLETED: 'success',
    VOIDED: 'error'
  };
  return colors[status] || 'default';
};

const getItemTypeColor = (type) => {
  const colors = {
    CHECK: 'indigo',
    DEPOSIT: 'teal',
    SERVICE_CHARGE: 'orange',
    INTEREST: 'green',
    ADJUSTMENT: 'purple',
    OTHER: 'grey'
  };
  return colors[type] || 'default';
};

const getItemStatusColor = (status) => {
  const colors = {
    PENDING: 'warning',
    RECONCILED: 'success',
    VOIDED: 'error'
  };
  return colors[status] || 'default';
};

const getLogColor = (action) => {
  if (action.includes('CREATE')) return 'green';
  if (action.includes('UPDATE')) return 'blue';
  if (action.includes('DELETE')) return 'red';
  if (action.includes('COMPLETE')) return 'success';
  if (action.includes('REOPEN')) return 'warning';
  return 'grey';
};

const getDifferenceClass = (difference) => {
  if (difference > 0) return 'text-success';
  if (difference < 0) return 'text-error';
  return '';
};

// Lifecycle hooks
onMounted(() => {
  if (route.params.id) {
    fetchReconciliation();
  } else {
    loading.value = false;
  }
});
</script>

<style scoped>
.reconciliation-detail {
  padding: 20px;
}

.text-success {
  color: #4CAF50;
  font-weight: 500;
}

.text-error {
  color: #F44336;
  font-weight: 500;
}

.text-warning {
  color: #FF9800;
  font-weight: 500;
}

.v-card {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.v-card-title {
  padding: 16px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

.v-card-text {
  padding: 16px 24px;
}

.v-timeline-item {
  min-height: 60px;
}

.v-timeline-divider {
  padding: 0;
}

.v-timeline-item__body {
  padding-bottom: 16px;
}

.v-data-table {
  margin-top: 16px;
}

.v-dialog .v-card {
  border-radius: 8px;
}

.v-dialog .v-card-title {
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.v-dialog .v-card-actions {
  padding: 16px 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.12);
}
</style>
