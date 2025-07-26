<template>
  <v-card>
    <v-card-title>AR Analytics</v-card-title>
    <v-card-text>
      <v-row>
        <v-col cols="12" md="6">
          <div class="text-subtitle-2 mb-2">Outstanding Receivables</div>
          <div class="text-h4 text-primary">{{ formatCurrency(outstandingAmount) }}</div>
        </v-col>
        <v-col cols="12" md="6">
          <div class="text-subtitle-2 mb-2">Average Collection Days</div>
          <div class="text-h4 text-info">{{ averageCollectionDays }} days</div>
        </v-col>
      </v-row>
      
      <v-divider class="my-4" />
      
      <div class="text-subtitle-2 mb-2">Aging Analysis</div>
      <v-progress-linear
        :model-value="(current / totalReceivables) * 100"
        color="success"
        height="20"
        class="mb-2"
      >
        <template #default>Current: {{ formatCurrency(current) }}</template>
      </v-progress-linear>
      
      <v-progress-linear
        :model-value="(overdue30 / totalReceivables) * 100"
        color="warning"
        height="20"
        class="mb-2"
      >
        <template #default>30+ Days: {{ formatCurrency(overdue30) }}</template>
      </v-progress-linear>
      
      <v-progress-linear
        :model-value="(overdue60 / totalReceivables) * 100"
        color="error"
        height="20"
      >
        <template #default>60+ Days: {{ formatCurrency(overdue60) }}</template>
      </v-progress-linear>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed } from 'vue'

const outstandingAmount = ref(125000)
const averageCollectionDays = ref(32)
const current = ref(75000)
const overdue30 = ref(35000)
const overdue60 = ref(15000)

const totalReceivables = computed(() => current.value + overdue30.value + overdue60.value)

const formatCurrency = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
</script>