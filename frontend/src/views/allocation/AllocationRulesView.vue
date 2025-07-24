<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <h2>Allocation Rules</h2>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              @click="openRuleDialog()"
            >
              New Rule
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="rules"
              :loading="loading"
              class="elevation-1"
            >
              <template v-slot:item.allocation_method="{ item }">
                <v-chip
                  :color="getMethodColor(item.allocation_method)"
                  size="small"
                >
                  {{ formatMethod(item.allocation_method) }}
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
              
              <template v-slot:item.effective_from="{ item }">
                {{ formatDate(item.effective_from) }}
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon
                  variant="text"
                  @click="viewRule(item)"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Rule Dialog -->
    <v-dialog v-model="ruleDialog" max-width="900px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ editMode ? 'View Allocation Rule' : 'New Allocation Rule' }}</span>
        </v-card-title>
        
        <v-card-text>
          <v-form ref="ruleForm">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedRule.rule_name"
                  label="Rule Name"
                  :rules="[v => !!v || 'Rule name is required']"
                  :disabled="editMode"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedRule.allocation_method"
                  :items="allocationMethods"
                  item-title="text"
                  item-value="value"
                  label="Allocation Method"
                  :rules="[v => !!v || 'Allocation method is required']"
                  :disabled="editMode"
                ></v-select>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="editedRule.description"
                  label="Description"
                  rows="2"
                  :disabled="editMode"
                ></v-textarea>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedRule.source_account_id"
                  :items="accounts"
                  item-title="name"
                  item-value="id"
                  label="Source Account (Optional)"
                  clearable
                  :disabled="editMode"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedRule.priority"
                  label="Priority"
                  type="number"
                  min="1"
                  max="999"
                  :disabled="editMode"
                ></v-text-field>
              </v-col>
            </v-row>
            
            <!-- Allocation Lines -->
            <v-divider class="my-4"></v-divider>
            <h3 class="mb-4">Allocation Lines</h3>
            
            <v-row v-for="(line, index) in editedRule.allocation_lines" :key="index" class="mb-2">
              <v-col cols="12" md="4">
                <v-select
                  v-model="line.target_account_id"
                  :items="accounts"
                  item-title="name"
                  item-value="id"
                  label="Target Account"
                  :rules="[v => !!v || 'Target account is required']"
                  :disabled="editMode"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="3" v-if="editedRule.allocation_method === 'percentage'">
                <v-text-field
                  v-model="line.allocation_percentage"
                  label="Percentage"
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  suffix="%"
                  :disabled="editMode"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="2">
                <v-text-field
                  v-model="line.line_order"
                  label="Order"
                  type="number"
                  min="1"
                  :disabled="editMode"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="1" v-if="!editMode">
                <v-btn
                  icon
                  variant="text"
                  color="error"
                  @click="removeAllocationLine(index)"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </v-col>
            </v-row>
            
            <v-btn
              v-if="!editMode"
              color="primary"
              variant="outlined"
              @click="addAllocationLine"
              class="mb-4"
            >
              <v-icon left>mdi-plus</v-icon>
              Add Line
            </v-btn>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="blue-darken-1"
            variant="text"
            @click="closeRuleDialog"
          >
            {{ editMode ? 'Close' : 'Cancel' }}
          </v-btn>
          <v-btn
            v-if="!editMode"
            color="blue-darken-1"
            variant="text"
            @click="saveRule"
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
import allocationService from '@/services/allocationService';
import { useSnackbar } from '@/composables/useSnackbar';

export default {
  name: 'AllocationRulesView',
  
  setup() {
    const { showSnackbar } = useSnackbar();
    
    const headers = [
      { title: 'Rule Name', key: 'rule_name', sortable: true },
      { title: 'Code', key: 'rule_code', sortable: true },
      { title: 'Method', key: 'allocation_method', sortable: true },
      { title: 'Status', key: 'status', sortable: true },
      { title: 'Effective From', key: 'effective_from', sortable: true },
      { title: 'Priority', key: 'priority', sortable: true },
      { title: 'Actions', key: 'actions', sortable: false }
    ];
    
    const rules = ref([]);
    const accounts = ref([]);
    const loading = ref(false);
    const saving = ref(false);
    
    const ruleDialog = ref(false);
    const editMode = ref(false);
    const editedRule = ref({
      rule_name: '',
      allocation_method: 'percentage',
      description: '',
      source_account_id: null,
      effective_from: new Date(),
      priority: 100,
      allocation_lines: []
    });
    const ruleForm = ref(null);
    
    const allocationMethods = [
      { text: 'Percentage', value: 'percentage' },
      { text: 'Equal', value: 'equal' }
    ];
    
    const loadRules = async () => {
      loading.value = true;
      try {
        const response = await allocationService.listAllocationRules();
        rules.value = response.data;
      } catch (error) {
        console.error('Failed to load rules:', error);
        showSnackbar('Failed to load allocation rules', 'error');
      } finally {
        loading.value = false;
      }
    };
    
    const openRuleDialog = (rule = null) => {
      if (rule) {
        editMode.value = true;
        editedRule.value = { ...rule };
      } else {
        editMode.value = false;
        editedRule.value = {
          rule_name: '',
          allocation_method: 'percentage',
          description: '',
          source_account_id: null,
          effective_from: new Date(),
          priority: 100,
          allocation_lines: []
        };
      }
      ruleDialog.value = true;
    };
    
    const closeRuleDialog = () => {
      ruleDialog.value = false;
    };
    
    const saveRule = async () => {
      if (!ruleForm.value.validate()) return;
      
      saving.value = true;
      try {
        await allocationService.createAllocationRule(editedRule.value);
        showSnackbar('Allocation rule saved successfully', 'success');
        closeRuleDialog();
        loadRules();
      } catch (error) {
        console.error('Failed to save rule:', error);
        showSnackbar(`Failed to save rule: ${error.response?.data?.detail || error.message}`, 'error');
      } finally {
        saving.value = false;
      }
    };
    
    const viewRule = (rule) => {
      openRuleDialog(rule);
    };
    
    const addAllocationLine = () => {
      editedRule.value.allocation_lines.push({
        target_account_id: '',
        allocation_percentage: 0,
        line_order: editedRule.value.allocation_lines.length + 1
      });
    };
    
    const removeAllocationLine = (index) => {
      editedRule.value.allocation_lines.splice(index, 1);
    };
    
    const formatMethod = (method) => {
      return method.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    };
    
    const getMethodColor = (method) => {
      const colors = {
        percentage: 'primary',
        equal: 'info'
      };
      return colors[method] || 'grey';
    };
    
    const getStatusColor = (status) => {
      const colors = {
        active: 'success',
        inactive: 'error',
        draft: 'warning'
      };
      return colors[status] || 'grey';
    };
    
    const formatDate = (dateString) => {
      if (!dateString) return '';
      return format(new Date(dateString), 'MMM dd, yyyy');
    };
    
    onMounted(() => {
      loadRules();
      accounts.value = [
        { id: '1', name: 'Marketing Expense' },
        { id: '2', name: 'IT Expense' },
        { id: '3', name: 'HR Expense' },
        { id: '4', name: 'Finance Expense' }
      ];
    });
    
    return {
      headers,
      rules,
      accounts,
      loading,
      saving,
      allocationMethods,
      ruleDialog,
      editMode,
      editedRule,
      ruleForm,
      loadRules,
      openRuleDialog,
      closeRuleDialog,
      saveRule,
      viewRule,
      addAllocationLine,
      removeAllocationLine,
      formatMethod,
      getMethodColor,
      getStatusColor,
      formatDate
    };
  }
};
</script>