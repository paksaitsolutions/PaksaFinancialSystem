<template>
  <Dialog v-model:visible="visible" header="Generate Consolidated Report" modal :style="{ width: '600px' }">
    <div class="consolidated-form">
      <div class="field">
        <label>Report Type</label>
        <Dropdown 
          v-model="form.reportType" 
          :options="reportTypes" 
          optionLabel="label" 
          optionValue="value" 
        />
      </div>
      
      <div class="field">
        <label>Period Start</label>
        <Calendar v-model="form.periodStart" />
      </div>
      
      <div class="field">
        <label>Period End</label>
        <Calendar v-model="form.periodEnd" />
      </div>
      
      <div class="field">
        <label>Companies to Include</label>
        <MultiSelect 
          v-model="form.selectedCompanies" 
          :options="availableCompanies" 
          optionLabel="company_name" 
          optionValue="id"
          placeholder="Select companies"
          :maxSelectedLabels="3"
        />
      </div>
      
      <div class="field">
        <label>Consolidation Method</label>
        <div class="flex flex-wrap gap-3">
          <div class="flex align-items-center">
            <RadioButton 
              id="sum" 
              name="method" 
              value="sum" 
              v-model="form.consolidationMethod"
            />
            <label for="sum" class="ml-2">Sum</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="average" 
              name="method" 
              value="average" 
              v-model="form.consolidationMethod"
            />
            <label for="average" class="ml-2">Average</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="weighted" 
              name="method" 
              value="weighted" 
              v-model="form.consolidationMethod"
            />
            <label for="weighted" class="ml-2">Weighted</label>
          </div>
        </div>
      </div>
      
      <div class="field">
        <Checkbox v-model="form.eliminateIntercompany" inputId="eliminate" />
        <label for="eliminate" class="ml-2">Eliminate Intercompany Transactions</label>
      </div>
    </div>
    
    <template #footer>
      <Button label="Cancel" class="p-button-text" @click="$emit('close')" />
      <Button label="Generate" @click="generateReport" :loading="loading" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useToast } from 'vue/usetoast';
import { useEnhancedReports } from '@/composables/useEnhancedReports';
import enhancedReportsService from '@/services/enhancedReportsService';

const props = defineProps<{
  visible: boolean;
}>();

const emit = defineEmits<{
  close: [];
  generated: [report: any];
}>();

const toast = useToast();
const { loading, generateReport: generateSingleReport } = useEnhancedReports();

const form = ref({
  reportType: 'income_statement',
  periodStart: new Date(),
  periodEnd: new Date(),
  selectedCompanies: [],
  consolidationMethod: 'sum',
  eliminateIntercompany: true
});

const reportTypes = enhancedReportsService.utils.getReportTypes().filter(type => 
  ['income_statement', 'balance_sheet', 'cash_flow'].includes(type.value)
);

// Mock companies - in real app, this would come from a store or API
const availableCompanies = ref([
  { id: '1', company_name: 'Parent Company' },
  { id: '2', company_name: 'Subsidiary A' },
  { id: '3', company_name: 'Subsidiary B' }
]);

const generateReport = async () => {
  try {
    // Generate individual reports for each company
    const reports = [];
    
    for (const companyId of form.value.selectedCompanies) {
      const report = await generateSingleReport(form.value.reportType, {
        periodStart: form.value.periodStart,
        periodEnd: form.value.periodEnd
      });
      
      if (report) {
        reports.push({ companyId, report });
      }
    }
    
    // Consolidate the reports
    const consolidatedReport = consolidateReports(reports);
    
    toast.add({
      severity: 'success',
      summary: 'Report Generated',
      detail: 'Consolidated report has been generated successfully',
      life: 3000
    });
    
    emit('generated', consolidatedReport);
    emit('close');
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Generation Failed',
      detail: 'Failed to generate consolidated report',
      life: 5000
    });
  }
};

const consolidateReports = (reports: any[]) => {
  // Simplified consolidation logic
  const consolidated = {
    report_type: 'Consolidated ' + enhancedReportsService.utils.formatReportType(form.value.reportType),
    companies: form.value.selectedCompanies.length,
    method: form.value.consolidationMethod,
    period: {
      start: form.value.periodStart.toISOString(),
      end: form.value.periodEnd.toISOString()
    },
    data: {}
  };
  
  // Consolidation logic would be implemented here
  // For now, just return the structure
  
  return consolidated;
};
</script>

<style scoped>
.consolidated-form {
  display: grid;
  gap: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}
</style>