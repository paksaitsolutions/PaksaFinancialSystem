<!--
  Paksa Financial System - Enhanced Audit Trail Visualization
  Copyright (c) 2025 Paksa IT Solutions. All rights reserved.
-->
<template>
  <div class="audit-trail-viewer">
    <div class="filters">
      <Calendar v-model="filters.dateRange" selectionMode="range" placeholder="Date Range" />
      <Dropdown v-model="filters.action" :options="actions" placeholder="Action" showClear />
      <Dropdown v-model="filters.resourceType" :options="resourceTypes" placeholder="Resource" showClear />
      <InputText v-model="filters.userId" placeholder="User ID" />
      <Button label="Search" icon="pi pi-search" @click="loadAuditLogs" />
    </div>

    <Timeline :value="auditLogs" align="alternate" class="audit-timeline">
      <template #marker="{ item }">
        <span :class="['timeline-marker', `marker-${item.level.toLowerCase()}`]">
          <i :class="getActionIcon(item.action)"></i>
        </span>
      </template>
      
      <template #content="{ item }">
        <Card class="audit-card">
          <template #title>
            <div class="audit-header">
              <Tag :value="item.action" :severity="getActionSeverity(item.action)" />
              <span class="resource-type">{{ item.resource_type }}</span>
            </div>
          </template>
          
          <template #content>
            <div class="audit-details">
              <div class="detail-row">
                <strong>User:</strong> {{ item.user_id || 'System' }}
              </div>
              <div class="detail-row">
                <strong>Time:</strong> {{ formatDate(item.created_at) }}
              </div>
              <div class="detail-row" v-if="item.resource_name">
                <strong>Resource:</strong> {{ item.resource_name }}
              </div>
              <div class="detail-row" v-if="item.message">
                <strong>Message:</strong> {{ item.message }}
              </div>
              
              <div v-if="item.old_values || item.new_values" class="changes-section">
                <Button 
                  label="View Changes" 
                  icon="pi pi-eye" 
                  text 
                  @click="showChanges(item)" 
                />
              </div>
            </div>
          </template>
        </Card>
      </template>
    </Timeline>

    <Dialog v-model:visible="changesDialog" header="Audit Changes" :style="{ width: '50vw' }">
      <div class="changes-viewer">
        <div v-if="selectedAudit?.old_values" class="change-section">
          <h4>Old Values</h4>
          <pre>{{ JSON.stringify(selectedAudit.old_values, null, 2) }}</pre>
        </div>
        <div v-if="selectedAudit?.new_values" class="change-section">
          <h4>New Values</h4>
          <pre>{{ JSON.stringify(selectedAudit.new_values, null, 2) }}</pre>
        </div>
        <div v-if="selectedAudit?.old_values && selectedAudit?.new_values" class="diff-section">
          <h4>Changes</h4>
          <div v-for="(value, key) in getDiff(selectedAudit)" :key="key" class="diff-item">
            <strong>{{ key }}:</strong>
            <span class="old-value">{{ value.old }}</span>
            <i class="pi pi-arrow-right"></i>
            <span class="new-value">{{ value.new }}</span>
          </div>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { format } from 'date-fns';

interface AuditLog {
  id: string;
  user_id?: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  resource_name?: string;
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
  level: string;
  message?: string;
  created_at: string;
}

const auditLogs = ref<AuditLog[]>([]);
const changesDialog = ref(false);
const selectedAudit = ref<AuditLog | null>(null);

const filters = ref({
  dateRange: null,
  action: null,
  resourceType: null,
  userId: ''
});

const actions = ['CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'APPROVE', 'REJECT'];
const resourceTypes = ['JournalEntry', 'Invoice', 'Payment', 'Account', 'User'];

const loadAuditLogs = async () => {
  // API call placeholder
};

const getActionIcon = (action: string) => {
  const icons: Record<string, string> = {
    CREATE: 'pi pi-plus-circle',
    UPDATE: 'pi pi-pencil',
    DELETE: 'pi pi-trash',
    LOGIN: 'pi pi-sign-in',
    LOGOUT: 'pi pi-sign-out',
    APPROVE: 'pi pi-check-circle',
    REJECT: 'pi pi-times-circle'
  };
  return icons[action] || 'pi pi-circle';
};

const getActionSeverity = (action: string) => {
  const severities: Record<string, string> = {
    CREATE: 'success',
    UPDATE: 'info',
    DELETE: 'danger',
    APPROVE: 'success',
    REJECT: 'warning'
  };
  return severities[action] || 'info';
};

const formatDate = (date: string) => {
  return format(new Date(date), 'PPpp');
};

const showChanges = (audit: AuditLog) => {
  selectedAudit.value = audit;
  changesDialog.value = true;
};

const getDiff = (audit: AuditLog) => {
  if (!audit.old_values || !audit.new_values) return {};
  
  const diff: Record<string, { old: any; new: any }> = {};
  const allKeys = new Set([...Object.keys(audit.old_values), ...Object.keys(audit.new_values)]);
  
  allKeys.forEach(key => {
    const oldVal = audit.old_values?.[key];
    const newVal = audit.new_values?.[key];
    if (oldVal !== newVal) {
      diff[key] = { old: oldVal, new: newVal };
    }
  });
  
  return diff;
};

onMounted(() => {
  loadAuditLogs();
});
</script>

<style scoped>
.audit-trail-viewer {
  padding: 1rem;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.audit-timeline {
  margin-top: 2rem;
}

.timeline-marker {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  color: white;
}

.marker-low { background: var(--blue-500); }
.marker-medium { background: var(--yellow-500); }
.marker-high { background: var(--orange-500); }
.marker-critical { background: var(--red-500); }

.audit-card {
  margin: 0.5rem 0;
}

.audit-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.audit-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-row {
  display: flex;
  gap: 0.5rem;
}

.changes-section {
  margin-top: 1rem;
}

.changes-viewer {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.change-section pre {
  background: var(--surface-100);
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
}

.diff-item {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  padding: 0.5rem;
  border-bottom: 1px solid var(--surface-200);
}

.old-value {
  color: var(--red-500);
  text-decoration: line-through;
}

.new-value {
  color: var(--green-500);
  font-weight: bold;
}
</style>
