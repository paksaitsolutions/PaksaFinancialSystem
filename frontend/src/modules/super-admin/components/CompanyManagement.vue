<template>
  <ResponsiveContainer>
    <v-card>
      <v-card-title class="d-flex align-center">
        <h2>Company Management</h2>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="refreshData">
          <v-icon left>mdi-refresh</v-icon>
          Refresh
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="companies"
          :loading="loading"
          :items-per-page="10"
        >
          <template v-slot:item.status="{ item }">
            <v-chip :color="getStatusColor(item.status)" small>
              {{ item.status.toUpperCase() }}
            </v-chip>
          </template>
          
          <template v-slot:item.subscription_tier="{ item }">
            <v-chip :color="getTierColor(item.subscription_tier)" small>
              {{ item.subscription_tier.toUpperCase() }}
            </v-chip>
          </template>
          
          <template v-slot:item.monthly_revenue="{ item }">
            {{ formatCurrency(item.monthly_revenue) }}
          </template>
          
          <template v-slot:item.storage_used="{ item }">
            {{ item.storage_used.toFixed(1) }} GB
          </template>
          
          <template v-slot:item.last_active="{ item }">
            {{ formatDate(item.last_active) }}
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-btn 
              v-if="item.status === 'pending'" 
              icon 
              small 
              color="success" 
              @click="approveCompany(item)"
            >
              <v-icon small>mdi-check</v-icon>
            </v-btn>
            <v-btn 
              v-if="item.status === 'active'" 
              icon 
              small 
              color="warning" 
              @click="suspendCompany(item)"
            >
              <v-icon small>mdi-pause</v-icon>
            </v-btn>
            <v-btn icon small @click="viewCompanyDetails(item)">
              <v-icon small>mdi-eye</v-icon>
            </v-btn>
            <v-btn icon small @click="impersonateCompany(item)">
              <v-icon small>mdi-account-switch</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Company Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="800px">
      <v-card v-if="selectedCompany">
        <v-card-title>{{ selectedCompany.name }} - Details</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <v-list>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Company ID</v-list-item-title>
                    <v-list-item-subtitle>{{ selectedCompany.id }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Email</v-list-item-title>
                    <v-list-item-subtitle>{{ selectedCompany.email }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Created</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDate(selectedCompany.created_at) }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-col>
            <v-col cols="12" md="6">
              <v-list>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Users</v-list-item-title>
                    <v-list-item-subtitle>{{ selectedCompany.user_count }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Storage Used</v-list-item-title>
                    <v-list-item-subtitle>{{ selectedCompany.storage_used }} GB</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Monthly Revenue</v-list-item-title>
                    <v-list-item-subtitle>{{ formatCurrency(selectedCompany.monthly_revenue) }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="detailsDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'

export default {
  name: 'CompanyManagement',
  components: { ResponsiveContainer },
  
  data: () => ({
    loading: false,
    detailsDialog: false,
    selectedCompany: null,
    companies: [
      {
        id: '1',
        name: 'ABC Corporation',
        email: 'admin@abc.com',
        status: 'active',
        subscription_tier: 'premium',
        user_count: 45,
        storage_used: 25.5,
        created_at: '2023-10-01T00:00:00Z',
        last_active: '2024-01-15T10:30:00Z',
        monthly_revenue: 299.0
      },
      {
        id: '2',
        name: 'XYZ Startup',
        email: 'admin@xyz.com',
        status: 'pending',
        subscription_tier: 'free',
        user_count: 3,
        storage_used: 0.8,
        created_at: '2024-01-10T00:00:00Z',
        last_active: '2024-01-15T04:30:00Z',
        monthly_revenue: 0.0
      }
    ],
    headers: [
      { title: 'Company', key: 'name' },
      { title: 'Email', key: 'email' },
      { title: 'Status', key: 'status' },
      { title: 'Tier', key: 'subscription_tier' },
      { title: 'Users', key: 'user_count' },
      { title: 'Storage', key: 'storage_used' },
      { title: 'Revenue', key: 'monthly_revenue' },
      { title: 'Last Active', key: 'last_active' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
  }),

  methods: {
    refreshData() {
      this.loading = true
      setTimeout(() => {
        this.loading = false
      }, 1000)
    },

    approveCompany(company) {
      company.status = 'active'
      this.$emit('company-approved', company)
    },

    suspendCompany(company) {
      company.status = 'suspended'
      this.$emit('company-suspended', company)
    },

    viewCompanyDetails(company) {
      this.selectedCompany = company
      this.detailsDialog = true
    },

    impersonateCompany(company) {
      console.log('Impersonating company:', company.name)
      // Implement impersonation logic
    },

    getStatusColor(status) {
      const colors = {
        active: 'success',
        pending: 'warning',
        suspended: 'error',
        cancelled: 'grey'
      }
      return colors[status] || 'grey'
    },

    getTierColor(tier) {
      const colors = {
        free: 'grey',
        basic: 'blue',
        premium: 'purple',
        enterprise: 'gold'
      }
      return colors[tier] || 'grey'
    },

    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>