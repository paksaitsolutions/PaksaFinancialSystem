<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Pay Runs</v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="payRuns"
              :loading="loading"
              class="elevation-1"
            >
              <template v-slot:item.status="{ item }">
                <v-chip :color="getStatusColor(item.status)">
                  {{ item.status }}
                </v-chip>
              </template>
              <template v-slot:item.actions="{ item }">
                <v-btn icon size="small" @click="viewPayRun(item)">
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

interface PayRun {
  id: string;
  period: string;
  status: string;
  employeeCount: number;
  totalAmount: number;
}

const loading = ref(false);
const payRuns = ref<PayRun[]>([]);

const headers = [
  { title: 'Period', key: 'period' },
  { title: 'Status', key: 'status' },
  { title: 'Employees', key: 'employeeCount' },
  { title: 'Total Amount', key: 'totalAmount' },
  { title: 'Actions', key: 'actions', sortable: false }
];

const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    'draft': 'grey',
    'approved': 'green',
    'paid': 'blue'
  };
  return colors[status] || 'grey';
};

const viewPayRun = (payRun: PayRun) => {
  console.log('Viewing pay run:', payRun);
};

onMounted(() => {
  // Load pay runs
});
</script>