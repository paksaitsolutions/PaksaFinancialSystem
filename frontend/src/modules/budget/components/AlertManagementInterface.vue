<template>
  <div class="alert-management-interface">
    <Card>
      <template #title>Alert Management</template>
      <template #content>
        <TabView>
          <TabPanel header="Active Alerts">
            <DataTable :value="activeAlerts" class="p-datatable-sm">
              <Column field="type" header="Type" :sortable="true">
                <template #body="{ data }">
                  <Tag :value="data.type" :severity="getTypeSeverity(data.type)" />
                </template>
              </Column>
              <Column field="budget" header="Budget" :sortable="true" />
              <Column field="message" header="Message" :sortable="true" />
              <Column field="threshold" header="Threshold" :sortable="true">
                <template #body="{ data }">
                  {{ data.threshold }}%
                </template>
              </Column>
              <Column field="current" header="Current" :sortable="true">
                <template #body="{ data }">
                  {{ data.current }}%
                </template>
              </Column>
              <Column field="created" header="Created" :sortable="true">
                <template #body="{ data }">
                  {{ formatDate(data.created) }}
                </template>
              </Column>
              <Column>
                <template #body="{ data }">
                  <div class="flex gap-1">
                    <Button 
                      icon="pi pi-check"
                      class="p-button-text p-button-sm p-button-success"
                      @click="acknowledgeAlert(data.id)"
                      v-tooltip.top="'Acknowledge'"
                    />
                    <Button 
                      icon="pi pi-times"
                      class="p-button-text p-button-sm p-button-danger"
                      @click="dismissAlert(data.id)"
                      v-tooltip.top="'Dismiss'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </TabPanel>
          
          <TabPanel header="Alert Rules">
            <div class="alert-rules-section">
              <div class="flex justify-content-between align-items-center mb-4">
                <h4>Alert Configuration</h4>
                <Button 
                  label="Add Rule"
                  icon="pi pi-plus"
                  @click="showRuleDialog = true"
                />
              </div>
              
              <DataTable :value="alertRules" class="p-datatable-sm">
                <Column field="name" header="Rule Name" :sortable="true" />
                <Column field="condition" header="Condition" :sortable="true" />
                <Column field="threshold" header="Threshold" :sortable="true">
                  <template #body="{ data }">
                    {{ data.threshold }}%
                  </template>
                </Column>
                <Column field="enabled" header="Status" :sortable="true">
                  <template #body="{ data }">
                    <Tag :value="data.enabled ? 'Enabled' : 'Disabled'" :severity="data.enabled ? 'success' : 'danger'" />
                  </template>
                </Column>
                <Column>
                  <template #body="{ data }">
                    <div class="flex gap-1">
                      <Button 
                        icon="pi pi-pencil"
                        class="p-button-text p-button-sm"
                        @click="editRule(data)"
                        v-tooltip.top="'Edit'"
                      />
                      <Button 
                        :icon="data.enabled ? 'pi pi-pause' : 'pi pi-play'"
                        class="p-button-text p-button-sm"
                        @click="toggleRule(data.id)"
                        v-tooltip.top="data.enabled ? 'Disable' : 'Enable'"
                      />
                      <Button 
                        icon="pi pi-trash"
                        class="p-button-text p-button-sm p-button-danger"
                        @click="deleteRule(data.id)"
                        v-tooltip.top="'Delete'"
                      />
                    </div>
                  </template>
                </Column>
              </DataTable>
            </div>
          </TabPanel>
          
          <TabPanel header="Notification Settings">
            <div class="notification-settings">
              <div class="grid">
                <div class="col-12 md:col-6">
                  <Card>
                    <template #title>Email Notifications</template>
                    <template #content>
                      <div class="field-checkbox">
                        <Checkbox v-model="notificationSettings.email.enabled" inputId="emailEnabled" binary />
                        <label for="emailEnabled">Enable email notifications</label>
                      </div>
                      
                      <div v-if="notificationSettings.email.enabled" class="mt-3">
                        <div class="field">
                          <label for="emailRecipients">Recipients</label>
                          <Chips 
                            id="emailRecipients"
                            v-model="notificationSettings.email.recipients"
                            placeholder="Enter email addresses"
                            class="w-full"
                          />
                        </div>
                        
                        <div class="field">
                          <label for="emailFrequency">Frequency</label>
                          <Dropdown 
                            id="emailFrequency"
                            v-model="notificationSettings.email.frequency"
                            :options="frequencyOptions"
                            optionLabel="label"
                            optionValue="value"
                            class="w-full"
                          />
                        </div>
                      </div>
                    </template>
                  </Card>
                </div>
                
                <div class="col-12 md:col-6">
                  <Card>
                    <template #title>In-App Notifications</template>
                    <template #content>
                      <div class="field-checkbox">
                        <Checkbox v-model="notificationSettings.inApp.enabled" inputId="inAppEnabled" binary />
                        <label for="inAppEnabled">Enable in-app notifications</label>
                      </div>
                      
                      <div class="field-checkbox">
                        <Checkbox v-model="notificationSettings.inApp.sound" inputId="soundEnabled" binary />
                        <label for="soundEnabled">Play notification sound</label>
                      </div>
                      
                      <div class="field-checkbox">
                        <Checkbox v-model="notificationSettings.inApp.desktop" inputId="desktopEnabled" binary />
                        <label for="desktopEnabled">Show desktop notifications</label>
                      </div>
                    </template>
                  </Card>
                </div>
              </div>
              
              <div class="flex justify-content-end mt-4">
                <Button 
                  label="Save Settings"
                  @click="saveNotificationSettings"
                  :loading="savingSettings"
                />
              </div>
            </div>
          </TabPanel>
        </TabView>
      </template>
    </Card>
    
    <!-- Rule Dialog -->
    <Dialog 
      v-model:visible="showRuleDialog"
      header="Alert Rule"
      :modal="true"
      :style="{ width: '500px' }"
    >
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label for="ruleName">Rule Name</label>
            <InputText 
              id="ruleName"
              v-model="ruleForm.name"
              class="w-full"
              placeholder="Enter rule name"
            />
          </div>
        </div>
        
        <div class="col-12">
          <div class="field">
            <label for="ruleCondition">Condition</label>
            <Dropdown 
              id="ruleCondition"
              v-model="ruleForm.condition"
              :options="conditionOptions"
              optionLabel="label"
              optionValue="value"
              class="w-full"
            />
          </div>
        </div>
        
        <div class="col-12">
          <div class="field">
            <label for="ruleThreshold">Threshold (%)</label>
            <InputNumber 
              id="ruleThreshold"
              v-model="ruleForm.threshold"
              :min="0"
              :max="200"
              suffix="%"
              class="w-full"
            />
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel"
          class="p-button-text"
          @click="showRuleDialog = false"
        />
        <Button 
          label="Save"
          @click="saveRule"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showRuleDialog = ref(false)
const savingSettings = ref(false)

const activeAlerts = ref([
  {
    id: 1,
    type: 'Budget Exceeded',
    budget: 'Marketing Q1',
    message: 'Budget utilization has exceeded 90%',
    threshold: 90,
    current: 95,
    created: new Date('2024-01-15')
  },
  {
    id: 2,
    type: 'Overspend',
    budget: 'IT Equipment',
    message: 'Budget has been exceeded',
    threshold: 100,
    current: 105,
    created: new Date('2024-01-14')
  }
])

const alertRules = ref([
  {
    id: 1,
    name: 'Budget Warning',
    condition: 'Budget utilization exceeds',
    threshold: 80,
    enabled: true
  },
  {
    id: 2,
    name: 'Budget Critical',
    condition: 'Budget utilization exceeds',
    threshold: 95,
    enabled: true
  },
  {
    id: 3,
    name: 'Overspend Alert',
    condition: 'Budget utilization exceeds',
    threshold: 100,
    enabled: true
  }
])

const ruleForm = ref({
  name: '',
  condition: '',
  threshold: 80
})

const notificationSettings = ref({
  email: {
    enabled: true,
    recipients: ['admin@company.com', 'finance@company.com'],
    frequency: 'immediate'
  },
  inApp: {
    enabled: true,
    sound: true,
    desktop: false
  }
})

const conditionOptions = [
  { label: 'Budget utilization exceeds', value: 'Budget utilization exceeds' },
  { label: 'Budget amount exceeds', value: 'Budget amount exceeds' },
  { label: 'Spending rate exceeds', value: 'Spending rate exceeds' }
]

const frequencyOptions = [
  { label: 'Immediate', value: 'immediate' },
  { label: 'Daily Digest', value: 'daily' },
  { label: 'Weekly Summary', value: 'weekly' }
]

const getTypeSeverity = (type: string) => {
  switch (type) {
    case 'Budget Exceeded': return 'warning'
    case 'Overspend': return 'danger'
    case 'Warning': return 'info'
    default: return 'info'
  }
}

const formatDate = (date: Date) => {
  return date.toLocaleDateString()
}

const acknowledgeAlert = (alertId: number) => {
  console.log('Acknowledging alert:', alertId)
}

const dismissAlert = (alertId: number) => {
  activeAlerts.value = activeAlerts.value.filter(alert => alert.id !== alertId)
}

const editRule = (rule: any) => {
  ruleForm.value = { ...rule }
  showRuleDialog.value = true
}

const toggleRule = (ruleId: number) => {
  const rule = alertRules.value.find(r => r.id === ruleId)
  if (rule) {
    rule.enabled = !rule.enabled
  }
}

const deleteRule = (ruleId: number) => {
  alertRules.value = alertRules.value.filter(rule => rule.id !== ruleId)
}

const saveRule = () => {
  // Mock save rule logic
  console.log('Saving rule:', ruleForm.value)
  showRuleDialog.value = false
  ruleForm.value = { name: '', condition: '', threshold: 80 }
}

const saveNotificationSettings = async () => {
  savingSettings.value = true
  try {
    // Mock save settings
    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log('Notification settings saved')
  } finally {
    savingSettings.value = false
  }
}
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color-secondary);
}

.field-checkbox {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.field-checkbox label {
  margin-left: 0.5rem;
  margin-bottom: 0;
}
</style>