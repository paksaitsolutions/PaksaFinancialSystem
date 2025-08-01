<template>
  <v-container fluid class="reports-view">
    <v-row>
      <v-col cols="12">
        <v-toolbar color="transparent" density="compact" class="mb-4">
          <v-toolbar-title class="text-h5 font-weight-bold">Reports</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="showNewReportDialog = true"
          >
            New Report
          </v-btn>
        </v-toolbar>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="4" v-for="(report, i) in reports" :key="i">
        <v-card height="100%" class="d-flex flex-column">
          <v-card-item>
            <v-card-title class="text-subtitle-1 font-weight-bold">
              {{ report.title }}
            </v-card-title>
            <v-card-subtitle>{{ report.category }}</v-card-subtitle>
          </v-card-item>
          
          <v-card-text class="flex-grow-1">
            <div class="text-caption text-medium-emphasis mb-2">
              Last run: {{ formatDate(report.lastRun) }}
            </div>
            <div class="d-flex flex-wrap gap-1">
              <v-chip
                v-for="(tag, j) in report.tags"
                :key="j"
                size="small"
                variant="outlined"
                label
              >
                {{ tag }}
              </v-chip>
            </div>
          </v-card-text>
          
          <v-card-actions class="mt-auto">
            <v-spacer></v-spacer>
            <v-btn
              size="small"
              variant="text"
              color="primary"
              :to="`/reports/${report.id}`"
            >
              View
            </v-btn>
            <v-btn
              size="small"
              variant="text"
              color="secondary"
              :to="`/reports/${report.id}/edit`"
            >
              Edit
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- New Report Dialog -->
    <v-dialog v-model="showNewReportDialog" max-width="600">
      <v-card>
        <v-card-title>Create New Report</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="createNewReport">
            <v-text-field
              v-model="newReport.title"
              label="Report Title"
              required
              class="mb-4"
            ></v-text-field>
            
            <v-select
              v-model="newReport.category"
              :items="['Financial', 'Operational', 'Analytics']"
              label="Category"
              required
              class="mb-4"
            ></v-select>
            
            <v-textarea
              v-model="newReport.description"
              label="Description"
              rows="3"
              class="mb-4"
            ></v-textarea>
            
            <v-combobox
              v-model="newReport.tags"
              label="Tags"
              multiple
              chips
              class="mb-4"
            ></v-combobox>
            
            <div class="d-flex justify-end gap-2">
              <v-btn
                variant="text"
                @click="showNewReportDialog = false"
              >
                Cancel
              </v-btn>
              <v-btn
                color="primary"
                type="submit"
              >
                Create
              </v-btn>
            </div>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const showNewReportDialog = ref(false);

// Sample reports data - replace with API call
const reports = ref([
  {
    id: 'financial-summary',
    title: 'Financial Summary',
    category: 'Financial',
    lastRun: '2023-11-15T10:30:00',
    tags: ['monthly', 'summary', 'executive']
  },
  {
    id: 'sales-performance',
    title: 'Sales Performance',
    category: 'Operational',
    lastRun: '2023-11-14T15:45:00',
    tags: ['weekly', 'sales', 'performance']
  },
  {
    id: 'expense-analysis',
    title: 'Expense Analysis',
    category: 'Financial',
    lastRun: '2023-11-13T09:15:00',
    tags: ['monthly', 'expenses', 'analysis']
  },
  {
    id: 'customer-segmentation',
    title: 'Customer Segmentation',
    category: 'Analytics',
    lastRun: '2023-11-12T14:20:00',
    tags: ['quarterly', 'customers', 'segmentation']
  },
  {
    id: 'inventory-turnover',
    title: 'Inventory Turnover',
    category: 'Operational',
    lastRun: '2023-11-11T11:05:00',
    tags: ['monthly', 'inventory', 'metrics']
  },
  {
    id: 'cash-flow-forecast',
    title: 'Cash Flow Forecast',
    category: 'Financial',
    lastRun: '2023-11-10T16:30:00',
    tags: ['weekly', 'forecast', 'cash-flow']
  }
]);

const newReport = ref({
  title: '',
  category: 'Financial',
  description: '',
  tags: [] as string[]
});

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const createNewReport = () => {
  // In a real app, this would call an API to save the new report
  const newId = `report-${Date.now()}`;
  
  reports.value.unshift({
    id: newId,
    title: newReport.value.title,
    category: newReport.value.category,
    lastRun: new Date().toISOString(),
    tags: newReport.value.tags
  });
  
  // Reset form and close dialog
  newReport.value = {
    title: '',
    category: 'Financial',
    description: '',
    tags: []
  };
  
  showNewReportDialog.value = false;
};
</script>

<style scoped>
.reports-view {
  max-width: 1600px;
  margin: 0 auto;
}

.gap-2 {
  gap: 8px;
}
</style>
