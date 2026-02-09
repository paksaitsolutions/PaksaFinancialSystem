<template>
  <div class="security-compliance-dashboard">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1>Security & Compliance</h1>
    </div>

    <div class="grid mb-4">
      <div class="col-12 md:col-3" v-for="card in summaryCards" :key="card.label">
        <Card class="h-full">
          <template #title>{{ card.label }}</template>
          <template #content>
            <div class="text-3xl font-bold text-primary">{{ card.value }}</div>
            <div class="text-sm text-500 mt-2">{{ card.caption }}</div>
          </template>
        </Card>
      </div>
    </div>

    <div class="grid">
      <div class="col-12 lg:col-6">
        <Card>
          <template #title>MFA Enforcement</template>
          <template #content>
            <ul class="m-0 pl-3">
              <li>Privileged MFA enforced: {{ securityStatus.mfa_enforced_for_privileged ? 'Yes' : 'No' }}</li>
              <li>Verified MFA devices present: {{ securityStatus.mfa_verified_devices ? 'Yes' : 'No' }}</li>
            </ul>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-6">
        <Card>
          <template #title>Token & Key Governance</template>
          <template #content>
            <ul class="m-0 pl-3">
              <li>Refresh token rotation: {{ securityStatus.refresh_token_rotation ? 'Enabled' : 'Disabled' }}</li>
              <li>Revocation list persisted: {{ securityStatus.revocation_list_persisted ? 'Enabled' : 'Disabled' }}</li>
              <li>
                PII key-rotation runbook:
                <a :href="securityStatus.pii_encryption_runbook" target="_blank" rel="noreferrer">Open</a>
              </li>
            </ul>
          </template>
        </Card>
      </div>
    </div>

    <div class="grid mt-4">
      <div class="col-12">
        <Card>
          <template #title>SOX Approval Matrix</template>
          <template #content>
            <DataTable :value="approvalMatrix" responsiveLayout="scroll">
              <Column field="action" header="Action" />
              <Column field="policy" header="Policy" />
              <Column header="Approvals">
                <template #body="{ data }">
                  <ul class="m-0 pl-3">
                    <li v-for="role in data.required_approvals" :key="role">{{ role }}</li>
                  </ul>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { securityComplianceService } from '@/services/securityComplianceService';
import { useToast } from 'primevue/usetoast';

const toast = useToast();
const securityStatus = ref<any>({
  mfa_enforced_for_privileged: false,
  mfa_verified_devices: false,
  refresh_token_rotation: false,
  revocation_list_persisted: false,
  pii_encryption_runbook: ''
});
const approvalMatrix = ref<any[]>([]);

const summaryCards = computed(() => [
  { label: 'MFA Enforced', value: securityStatus.value.mfa_enforced_for_privileged ? 'Yes' : 'No', caption: 'Privileged routes' },
  { label: 'Refresh Rotation', value: securityStatus.value.refresh_token_rotation ? 'Enabled' : 'Disabled', caption: 'Session safety' },
  { label: 'Revocation List', value: securityStatus.value.revocation_list_persisted ? 'Enabled' : 'Disabled', caption: 'Token invalidation' },
  { label: 'SOX Policies', value: approvalMatrix.value.length, caption: 'Approval rules' }
]);

const loadSecurityCompliance = async () => {
  try {
    const status = await securityComplianceService.getSecurityStatus();
    securityStatus.value = status;
    const matrix = await securityComplianceService.getApprovalMatrix();
    approvalMatrix.value = matrix.matrix || [];
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load security compliance data' });
  }
};

onMounted(loadSecurityCompliance);
</script>

<style scoped>
.security-compliance-dashboard ul {
  list-style: disc;
}
</style>
