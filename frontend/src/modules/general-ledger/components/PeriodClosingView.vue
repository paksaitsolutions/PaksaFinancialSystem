<template>
  <v-container fluid>
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-calendar-lock</v-icon>
        Period Closing
      </v-card-title>

      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-select
              v-model="selectedPeriod"
              :items="periods"
              item-title="name"
              item-value="id"
              label="Select Period"
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-btn 
              color="warning" 
              @click="closePeriod" 
              :loading="closing"
              :disabled="!selectedPeriod"
            >
              <v-icon start>mdi-lock</v-icon>
              Close Period
            </v-btn>
          </v-col>
        </v-row>

        <v-data-table
          :items="periods"
          :headers="periodHeaders"
          class="elevation-1 mt-4"
        >
          <template #item.status="{ item }">
            <v-chip :color="item.status === 'open' ? 'success' : 'error'" size="small">
              {{ item.status }}
            </v-chip>
          </template>
          <template #item.actions="{ item }">
            <v-btn
              v-if="item.status === 'closed'"
              color="primary"
              size="small"
              @click="reopenPeriod(item.id)"
            >
              Reopen
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'

const closing = ref(false)
const selectedPeriod = ref(null)
const periods = ref([
  { id: '1', name: 'January 2024', status: 'open', start_date: '2024-01-01', end_date: '2024-01-31' },
  { id: '2', name: 'February 2024', status: 'closed', start_date: '2024-02-01', end_date: '2024-02-29' }
])

const periodHeaders = [
  { title: 'Period', key: 'name' },
  { title: 'Start Date', key: 'start_date' },
  { title: 'End Date', key: 'end_date' },
  { title: 'Status', key: 'status' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const closePeriod = async () => {
  closing.value = true
  // Mock API call
  setTimeout(() => {
    const period = periods.value.find(p => p.id === selectedPeriod.value)
    if (period) period.status = 'closed'
    closing.value = false
  }, 1000)
}

const reopenPeriod = async (periodId) => {
  const period = periods.value.find(p => p.id === periodId)
  if (period) period.status = 'open'
}
</script>