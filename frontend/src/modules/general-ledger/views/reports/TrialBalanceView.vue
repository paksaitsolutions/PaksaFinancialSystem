<template>
  <div class="trial-balance-view">
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon left>mdi-scale-balance</v-icon>
        {{ $t('gl.trialBalance.title') }}
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          :loading="exporting"
          :disabled="!trialBalance"
          @click="exportReport"
        >
          <v-icon left>mdi-download</v-icon>
          {{ $t('common.export') }}
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-form @submit.prevent="generateReport" ref="form">
          <v-row>
            <v-col cols="12" md="3">
              <v-menu
                v-model="startDateMenu"
                :close-on-content-click="false"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    v-model="formData.startDate"
                    :label="$t('gl.trialBalance.startDate')"
                    prepend-icon="mdi-calendar"
                    readonly
                    v-bind="attrs"
                    v-on="on"
                    :rules="[v => !!v || $t('validation.required')]"
                    outlined
                    dense
                  ></v-text-field>
                </template>
                <v-date-picker
                  v-model="formData.startDate"
                  @input="startDateMenu = false"
                  :max="formData.endDate || null"
                ></v-date-picker>
              </v-menu>
            </v-col>

            <v-col cols="12" md="3">
              <v-menu
                v-model="endDateMenu"
                :close-on-content-click="false"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    v-model="formData.endDate"
                    :label="$t('gl.trialBalance.endDate')"
                    prepend-icon="mdi-calendar"
                    readonly
                    v-bind="attrs"
                    v-on="on"
                    :rules="[v => !!v || $t('validation.required')]"
                    outlined
                    dense
                  ></v-text-field>
                </template>
                <v-date-picker
                  v-model="formData.endDate"
                  @input="endDateMenu = false"
                  :min="formData.startDate || null"
                ></v-date-picker>
              </v-menu>
            </v-col>

            <v-col cols="12" md="3" class="d-flex align-center">
              <v-checkbox
                v-model="formData.includeZeros"
                :label="$t('gl.trialBalance.includeZeros')"
                class="mt-0 pt-0"
                hide-details
              ></v-checkbox>
            </v-col>

            <v-col cols="12" md="3" class="d-flex align-center">
              <v-btn
                color="primary"
                type="submit"
                :loading="loading"
                block
              >
                <v-icon left>mdi-refresh</v-icon>
                {{ $t('common.generate') }}
              </v-btn>
            </v-col>
          </v-row>
        </v-form>

        <v-divider class="my-4"></v-divider>

        <!-- Loading State -->
        <v-row v-if="loading">
          <v-col cols="12" class="text-center">
            <v-progress-circular
              indeterminate
              color="primary"
            ></v-progress-circular>
            <div class="mt-2">{{ $t('common.loading') }}</div>
          </v-col>
        </v-row>

        <!-- Error State -->
        <v-alert
          v-else-if="error"
          type="error"
          class="mb-4"
        >
          {{ $t('errors.generic', { message: error }) }}
        </v-alert>

        <!-- Empty State -->
        <v-alert
          v-else-if="!trialBalance"
          type="info"
          class="mb-4"
        >
          {{ $t('gl.trialBalance.noData') }}
        </v-alert>

        <!-- Trial Balance Table -->
        <template v-else>
          <div class="d-flex justify-space-between mb-4">
            <div>
              <div class="text-subtitle-1">
                {{ $t('gl.trialBalance.period') }}: {{ formatDate(formData.startDate) }} - {{ formatDate(formData.endDate) }}
              </div>
              <div class="text-caption text--secondary">
                {{ $t('common.generatedOn') }}: {{ formatDateTime(new Date()) }}
              </div>
            </div>
          </div>

          <v-data-table
            :headers="headers"
            :items="trialBalance.entries"
            :items-per-page="-1"
            hide-default-footer
            class="elevation-1"
            dense
          >
            <template v-slot:body.append>
              <tr class="font-weight-bold">
                <td colspan="5" class="text-right">
                  {{ $t('gl.trialBalance.totals') }}:
                </td>
                <td class="text-right">
                  {{ formatCurrency(trialBalance.totalDebit) }}
                </td>
                <td class="text-right">
                  {{ formatCurrency(trialBalance.totalCredit) }}
                </td>
              </tr>
              <tr v-if="Math.abs(trialBalance.difference) > 0.01" class="error--text">
                <td colspan="7" class="text-right">
                  {{ $t('gl.trialBalance.outOfBalance') }}: {{ formatCurrency(Math.abs(trialBalance.difference)) }}
                </td>
              </tr>
            </template>

            <template v-slot:item.openingBalance="{ item }">
              {{ formatCurrency(item.openingBalance) }}
            </template>

            <template v-slot:item.periodActivity="{ item }">
              {{ formatCurrency(item.periodActivity) }}
            </template>

            <template v-slot:item.endingBalance="{ item }">
              {{ formatCurrency(item.endingBalance) }}
            </template>

            <template v-slot:item.debitAmount="{ item }">
              {{ formatCurrency(item.debitAmount) }}
            </template>

            <template v-slot:item.creditAmount="{ item }">
              {{ formatCurrency(item.creditAmount) }}
            </template>
          </v-data-table>
        </template>
      </v-card-text>
    </v-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { format } from 'date-fns';
import { TrialBalanceService } from '@/services/gl/trialBalanceService';
import type { TrialBalance, TrialBalanceParams } from '@/types/gl/trialBalance';
import { formatCurrency, formatDate, formatDateTime } from '@/utils/formatters';

interface TrialBalanceData {
  loading: boolean;
  exporting: boolean;
  error: string | null;
  trialBalance: TrialBalance | null;
  startDateMenu: boolean;
  endDateMenu: boolean;
  formData: {
    startDate: string;
    endDate: string;
    includeZeros: boolean;
  };
  headers: Array<{
    text: string;
    value: string;
    align?: string;
    sortable?: boolean;
  }>;
}

export default defineComponent({
  name: 'TrialBalanceView',
  setup() {
    const { t } = useI18n();
    const loading = ref(false);
    const exporting = ref(false);
    const error = ref<string | null>(null);
    const trialBalance = ref<TrialBalance | null>(null);
    const startDateMenu = ref(false);
    const endDateMenu = ref(false);
    
    const formData = ref({
      startDate: format(new Date(new Date().getFullYear(), 0, 1), 'yyyy-MM-dd'),
      endDate: format(new Date(), 'yyyy-MM-dd'),
      includeZeros: false,
    });
    
    const headers = [
      { text: t('gl.trialBalance.accountCode'), value: 'accountCode' },
      { text: t('gl.trialBalance.accountName'), value: 'accountName' },
      { text: t('gl.trialBalance.accountType'), value: 'accountType' },
      { 
        text: t('gl.trialBalance.openingBalance'), 
        value: 'openingBalance',
        align: 'right',
        sortable: false,
      },
      { 
        text: t('gl.trialBalance.periodActivity'), 
        value: 'periodActivity',
        align: 'right',
        sortable: false,
      },
      { 
        text: t('gl.trialBalance.debitAmount'), 
        value: 'debitAmount',
        align: 'right',
        sortable: false,
      },
      { 
        text: t('gl.trialBalance.creditAmount'), 
        value: 'creditAmount',
        align: 'right',
        sortable: false,
      },
    ];
    
    return {
      t,
      loading,
      exporting,
      error,
      trialBalance,
      startDateMenu,
      endDateMenu,
      formData,
      headers,
      formatCurrency,
      formatDate,
      formatDateTime,
    };
  },
  mounted() {
    this.generateReport();
  },
  methods: {
      async generateReport() {
        const form = this.$refs.form as { validate: () => boolean } | null;
        if (form && !form.validate()) {
          return;
        }

        this.loading = true;
        this.error = null;

        try {
          const params: Omit<TrialBalanceParams, 'format'> = {
            startDate: this.formData.startDate,
            endDate: this.formData.endDate,
            includeZeros: this.formData.includeZeros,
          };

          this.trialBalance = await TrialBalanceService.getTrialBalance(params);
        } catch (err: any) {
          console.error('Error generating trial balance:', err);
          this.error = err.message || this.t('errors.genericMessage');
        } finally {
          this.loading = false;
        }
      },
      
      async exportReport() {
        if (!this.trialBalance) return;

        this.exporting = true;

        try {
          const params: TrialBalanceParams = {
            startDate: this.formData.startDate,
            endDate: this.formData.endDate,
            includeZeros: this.formData.includeZeros,
            format: 'excel',
          };

          await TrialBalanceService.exportTrialBalance(params);
        } catch (err: any) {
          console.error('Error exporting trial balance:', err);
          this.error = err.message || this.t('errors.exportFailed');
        } finally {
          this.exporting = false;
        }
      }
  }
});
</script>

<style scoped>
.trial-balance-view {
  height: 100%;
}

.v-data-table {
  font-size: 0.875rem;
}

.v-data-table /deep/ th {
  font-weight: 600;
  white-space: nowrap;
}

.v-data-table /deep/ td {
  white-space: nowrap;
}

.text-right {
  text-align: right;
}
</style>
