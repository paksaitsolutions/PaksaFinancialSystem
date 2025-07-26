<template>
  <v-container fluid>
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-cog</v-icon>
        General Ledger Settings
      </v-card-title>

      <v-card-text>
        <v-tabs v-model="activeTab">
          <v-tab value="posting">Posting Rules</v-tab>
          <v-tab value="currency">Currency</v-tab>
          <v-tab value="fiscal">Fiscal Year</v-tab>
          <v-tab value="approvals">Approvals</v-tab>
        </v-tabs>

        <v-tabs-window v-model="activeTab">
          <!-- Posting Rules Tab -->
          <v-tabs-window-item value="posting">
            <v-card flat>
              <v-card-text>
                <v-row>
                  <v-col cols="12" md="6">
                    <v-switch
                      v-model="settings.allow_future_posting"
                      label="Allow Future Date Posting"
                      color="primary"
                    />
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-switch
                      v-model="settings.require_balanced_entries"
                      label="Require Balanced Entries"
                      color="primary"
                    />
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-switch
                      v-model="settings.auto_post_entries"
                      label="Auto-Post Journal Entries"
                      color="primary"
                    />
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-tabs-window-item>

          <!-- Currency Tab -->
          <v-tabs-window-item value="currency">
            <v-card flat>
              <v-card-text>
                <v-row>
                  <v-col cols="12" md="6">
                    <v-select
                      v-model="settings.base_currency"
                      :items="currencies"
                      label="Base Currency"
                      item-title="name"
                      item-value="code"
                    />
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-switch
                      v-model="settings.allow_multi_currency"
                      label="Allow Multi-Currency Transactions"
                      color="primary"
                    />
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-tabs-window-item>

          <!-- Fiscal Year Tab -->
          <v-tabs-window-item value="fiscal">
            <v-card flat>
              <v-card-text>
                <v-row>
                  <v-col cols="12" md="6">
                    <v-select
                      v-model="settings.fiscal_year_start_month"
                      :items="months"
                      label="Fiscal Year Start Month"
                      item-title="name"
                      item-value="value"
                    />
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-select
                      v-model="settings.fiscal_year_end_month"
                      :items="months"
                      label="Fiscal Year End Month"
                      item-title="name"
                      item-value="value"
                    />
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-tabs-window-item>

          <!-- Approvals Tab -->
          <v-tabs-window-item value="approvals">
            <v-card flat>
              <v-card-text>
                <v-row>
                  <v-col cols="12" md="4">
                    <v-switch
                      v-model="settings.require_journal_approval"
                      label="Require Journal Entry Approval"
                      color="primary"
                    />
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-switch
                      v-model="settings.require_period_close_approval"
                      label="Require Period Close Approval"
                      color="primary"
                    />
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-switch
                      v-model="settings.require_reversal_approval"
                      label="Require Reversal Approval"
                      color="primary"
                    />
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-tabs-window-item>
        </v-tabs-window>

        <v-divider class="my-4" />

        <v-row>
          <v-col cols="12" class="text-right">
            <v-btn color="primary" @click="saveSettings" :loading="saving">
              <v-icon start>mdi-content-save</v-icon>
              Save Settings
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Role Management Section -->
    <v-card class="mt-4">
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-account-group</v-icon>
        Role Management
      </v-card-title>

      <v-card-text>
        <v-data-table
          :items="roles"
          :headers="roleHeaders"
          class="elevation-1"
        >
          <template #item.permissions="{ item }">
            <v-chip-group>
              <v-chip
                v-for="permission in getActivePermissions(item)"
                :key="permission"
                size="small"
                color="primary"
              >
                {{ formatPermission(permission) }}
              </v-chip>
            </v-chip-group>
          </template>
          <template #item.actions="{ item }">
            <v-btn
              icon="mdi-pencil"
              size="small"
              @click="editRole(item)"
            />
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const activeTab = ref('posting')
const saving = ref(false)

const settings = ref({
  allow_future_posting: false,
  require_balanced_entries: true,
  auto_post_entries: false,
  base_currency: 'USD',
  allow_multi_currency: false,
  fiscal_year_start_month: 1,
  fiscal_year_end_month: 12,
  require_journal_approval: true,
  require_period_close_approval: true,
  require_reversal_approval: true
})

const currencies = ref([
  { code: 'USD', name: 'US Dollar' },
  { code: 'EUR', name: 'Euro' },
  { code: 'GBP', name: 'British Pound' },
  { code: 'JPY', name: 'Japanese Yen' }
])

const months = ref([
  { value: 1, name: 'January' },
  { value: 2, name: 'February' },
  { value: 3, name: 'March' },
  { value: 4, name: 'April' },
  { value: 5, name: 'May' },
  { value: 6, name: 'June' },
  { value: 7, name: 'July' },
  { value: 8, name: 'August' },
  { value: 9, name: 'September' },
  { value: 10, name: 'October' },
  { value: 11, name: 'November' },
  { value: 12, name: 'December' }
])

const roles = ref([
  {
    id: '1',
    name: 'GL_ACCOUNTANT',
    description: 'General Ledger Accountant',
    can_create_accounts: true,
    can_edit_accounts: true,
    can_create_journal_entries: true,
    can_edit_journal_entries: true,
    can_view_all_entries: true,
    can_generate_reports: true
  },
  {
    id: '2',
    name: 'GL_REVIEWER',
    description: 'GL Reviewer',
    can_post_journal_entries: true,
    can_unpost_journal_entries: true,
    can_approve_entries: true,
    can_view_all_entries: true,
    can_generate_reports: true
  },
  {
    id: '3',
    name: 'GL_AUDITOR',
    description: 'GL Auditor',
    can_view_all_entries: true,
    can_generate_reports: true
  }
])

const roleHeaders = [
  { title: 'Role Name', key: 'name' },
  { title: 'Description', key: 'description' },
  { title: 'Permissions', key: 'permissions' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const getActivePermissions = (role) => {
  const permissions = []
  Object.keys(role).forEach(key => {
    if (key.startsWith('can_') && role[key]) {
      permissions.push(key)
    }
  })
  return permissions
}

const formatPermission = (permission) => {
  return permission.replace('can_', '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const saveSettings = async () => {
  saving.value = true
  // Mock API call
  setTimeout(() => {
    saving.value = false
  }, 1000)
}

const editRole = (role) => {
  console.log('Edit role:', role.name)
}

onMounted(() => {
  // Load settings from API
})
</script>