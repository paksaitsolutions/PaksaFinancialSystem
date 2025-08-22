<template>
  <ResponsiveContainer>
    <v-row>
      <!-- Error Logs -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="error">mdi-alert-circle</v-icon>
            Recent Errors
          </v-card-title>
          <v-card-text>
            <v-list max-height="300" class="overflow-y-auto">
              <v-list-item v-for="error in errorLogs" :key="error.id">
                <v-list-item-content>
                  <v-list-item-title>{{ error.message }}</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ error.company }} - {{ formatDate(error.timestamp) }}
                  </v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <v-chip :color="getSeverityColor(error.severity)" small>
                    {{ error.severity }}
                  </v-chip>
                </v-list-item-action>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Audit Logs -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="info">mdi-file-document</v-icon>
            Audit Trail
          </v-card-title>
          <v-card-text>
            <v-list max-height="300" class="overflow-y-auto">
              <v-list-item v-for="audit in auditLogs" :key="audit.id">
                <v-list-item-content>
                  <v-list-item-title>{{ audit.action }}</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ audit.user }} - {{ formatDate(audit.timestamp) }}
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Usage Statistics -->
      <v-col cols="12">
        <v-card>
          <v-card-title>Usage Statistics</v-card-title>
          <v-card-text>
            <v-data-table
              :headers="usageHeaders"
              :items="usageStats"
              :items-per-page="10"
            >
              <template v-slot:item.api_calls="{ item }">
                {{ item.api_calls.toLocaleString() }}
              </template>
              
              <template v-slot:item.storage_gb="{ item }">
                {{ item.storage_gb.toFixed(1) }} GB
              </template>
              
              <template v-slot:item.last_updated="{ item }">
                {{ formatDate(item.last_updated) }}
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'

export default {
  name: 'SystemMonitoring',
  components: { ResponsiveContainer },
  
  data: () => ({
    errorLogs: [
      {
        id: 1,
        message: 'Database connection timeout',
        company: 'ABC Corporation',
        severity: 'high',
        timestamp: '2024-01-15T10:30:00Z'
      },
      {
        id: 2,
        message: 'API rate limit exceeded',
        company: 'XYZ Startup',
        severity: 'medium',
        timestamp: '2024-01-15T09:15:00Z'
      }
    ],
    auditLogs: [
      {
        id: 1,
        action: 'Company approved: ABC Corporation',
        user: 'super.admin@paksa.com',
        timestamp: '2024-01-15T11:00:00Z'
      },
      {
        id: 2,
        action: 'Configuration updated: User limits',
        user: 'super.admin@paksa.com',
        timestamp: '2024-01-15T10:45:00Z'
      }
    ],
    usageStats: [
      {
        company_name: 'ABC Corporation',
        api_calls: 12500,
        storage_gb: 25.5,
        active_users: 45,
        transactions_count: 8750,
        last_updated: '2024-01-15T10:30:00Z'
      },
      {
        company_name: 'XYZ Startup',
        api_calls: 2100,
        storage_gb: 0.8,
        active_users: 3,
        transactions_count: 450,
        last_updated: '2024-01-15T09:15:00Z'
      }
    ],
    usageHeaders: [
      { title: 'Company', key: 'company_name' },
      { title: 'API Calls', key: 'api_calls' },
      { title: 'Storage', key: 'storage_gb' },
      { title: 'Users', key: 'active_users' },
      { title: 'Transactions', key: 'transactions_count' },
      { title: 'Last Updated', key: 'last_updated' }
    ]
  }),

  methods: {
    getSeverityColor(severity) {
      const colors = {
        high: 'error',
        medium: 'warning',
        low: 'info'
      }
      return colors[severity] || 'grey'
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleString()
    }
  }
}
</script>