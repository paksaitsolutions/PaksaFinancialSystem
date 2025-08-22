<template>
  <v-card>
    <v-card-title class="headline">
      {{ $t('gl.journal_entries.details.title') }}
      <v-spacer></v-spacer>
      <v-btn icon @click="$emit('close')">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-card-title>
    
    <v-card-text v-if="loading">
      <v-progress-linear indeterminate color="primary"></v-progress-linear>
    </v-card-text>
    
    <v-card-text v-else-if="error">
      <v-alert type="error" text>
        {{ error }}
      </v-alert>
    </v-card-text>
    
    <v-card-text v-else>
      <!-- Journal Entry Header -->
      <v-row class="mb-4">
        <v-col cols="12" md="4">
          <div class="text-subtitle-2">{{ $t('gl.journal_entries.fields.entry_number') }}</div>
          <div>{{ journalEntry.entry_number || 'N/A' }}</div>
        </v-col>
        <v-col cols="12" md="4">
          <div class="text-subtitle-2">{{ $t('gl.journal_entries.fields.entry_date') }}</div>
          <div>{{ formatDate(journalEntry.entry_date) }}</div>
        </v-col>
        <v-col cols="12" md="4">
          <div class="text-subtitle-2">{{ $t('gl.journal_entries.fields.status') }}</div>
          <v-chip small :color="getStatusColor(journalEntry.status)" text-color="white">
            {{ $t(`gl.journal_entries.statuses.${journalEntry.status}`) }}
          </v-chip>
        </v-col>
        
        <v-col cols="12">
          <div class="text-subtitle-2">{{ $t('gl.journal_entries.fields.description') }}</div>
          <div>{{ journalEntry.description || $t('common.no_description') }}</div>
        </v-col>
      </v-row>
      
      <!-- Journal Entry Lines -->
      <v-data-table
        :headers="headers"
        :items="journalEntry.lines || []"
        :items-per-page="10"
        class="elevation-1"
        dense
      >
        <template v-slot:item.account_number="{ item }">
          {{ item.account_number }}
          <div class="text-caption text--secondary">
            {{ item.account_name }}
          </div>
        </template>
        
        <template v-slot:item.debit="{ item }">
          <div class="text-right">
            {{ formatCurrency(item.debit) }}
          </div>
        </template>
        
        <template v-slot:item.credit="{ item }">
          <div class="text-right">
            {{ formatCurrency(item.credit) }}
          </div>
        </template>
        
        <template v-slot:item.tax_code="{ item }">
          {{ item.tax_code || 'N/A' }}
        </template>
      </v-data-table>
      
      <!-- Totals -->
      <v-row class="mt-4">
        <v-col cols="12" md="6" offset-md="6">
          <v-simple-table dense>
            <template v-slot:default>
              <tbody>
                <tr>
                  <td class="text-subtitle-2">{{ $t('gl.journal_entries.totals.debit') }}:</td>
                  <td class="text-right">{{ formatCurrency(journalEntry.total_debit) }}</td>
                </tr>
                <tr>
                  <td class="text-subtitle-2">{{ $t('gl.journal_entries.totals.credit') }}:</td>
                  <td class="text-right">{{ formatCurrency(journalEntry.total_credit) }}</td>
                </tr>
                <tr>
                  <td class="text-subtitle-2">{{ $t('gl.journal_entries.totals.difference') }}:</td>
                  <td class="text-right" :class="getDifferenceClass">
                    {{ formatCurrency(Math.abs(journalEntry.total_debit - journalEntry.total_credit)) }}
                  </td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-col>
      </v-row>
      
      <!-- Audit Information -->
      <v-divider class="my-4"></v-divider>
      <v-row class="text-caption text--secondary">
        <v-col cols="12" md="4">
          <div>{{ $t('common.created_by') }}: {{ journalEntry.created_by_name || 'N/A' }}</div>
          <div>{{ $t('common.created_at') }}: {{ formatDateTime(journalEntry.created_at) }}</div>
        </v-col>
        <v-col cols="12" md="4" v-if="journalEntry.updated_at">
          <div>{{ $t('common.updated_by') }}: {{ journalEntry.updated_by_name || 'N/A' }}</div>
          <div>{{ $t('common.updated_at') }}: {{ formatDateTime(journalEntry.updated_at) }}</div>
        </v-col>
        <v-col cols="12" md="4" v-if="journalEntry.posted_at">
          <div>{{ $t('common.posted_by') }}: {{ journalEntry.posted_by_name || 'N/A' }}</div>
          <div>{{ $t('common.posted_at') }}: {{ formatDateTime(journalEntry.posted_at) }}</div>
        </v-col>
      </v-row>
    </v-card-text>
    
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="primary" text @click="$emit('close')">
        {{ $t('common.close') }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';
import { JournalEntry } from '../types/journalEntry';

@Component
export default class JournalEntryDetails extends Vue {
  @Prop({ type: [String, Number], required: true }) readonly journalEntryId!: string | number;
  
  loading = false;
  error: string | null = null;
  journalEntry: Partial<JournalEntry> = {};
  
  get headers() {
    return [
      { text: this.$t('gl.journal_entries.fields.account'), value: 'account_number', width: '25%' },
      { text: this.$t('gl.journal_entries.fields.description'), value: 'description', width: '30%' },
      { text: this.$t('gl.journal_entries.fields.debit'), value: 'debit', align: 'right', width: '15%' },
      { text: this.$t('gl.journal_entries.fields.credit'), value: 'credit', align: 'right', width: '15%' },
      { text: this.$t('gl.journal_entries.fields.tax_code'), value: 'tax_code', width: '15%' },
    ];
  }
  
  get getDifferenceClass() {
    const diff = this.journalEntry.total_debit - this.journalEntry.total_credit;
    if (Math.abs(diff) < 0.01) return ''; // Consider them equal if difference is less than 0.01
    return 'error--text font-weight-bold';
  }
  
  async created() {
    await this.fetchJournalEntry();
  }
  
  async fetchJournalEntry() {
    if (!this.journalEntryId) return;
    
    this.loading = true;
    this.error = null;
    
    try {
      // TODO: Replace with actual API call to fetch journal entry details
      // const response = await journalEntryService.getJournalEntry(this.journalEntryId);
      // this.journalEntry = response.data;
      
      // Mock data for now
      this.journalEntry = {
        id: this.journalEntryId,
        entry_number: `JE-${this.journalEntryId}`,
        entry_date: new Date().toISOString().split('T')[0],
        status: 'posted',
        description: 'Sample journal entry for demonstration purposes',
        total_debit: 1000,
        total_credit: 1000,
        created_at: new Date().toISOString(),
        created_by_name: 'System',
        posted_at: new Date().toISOString(),
        posted_by_name: 'System',
        lines: [
          {
            id: 1,
            account_number: '1000',
            account_name: 'Cash and Cash Equivalents',
            description: 'Initial deposit',
            debit: 1000,
            credit: 0,
            tax_code: 'VAT-0',
          },
          {
            id: 2,
            account_number: '3000',
            account_name: 'Owner\'s Equity',
            description: 'Initial capital',
            debit: 0,
            credit: 1000,
            tax_code: 'VAT-0',
          },
        ],
      };
    } catch (error) {
      console.error('Error fetching journal entry:', error);
      this.error = this.$t('common.errors.load_failed', { item: 'journal entry' }).toString();
    } finally {
      this.loading = false;
    }
  }
  
  formatDate(date: string) {
    if (!date) return 'N/A';
    return this.$d(new Date(date), 'short');
  }
  
  formatDateTime(dateTime: string) {
    if (!dateTime) return 'N/A';
    return this.$d(new Date(dateTime), 'long');
  }
  
  formatCurrency(amount: number) {
    if (amount === null || amount === undefined) return '0.00';
    return this.$n(amount, 'currency');
  }
  
  getStatusColor(status: string) {
    const statusColors: Record<string, string> = {
      draft: 'grey',
      posted: 'success',
      reversed: 'warning',
      cancelled: 'error',
    };
    return statusColors[status] || 'secondary';
  }
}
</script>

<style scoped>
.v-data-table {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.v-data-table /deep/ th {
  background-color: #f5f5f5;
  font-weight: 600;
}

.v-data-table /deep/ .v-data-table__empty-wrapper {
  padding: 16px;
  text-align: center;
  color: rgba(0, 0, 0, 0.6);
}
</style>
