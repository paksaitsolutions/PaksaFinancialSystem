<template>
  <div class="data-quality-dashboard">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1>Data Integrity & Quality</h1>
      <Button label="Run Reconciliation" icon="pi pi-refresh" @click="runReconciliation" :loading="running" />
    </div>

    <div class="grid mb-4">
      <div class="col-12 md:col-4" v-for="metric in summaryCards" :key="metric.label">
        <Card class="h-full">
          <template #title>{{ metric.label }}</template>
          <template #content>
            <div class="text-4xl font-bold text-primary">{{ metric.value }}</div>
            <div class="text-sm text-500 mt-2">{{ metric.caption }}</div>
          </template>
        </Card>
      </div>
    </div>

    <div class="grid">
      <div class="col-12 lg:col-6">
        <Card>
          <template #title>Constraints Review</template>
          <template #content>
            <DataTable :value="constraints" responsiveLayout="scroll">
              <Column field="module" header="Module" />
              <Column field="status" header="Status" />
              <Column header="Checks">
                <template #body="{ data }">
                  <ul class="m-0 pl-3">
                    <li v-for="check in data.checks" :key="check">{{ check }}</li>
                  </ul>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>

      <div class="col-12 lg:col-6">
        <Card>
          <template #title>Reconciliation Results</template>
          <template #content>
            <DataTable :value="reconciliationResults" responsiveLayout="scroll">
              <Column field="check" header="Check" />
              <Column field="value" header="Value" />
              <Column field="status" header="Status" />
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <div class="grid mt-4">
      <div class="col-12">
        <Card>
          <template #title>Data Quality Findings</template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-4">
                <h3 class="text-lg font-semibold">Orphaned Records</h3>
                <ul class="m-0 pl-3">
                  <li v-for="item in dataQuality.metrics.orphaned_records" :key="item.type">
                    {{ item.type }}: {{ item.count }}
                  </li>
                </ul>
              </div>
              <div class="col-12 md:col-4">
                <h3 class="text-lg font-semibold">Posting Gaps</h3>
                <ul class="m-0 pl-3">
                  <li v-for="item in dataQuality.metrics.posting_gaps" :key="item.type">
                    {{ item.type }}: {{ item.count }}
                  </li>
                </ul>
              </div>
              <div class="col-12 md:col-4">
                <h3 class="text-lg font-semibold">Stale States</h3>
                <ul class="m-0 pl-3">
                  <li v-for="item in dataQuality.metrics.stale_states" :key="item.type">
                    {{ item.type }}: {{ item.count }}
                  </li>
                </ul>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { dataIntegrityService } from '@/services/dataIntegrityService';
import { useToast } from 'primevue/usetoast';

const toast = useToast();
const constraints = ref<any[]>([]);
const reconciliationResults = ref<any[]>([]);
const dataQuality = ref<any>({ metrics: { orphaned_records: [], posting_gaps: [], stale_states: [] } });
const running = ref(false);

const summaryCards = computed(() => [
  { label: 'Constraints Reviewed', value: constraints.value.length, caption: 'Modules covered' },
  { label: 'Reconciliation Checks', value: reconciliationResults.value.length, caption: 'Latest run results' },
  { label: 'Orphaned Records', value: dataQuality.value.metrics.orphaned_records?.length || 0, caption: 'Detected issues' }
]);

const loadDashboard = async () => {
  try {
    const constraintsResponse = await dataIntegrityService.getConstraintsReview();
    constraints.value = constraintsResponse.checks || [];

    const qualityResponse = await dataIntegrityService.getDataQualityDashboard();
    dataQuality.value = qualityResponse || dataQuality.value;
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load data integrity dashboard' });
  }
};

const runReconciliation = async () => {
  running.value = true;
  try {
    const response = await dataIntegrityService.runReconciliation();
    reconciliationResults.value = response.results || [];
    toast.add({ severity: 'success', summary: 'Reconciliation', detail: 'Reconciliation completed' });
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Reconciliation', detail: 'Reconciliation failed' });
  } finally {
    running.value = false;
  }
};

onMounted(async () => {
  await loadDashboard();
  await runReconciliation();
});
</script>

<style scoped>
.data-quality-dashboard ul {
  list-style: disc;
}
</style>
