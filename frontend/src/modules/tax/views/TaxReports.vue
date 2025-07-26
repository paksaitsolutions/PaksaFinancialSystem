<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Tax Reports</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="4">
                <v-select
                  v-model="selectedReport"
                  :items="reportTypes"
                  label="Report Type"
                  item-title="label"
                  item-value="value"
                />
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="startDate"
                  label="Start Date"
                  type="date"
                />
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="endDate"
                  label="End Date"
                  type="date"
                />
              </v-col>
            </v-row>
            <v-btn color="primary" @click="generateReport">Generate Report</v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const selectedReport = ref('');
const startDate = ref('');
const endDate = ref('');

const reportTypes = [
  { label: 'Sales Tax Report', value: 'sales_tax' },
  { label: 'VAT Report', value: 'vat' },
  { label: 'GST Report', value: 'gst' }
];

const generateReport = () => {
  console.log('Generating report:', {
    type: selectedReport.value,
    startDate: startDate.value,
    endDate: endDate.value
  });
};
</script>