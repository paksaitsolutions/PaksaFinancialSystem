<template>
  <div class="chart-of-accounts">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h3>Chart of Accounts</h3>
        <div>
          <v-btn
            color="secondary"
            prepend-icon="mdi-cog"
            @click="setupDefaults"
            :loading="settingUpDefaults"
            class="mr-2"
          >
            Setup Defaults
          </v-btn>
          <v-btn color="primary" prepend-icon="mdi-plus" @click="openAccountDialog">
            Add Account
          </v-btn>
        </div>
      </v-card-title>
      
      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="accounts"
          :loading="loading"
          class="elevation-1"
          item-key="id"
        >
          <template v-slot:item.account_code="{ item }">
            <strong>{{ item.account_code }}</strong>
          </template>
          
          <template v-slot:item.account_name="{ item }">
            <span :style="{ marginLeft: (item.level - 1) * 20 + 'px' }">
              {{ item.account_name }}
            </span>
          </template>
          
          <template v-slot:item.account_type="{ item }">
            <v-chip :color="getAccountTypeColor(item.account_type)" size="small">
              {{ item.account_type.toUpperCase() }}
            </v-chip>
          </template>
          
          <template v-slot:item.is_active="{ item }">
            <v-chip :color="item.is_active ? 'success' : 'error'" size="small">
              {{ item.is_active ? 'Active' : 'Inactive' }}
            </v-chip>
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon
              size="small"
              @click="editAccount(item)"
              :disabled="item.is_system"
            >
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
    
    <!-- Account Dialog -->
    <v-dialog v-model="accountDialog.show" max-width="600px">
      <v-card>
        <v-card-title>{{ accountDialog.isEdit ? 'Edit' : 'Add' }} Account</v-card-title>
        <v-card-text>
          <v-form ref="accountForm" v-model="accountDialog.valid">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="accountDialog.formData.account_code"
                  label="Account Code*"
                  :rules="[v => !!v || 'Account code is required']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="accountDialog.formData.account_type"
                  label="Account Type*"
                  :items="accountTypes"
                  :rules="[v => !!v || 'Account type is required']"
                  required
                ></v-select>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="accountDialog.formData.account_name"
                  label="Account Name*"
                  :rules="[v => !!v || 'Account name is required']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="accountDialog.formData.parent_id"
                  label="Parent Account"
                  :items="parentAccounts"
                  item-title="display_name"
                  item-value="id"
                  clearable
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="accountDialog.formData.currency_code"
                  label="Currency"
                  :items="currencies"
                  item-title="name"
                  item-value="code"
                ></v-select>
              </v-col>
              
              <v-col cols="12">
                <v-checkbox
                  v-model="accountDialog.formData.is_active"
                  label="Active"
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="accountDialog.show = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="accountDialog.saving"
            :disabled="!accountDialog.valid"
            @click="saveAccount"
          >
            {{ accountDialog.isEdit ? 'Update' : 'Create' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { apiClient } from '@/utils/apiClient';

const { showSnackbar } = useSnackbar();

// Data
const loading = ref(false);
const settingUpDefaults = ref(false);
const accounts = ref([]);

const accountDialog = reactive({
  show: false,
  isEdit: false,
  valid: false,
  saving: false,
  formData: {
    account_code: '',
    account_name: '',
    account_type: '',
    parent_id: null,
    currency_code: 'USD',
    is_active: true
  },
  editId: null
});

// Options
const accountTypes = [
  { title: 'Asset', value: 'asset' },
  { title: 'Liability', value: 'liability' },
  { title: 'Equity', value: 'equity' },
  { title: 'Revenue', value: 'revenue' },
  { title: 'Expense', value: 'expense' }
];

const currencies = [
  { code: 'USD', name: 'US Dollar' },
  { code: 'EUR', name: 'Euro' },
  { code: 'GBP', name: 'British Pound' },
  { code: 'CAD', name: 'Canadian Dollar' }
];

const headers = [
  { title: 'Code', key: 'account_code', sortable: true },
  { title: 'Name', key: 'account_name', sortable: true },
  { title: 'Type', key: 'account_type', sortable: true },
  { title: 'Currency', key: 'currency_code', sortable: true },
  { title: 'Status', key: 'is_active', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
];

// Computed
const parentAccounts = computed(() => {
  return accounts.value.map(account => ({
    id: account.id,
    display_name: `${account.account_code} - ${account.account_name}`
  }));
});

// Methods
const fetchAccounts = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get('/api/v1/accounting/chart-of-accounts');
    accounts.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load accounts', 'error');
    console.error('Error fetching accounts:', error);
  } finally {
    loading.value = false;
  }
};

const setupDefaults = async () => {
  settingUpDefaults.value = true;
  try {
    await apiClient.post('/api/v1/accounting/chart-of-accounts/setup-defaults');
    showSnackbar('Default accounts created successfully', 'success');
    fetchAccounts();
  } catch (error) {
    showSnackbar('Failed to setup default accounts', 'error');
    console.error('Error setting up defaults:', error);
  } finally {
    settingUpDefaults.value = false;
  }
};

const openAccountDialog = () => {
  accountDialog.isEdit = false;
  accountDialog.editId = null;
  accountDialog.formData = {
    account_code: '',
    account_name: '',
    account_type: '',
    parent_id: null,
    currency_code: 'USD',
    is_active: true
  };
  accountDialog.show = true;
};

const editAccount = (account) => {
  accountDialog.isEdit = true;
  accountDialog.editId = account.id;
  accountDialog.formData = {
    account_code: account.account_code,
    account_name: account.account_name,
    account_type: account.account_type,
    parent_id: account.parent_id,
    currency_code: account.currency_code,
    is_active: account.is_active
  };
  accountDialog.show = true;
};

const saveAccount = async () => {
  if (!accountDialog.valid) return;
  
  accountDialog.saving = true;
  try {
    if (accountDialog.isEdit) {
      await apiClient.put(
        `/api/v1/accounting/chart-of-accounts/${accountDialog.editId}`,
        accountDialog.formData
      );
      showSnackbar('Account updated successfully', 'success');
    } else {
      await apiClient.post('/api/v1/accounting/chart-of-accounts', accountDialog.formData);
      showSnackbar('Account created successfully', 'success');
    }
    
    accountDialog.show = false;
    fetchAccounts();
  } catch (error) {
    showSnackbar('Failed to save account', 'error');
    console.error('Save account error:', error);
  } finally {
    accountDialog.saving = false;
  }
};

const getAccountTypeColor = (type) => {
  const colors = {
    asset: 'blue',
    liability: 'red',
    equity: 'green',
    revenue: 'purple',
    expense: 'orange'
  };
  return colors[type] || 'grey';
};

// Lifecycle
onMounted(() => {
  fetchAccounts();
});
</script>

<style scoped>
.chart-of-accounts {
  padding: 16px;
}
</style>