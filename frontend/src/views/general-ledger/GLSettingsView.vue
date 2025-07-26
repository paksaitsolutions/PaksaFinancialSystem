<template>
  <v-container fluid>
    <v-card>
      <v-card-title>
        <v-icon left>mdi-cog</v-icon>
        General Ledger Settings
      </v-card-title>
      
      <v-card-text>
        <v-tabs v-model="activeTab">
          <v-tab>Account Settings</v-tab>
          <v-tab>Period Settings</v-tab>
          <v-tab>Posting Rules</v-tab>
          <v-tab>Numbering</v-tab>
        </v-tabs>
        
        <v-window v-model="activeTab">
          <v-window-item>
            <v-form>
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="settings.defaultCurrency"
                    label="Default Currency"
                    outlined
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-select
                    v-model="settings.accountCodeFormat"
                    :items="accountCodeFormats"
                    label="Account Code Format"
                    outlined
                  />
                </v-col>
              </v-row>
            </v-form>
          </v-window-item>
          
          <v-window-item>
            <v-form>
              <v-row>
                <v-col cols="12" md="6">
                  <v-select
                    v-model="settings.fiscalYearStart"
                    :items="months"
                    label="Fiscal Year Start Month"
                    outlined
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-switch
                    v-model="settings.autoCreatePeriods"
                    label="Auto Create Periods"
                  />
                </v-col>
              </v-row>
            </v-form>
          </v-window-item>
          
          <v-window-item>
            <v-form>
              <v-row>
                <v-col cols="12" md="6">
                  <v-switch
                    v-model="settings.requireBalancedEntries"
                    label="Require Balanced Journal Entries"
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-switch
                    v-model="settings.requireApproval"
                    label="Require Journal Entry Approval"
                  />
                </v-col>
              </v-row>
            </v-form>
          </v-window-item>
          
          <v-window-item>
            <v-form>
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="settings.journalEntryPrefix"
                    label="Journal Entry Prefix"
                    outlined
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="settings.nextJournalNumber"
                    label="Next Journal Entry Number"
                    type="number"
                    outlined
                  />
                </v-col>
              </v-row>
            </v-form>
          </v-window-item>
        </v-window>
      </v-card-text>
      
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" @click="saveSettings">
          Save Settings
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script>
export default {
  name: 'GLSettingsView',
  
  data: () => ({
    activeTab: 0,
    settings: {
      defaultCurrency: 'USD',
      accountCodeFormat: 'numeric',
      fiscalYearStart: 1,
      autoCreatePeriods: true,
      requireBalancedEntries: true,
      requireApproval: false,
      journalEntryPrefix: 'JE',
      nextJournalNumber: 1
    },
    
    accountCodeFormats: [
      { text: 'Numeric', value: 'numeric' },
      { text: 'Alphanumeric', value: 'alphanumeric' }
    ],
    
    months: [
      { text: 'January', value: 1 },
      { text: 'February', value: 2 },
      { text: 'March', value: 3 },
      { text: 'April', value: 4 },
      { text: 'May', value: 5 },
      { text: 'June', value: 6 },
      { text: 'July', value: 7 },
      { text: 'August', value: 8 },
      { text: 'September', value: 9 },
      { text: 'October', value: 10 },
      { text: 'November', value: 11 },
      { text: 'December', value: 12 }
    ]
  }),
  
  methods: {
    saveSettings() {
      console.log('Saving GL settings:', this.settings)
    }
  }
}
</script>