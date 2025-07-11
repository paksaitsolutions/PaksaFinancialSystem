<template>
  <div class="chart-of-accounts">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="d-flex justify-space-between align-center">
              <span>Chart of Accounts</span>
              <v-btn color="primary" @click="showCreateDialog = true">
                <v-icon left>mdi-plus</v-icon>
                Add Account
              </v-btn>
            </v-card-title>
            
            <v-card-text>
              <v-data-table
                :headers="headers"
                :items="accounts"
                :loading="loading"
                class="elevation-1"
                item-key="id"
              >
                <template #item.account_type="{ item }">
                  <v-chip
                    :color="getAccountTypeColor(item.account_type)"
                    small
                    text-color="white"
                  >
                    {{ formatAccountType(item.account_type) }}
                  </v-chip>
                </template>
                
                <template #item.is_active="{ item }">
                  <v-icon :color="item.is_active ? 'success' : 'error'">
                    {{ item.is_active ? 'mdi-check-circle' : 'mdi-close-circle' }}
                  </v-icon>
                </template>
                
                <template #item.actions="{ item }">
                  <v-btn
                    icon
                    small
                    @click="editAccount(item)"
                  >
                    <v-icon>mdi-pencil</v-icon>
                  </v-btn>
                  <v-btn
                    icon
                    small
                    color="error"
                    @click="deleteAccount(item)"
                  >
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    
    <!-- Create/Edit Dialog -->
    <v-dialog v-model="showCreateDialog" max-width="600px">
      <AccountForm
        :account="selectedAccount"
        :is-edit="isEdit"
        @cancel="closeDialog"
        @success="handleAccountSaved"
      />
    </v-dialog>
    
    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400px">
      <v-card>
        <v-card-title>Confirm Delete</v-card-title>
        <v-card-text>
          Are you sure you want to delete account "{{ selectedAccount?.account_name }}"?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showDeleteDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="confirmDelete">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useGLStore } from '@/store/glAccounts'
import AccountForm from '@/components/gl/AccountForm.vue'

const glStore = useGLStore()

const loading = ref(false)
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const selectedAccount = ref(null)
const isEdit = ref(false)

const headers = [
  { title: 'Code', key: 'account_code', sortable: true },
  { title: 'Name', key: 'account_name', sortable: true },
  { title: 'Type', key: 'account_type', sortable: true },
  { title: 'Description', key: 'description', sortable: false },
  { title: 'Active', key: 'is_active', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
]

const accounts = computed(() => glStore.accounts)

onMounted(async () => {
  await loadAccounts()
})

const loadAccounts = async () => {
  loading.value = true
  try {
    await glStore.fetchAccounts()
  } catch (error) {
    console.error('Error loading accounts:', error)
  } finally {
    loading.value = false
  }
}

const editAccount = (account: any) => {
  selectedAccount.value = account
  isEdit.value = true
  showCreateDialog.value = true
}

const deleteAccount = (account: any) => {
  selectedAccount.value = account
  showDeleteDialog.value = true
}

const confirmDelete = async () => {
  if (selectedAccount.value) {
    try {
      await glStore.deleteAccount(selectedAccount.value.id)
      showDeleteDialog.value = false
      selectedAccount.value = null
    } catch (error) {
      console.error('Error deleting account:', error)
    }
  }
}

const closeDialog = () => {
  showCreateDialog.value = false
  selectedAccount.value = null
  isEdit.value = false
}

const handleAccountSaved = () => {
  closeDialog()
  loadAccounts()
}

const getAccountTypeColor = (type: string) => {
  const colors = {
    asset: 'blue',
    liability: 'red',
    equity: 'green',
    revenue: 'purple',
    expense: 'orange'
  }
  return colors[type] || 'grey'
}

const formatAccountType = (type: string) => {
  return type.charAt(0).toUpperCase() + type.slice(1)
}
</script>