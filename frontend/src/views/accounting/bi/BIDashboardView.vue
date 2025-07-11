<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h2>Business Intelligence Dashboard</h2>
        <v-row>
          <v-col v-for="kpi in kpis" :key="kpi.name" cols="4">
            <v-card>
              <v-card-title>{{ kpi.name }}</v-card-title>
              <v-card-text>{{ kpi.value }}</v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row>
          <v-col v-for="widget in widgets" :key="widget.title" cols="6">
            <v-card>
              <v-card-title>{{ widget.title }}</v-card-title>
              <v-card-text>
                <chart-js :data="widget.data" />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <GLAnalyticsWidget />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" md="6">
            <APAnalyticsWidget />
          </v-col>
          <v-col cols="12" md="6">
            <ARAnalyticsWidget />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <CashAnalyticsWidget />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <AIAnalyticsWidget />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getKPIReport, getBIDashboard } from '@/services/biReportingService';
import GLAnalyticsWidget from './GLAnalyticsWidget.vue';
import APAnalyticsWidget from './APAnalyticsWidget.vue';
import ARAnalyticsWidget from './ARAnalyticsWidget.vue';
import CashAnalyticsWidget from './CashAnalyticsWidget.vue';
import AIAnalyticsWidget from './AIAnalyticsWidget.vue';
const kpis = ref([]);
const widgets = ref([]);
onMounted(async () => {
  kpis.value = (await getKPIReport()).kpis;
  widgets.value = (await getBIDashboard()).widgets;
});
</script>
