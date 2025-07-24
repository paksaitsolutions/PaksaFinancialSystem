<template>
  <ResponsiveContainer>
    <v-row>
      <!-- Key Metrics -->
      <v-col cols="12" md="3">
        <v-card color="primary" dark>
          <v-card-text class="text-center">
            <div class="text-h4">{{ analytics.total_companies }}</div>
            <div class="text-caption">Total Companies</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="success" dark>
          <v-card-text class="text-center">
            <div class="text-h4">{{ analytics.total_users }}</div>
            <div class="text-caption">Total Users</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="info" dark>
          <v-card-text class="text-center">
            <div class="text-h4">{{ analytics.total_storage_gb.toFixed(1) }}GB</div>
            <div class="text-caption">Storage Used</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="warning" dark>
          <v-card-text class="text-center">
            <div class="text-h4">{{ formatCurrency(analytics.monthly_revenue) }}</div>
            <div class="text-caption">Monthly Revenue</div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Company Status Breakdown -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Company Status</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="6">
                <div class="text-center">
                  <div class="text-h6 text-success">{{ analytics.active_companies }}</div>
                  <div class="text-caption">Active</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="text-center">
                  <div class="text-h6 text-warning">{{ analytics.pending_companies }}</div>
                  <div class="text-caption">Pending</div>
                </div>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="6">
                <div class="text-center">
                  <div class="text-h6 text-error">{{ analytics.suspended_companies }}</div>
                  <div class="text-caption">Suspended</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="text-center">
                  <div class="text-h6">{{ analytics.total_companies - analytics.active_companies - analytics.pending_companies - analytics.suspended_companies }}</div>
                  <div class="text-caption">Other</div>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Subscription Breakdown -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Subscription Tiers</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item v-for="(count, tier) in analytics.subscription_breakdown" :key="tier">
                <v-list-item-content>
                  <v-list-item-title>{{ tier.toUpperCase() }}</v-list-item-title>
                </v-list-item-content>
                <v-list-item-action>
                  <v-chip :color="getTierColor(tier)" small>{{ count }}</v-chip>
                </v-list-item-action>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- System Health -->
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" :color="systemHealth.status === 'healthy' ? 'success' : 'error'">
              mdi-heart-pulse
            </v-icon>
            System Health
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <div class="text-center">
                  <v-progress-circular
                    :value="parseFloat(systemHealth.uptime)"
                    size="80"
                    width="8"
                    color="success"
                  >
                    {{ systemHealth.uptime }}
                  </v-progress-circular>
                  <div class="text-caption mt-2">Uptime</div>
                </div>
              </v-col>
              
              <v-col cols="12" md="9">
                <v-row>
                  <v-col cols="12" md="4">
                    <div class="mb-2">
                      <div class="text-subtitle-2">Memory Usage</div>
                      <v-progress-linear
                        :value="systemHealth.memory_usage"
                        color="info"
                        height="20"
                      >
                        {{ systemHealth.memory_usage }}%
                      </v-progress-linear>
                    </div>
                  </v-col>
                  
                  <v-col cols="12" md="4">
                    <div class="mb-2">
                      <div class="text-subtitle-2">CPU Usage</div>
                      <v-progress-linear
                        :value="systemHealth.cpu_usage"
                        color="warning"
                        height="20"
                      >
                        {{ systemHealth.cpu_usage }}%
                      </v-progress-linear>
                    </div>
                  </v-col>
                  
                  <v-col cols="12" md="4">
                    <div class="mb-2">
                      <div class="text-subtitle-2">Disk Usage</div>
                      <v-progress-linear
                        :value="systemHealth.disk_usage"
                        color="success"
                        height="20"
                      >
                        {{ systemHealth.disk_usage }}%
                      </v-progress-linear>
                    </div>
                  </v-col>
                </v-row>
                
                <v-row class="mt-2">
                  <v-col cols="6">
                    <div class="text-center">
                      <div class="text-h6">{{ systemHealth.response_time_ms }}ms</div>
                      <div class="text-caption">Avg Response Time</div>
                    </div>
                  </v-col>
                  <v-col cols="6">
                    <div class="text-center">
                      <div class="text-h6">{{ systemHealth.active_connections }}</div>
                      <div class="text-caption">Active Connections</div>
                    </div>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'

export default {
  name: 'PlatformAnalytics',
  components: { ResponsiveContainer },
  
  data: () => ({
    analytics: {
      total_companies: 156,
      active_companies: 142,
      pending_companies: 8,
      suspended_companies: 6,
      total_users: 3247,
      total_storage_gb: 1247.8,
      monthly_revenue: 47850,
      subscription_breakdown: {
        free: 45,
        basic: 67,
        premium: 32,
        enterprise: 12
      }
    },
    systemHealth: {
      status: 'healthy',
      uptime: '99.9',
      response_time_ms: 145,
      error_rate: 0.02,
      active_connections: 1247,
      memory_usage: 68.5,
      cpu_usage: 23.1,
      disk_usage: 45.2
    }
  }),

  methods: {
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
    }
  }
}
</script>