<template>
  <ResponsiveContainer>
    <v-card>
      <v-card-title class="d-flex align-center">
        <h2>Global Configuration</h2>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="saveConfiguration" :loading="saving">
          <v-icon left>mdi-content-save</v-icon>
          Save Changes
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-tabs v-model="activeTab">
          <v-tab value="limits">User Limits</v-tab>
          <v-tab value="pricing">Pricing</v-tab>
          <v-tab value="features">Features</v-tab>
          <v-tab value="system">System</v-tab>
        </v-tabs>

        <v-window v-model="activeTab" class="mt-4">
          <!-- User Limits -->
          <v-window-item value="limits">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="config.max_users_free"
                  label="Max Users (Free)"
                  type="number"
                  outlined
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="config.max_users_basic"
                  label="Max Users (Basic)"
                  type="number"
                  outlined
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="config.max_users_premium"
                  label="Max Users (Premium)"
                  type="number"
                  outlined
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="config.max_users_enterprise"
                  label="Max Users (Enterprise)"
                  type="number"
                  outlined
                ></v-text-field>
              </v-col>
            </v-row>
            
            <h3 class="mb-4">Storage Limits (GB)</h3>
            <v-row>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="config.storage_limits.free"
                  label="Free Tier"
                  type="number"
                  outlined
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="config.storage_limits.basic"
                  label="Basic Tier"
                  type="number"
                  outlined
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="config.storage_limits.premium"
                  label="Premium Tier"
                  type="number"
                  outlined
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="config.storage_limits.enterprise"
                  label="Enterprise Tier"
                  type="number"
                  outlined
                ></v-text-field>
              </v-col>
            </v-row>
          </v-window-item>

          <!-- Pricing -->
          <v-window-item value="pricing">
            <v-row>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="config.pricing.basic"
                  label="Basic Monthly Price"
                  type="number"
                  prefix="$"
                  outlined
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="config.pricing.premium"
                  label="Premium Monthly Price"
                  type="number"
                  prefix="$"
                  outlined
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="config.pricing.enterprise"
                  label="Enterprise Monthly Price"
                  type="number"
                  prefix="$"
                  outlined
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="config.pricing.per_user"
                  label="Per Additional User"
                  type="number"
                  prefix="$"
                  outlined
                ></v-text-field>
              </v-col>
            </v-row>
          </v-window-item>

          <!-- Features -->
          <v-window-item value="features">
            <v-row>
              <v-col cols="12" md="6">
                <h3 class="mb-4">Free Tier Features</h3>
                <v-checkbox
                  v-for="feature in availableFeatures"
                  :key="feature.key"
                  v-model="config.features.free"
                  :value="feature.key"
                  :label="feature.label"
                ></v-checkbox>
              </v-col>
              <v-col cols="12" md="6">
                <h3 class="mb-4">Premium Features</h3>
                <v-checkbox
                  v-for="feature in premiumFeatures"
                  :key="feature.key"
                  v-model="config.features.premium"
                  :value="feature.key"
                  :label="feature.label"
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-window-item>

          <!-- System -->
          <v-window-item value="system">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="config.system.session_timeout"
                  label="Session Timeout (minutes)"
                  type="number"
                  outlined
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="config.system.max_api_calls_per_hour"
                  label="Max API Calls per Hour"
                  type="number"
                  outlined
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-checkbox
                  v-model="config.system.maintenance_mode"
                  label="Maintenance Mode"
                ></v-checkbox>
              </v-col>
              <v-col cols="12" md="6">
                <v-checkbox
                  v-model="config.system.new_registrations_enabled"
                  label="Allow New Registrations"
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-window-item>
        </v-window>
      </v-card-text>
    </v-card>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'

export default {
  name: 'GlobalConfiguration',
  components: { ResponsiveContainer },
  
  data: () => ({
    activeTab: 'limits',
    saving: false,
    config: {
      max_users_free: 5,
      max_users_basic: 25,
      max_users_premium: 100,
      max_users_enterprise: 1000,
      storage_limits: {
        free: 1,
        basic: 10,
        premium: 100,
        enterprise: 1000
      },
      pricing: {
        basic: 29,
        premium: 99,
        enterprise: 299,
        per_user: 5
      },
      features: {
        free: ['basic_accounting', 'invoicing'],
        premium: ['advanced_reporting', 'api_access', 'integrations']
      },
      system: {
        session_timeout: 60,
        max_api_calls_per_hour: 1000,
        maintenance_mode: false,
        new_registrations_enabled: true
      }
    },
    availableFeatures: [
      { key: 'basic_accounting', label: 'Basic Accounting' },
      { key: 'invoicing', label: 'Invoicing' },
      { key: 'expense_tracking', label: 'Expense Tracking' },
      { key: 'basic_reports', label: 'Basic Reports' }
    ],
    premiumFeatures: [
      { key: 'advanced_reporting', label: 'Advanced Reporting' },
      { key: 'api_access', label: 'API Access' },
      { key: 'integrations', label: 'Third-party Integrations' },
      { key: 'ai_insights', label: 'AI Insights' },
      { key: 'multi_currency', label: 'Multi-currency Support' }
    ]
  }),

  methods: {
    saveConfiguration() {
      this.saving = true
      setTimeout(() => {
        this.saving = false
        this.$emit('configuration-saved', this.config)
      }, 1000)
    }
  }
}
</script>