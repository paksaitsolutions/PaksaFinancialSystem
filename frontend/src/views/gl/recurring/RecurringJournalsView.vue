<template>
  <v-container fluid class="pa-4">
    <!-- Header -->
    <v-row class="mb-4" no-gutters>
      <v-col cols="12" md="6">
        <h1 class="text-h4 font-weight-bold">
          <v-icon large left>mdi-calendar-refresh</v-icon>
          {{ $t('gl.recurring_journals.title') }}
        </h1>
        <div class="text-body-1 text--secondary mt-1">
          {{ $t('gl.recurring_journals.subtitle') }}
        </div>
      </v-col>
      <v-col cols="12" md="6" class="d-flex align-center justify-end">
        <v-btn
          color="primary"
          @click="showCreateDialog = true"
          :loading="loading"
        >
          <v-icon left>mdi-plus</v-icon>
          {{ $t('gl.recurring_journals.create') }}
        </v-btn>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-card class="mb-4" flat>
      <v-card-text class="pa-4">
        <v-row dense>
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              v-model="filters.search"
              :label="$t('common.search')"
              prepend-inner-icon="mdi-magnify"
              outlined
              dense
              hide-details
              clearable
              @keyup.enter="fetchRecurringJournals"
            ></v-text-field>
          </v-col>
          <v-col cols="6" sm="4" md="2">
            <v-select
              v-model="filters.status"
              :items="statusOptions"
              :label="$t('gl.recurring_journals.fields.status')"
              outlined
              dense
              hide-details
              clearable
            ></v-select>
          </v-col>
          <v-col cols="6" sm="4" md="2">
            <v-select
              v-model="filters.frequency"
              :items="frequencyOptions"
              :label="$t('gl.recurring_journals.fields.frequency')"
              outlined
              dense
              hide-details
              clearable
            ></v-select>
          </v-col>
          <v-col cols="12" sm="4" md="2" class="d-flex align-center">
            <v-checkbox
              v-model="filters.include_inactive"
              :label="$t('common.include_inactive')"
              hide-details
              class="mt-0"
            ></v-checkbox>
          </v-col>
          <v-spacer></v-spacer>
          <v-col cols="auto">
            <v-btn
              color="primary"
              outlined
              @click="fetchRecurringJournals"
              :loading="loading"
              class="mr-2"
            >
              <v-icon left>mdi-filter</v-icon>
              {{ $t('common.apply_filters') }}
            </v-btn>
            <v-btn
              @click="resetFilters"
              :disabled="!hasFilters"
              text
            >
              {{ $t('common.reset') }}
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Data Table -->
    <v-card>
      <v-card-text class="pa-0">
        <recurring-journal-data-table
          ref="dataTable"
          :items="recurringJournals"
          :loading="loading"
          :options="tableOptions"
          :total-items="totalItems"
          @update:options="onTableOptionsChange"
          @edit="editItem"
          @delete="confirmDelete"
          @run-now="runNow"
          @update:status="updateStatus"
        />
      </v-card-text>
    </v-card>

    <!-- Create/Edit Dialog -->
    <v-dialog
      v-model="showDialog"
      max-width="1000"
      persistent
      scrollable
    >
      <recurring-journal-form
        v-if="showDialog"
        :journal="editedItem"
        :loading="saving"
        :editable="!viewMode"
        @create="createRecurringJournal"
        @update="updateRecurringJournal"
        @cancel="closeDialog"
      />
    </v-dialog>

    <!-- Delete Confirmation -->
    <delete-confirmation-dialog
      v-model="showDeleteDialog"
      :item-name="editedItem?.name || ''"
      :loading="deleting"
      @confirm="deleteRecurringJournal"
    />

    <!-- Run Now Confirmation -->
    <v-dialog
      v-model="showRunNowDialog"
      max-width="500"
      persistent
    >
      <v-card>
        <v-card-title class="headline">
          {{ $t('gl.recurring_journals.run_now.title') }}
        </v-card-title>
        <v-card-text>
          <p>{{ $t('gl.recurring_journals.run_now.confirm', { name: editedItem?.name }) }}</p>
          <v-checkbox
            v-model="previewBeforeRun"
            :label="$t('gl.recurring_journals.run_now.preview_before_run')"
            hide-details
            class="mt-2"
          ></v-checkbox>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            text
            @click="showRunNowDialog = false"
            :disabled="running"
          >
            {{ $t('common.cancel') }}
          </v-btn>
          <v-btn
            color="primary"
            @click="executeRunNow"
            :loading="running"
          >
            {{ $t('common.run') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Preview Dialog -->
    <v-dialog
      v-model="showPreviewDialog"
      max-width="1000"
      fullscreen
    >
      <v-card v-if="previewData">
        <v-toolbar color="primary" dark flat>
          <v-toolbar-title>
            {{ $t('gl.recurring_journals.preview.title') }}
          </v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon @click="showPreviewDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-toolbar>
        <v-card-text class="pa-4">
          <v-alert
            type="info"
            class="mb-4"
            border="left"
            colored-border
            elevation="2"
          >
            {{ $t('gl.recurring_journals.preview.instructions') }}
          </v-alert>
          
          <v-tabs v-model="previewTab" grow>
            <v-tab>
              <v-icon left>mdi-format-list-checks</v-icon>
              {{ $t('gl.recurring_journals.preview.occurrences') }}
            </v-tab>
            <v-tab v-if="previewData.journal_entries && previewData.journal_entries.length > 0">
              <v-icon left>mdi-format-list-bulleted</v-icon>
              {{ $t('gl.recurring_journals.preview.journal_entries') }}
              <v-chip
                small
                color="primary"
                text-color="white"
                class="ml-2"
              >
                {{ previewData.journal_entries.length }}
              </v-chip>
            </v-tab>
          </v-tabs>

          <v-tabs-items v-model="previewTab" class="mt-4">
            <!-- Occurrences Tab -->
            <v-tab-item>
              <v-card flat>
                <v-card-text>
                  <v-data-table
                    :headers="previewHeaders"
                    :items="previewData.occurrences || []"
                    :loading="loadingPreview"
                    :items-per-page="10"
                    class="elevation-1"
                  >
                    <template v-slot:item.date="{ item }">
                      {{ formatDate(item.date) }}
                    </template>
                    <template v-slot:item.status="{ item }">
                      <v-chip
                        small
                        :color="getStatusColor(item.status)"
                        text-color="white"
                      >
                        {{ $t(`gl.recurring_journals.occurrence_statuses.${item.status}`) }}
                      </v-chip>
                    </template>
                  </v-data-table>
                </v-card-text>
              </v-card>
            </v-tab-item>

            <!-- Journal Entries Tab -->
            <v-tab-item v-if="previewData.journal_entries && previewData.journal_entries.length > 0">
              <v-card flat>
                <v-card-text>
                  <v-expansion-panels>
                    <v-expansion-panel
                      v-for="(entry, index) in previewData.journal_entries"
                      :key="index"
                    >
                      <v-expansion-panel-header>
                        <div class="d-flex align-center">
                          <v-icon left>mdi-file-document-outline</v-icon>
                          <span class="font-weight-medium">
                            {{ entry.reference || $t('gl.recurring_journals.preview.entry', { number: index + 1 }) }}
                          </span>
                          <v-chip
                            small
                            color="primary"
                            text-color="white"
                            class="ml-2"
                          >
                            {{ formatCurrency(entry.amount) }}
                          </v-chip>
                          <v-chip
                            v-if="entry.status"
                            small
                            :color="getStatusColor(entry.status)"
                            text-color="white"
                            class="ml-2"
                          >
                            {{ $t(`gl.recurring_journals.entry_statuses.${entry.status}`) }}
                          </v-chip>
                        </div>
                      </v-expansion-panel-header>
                      <v-expansion-panel-content>
                        <journal-entry-details
                          :entry="entry"
                          :readonly="true"
                        />
                      </v-expansion-panel-content>
                    </v-expansion-panel>
                  </v-expansion-panels>
                </v-card-text>
              </v-card>
            </v-tab-item>
          </v-tabs-items>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn
            text
            @click="showPreviewDialog = false"
            class="mr-2"
          >
            {{ $t('common.cancel') }}
          </v-btn>
          <v-btn
            color="primary"
            @click="confirmRunNow"
            :loading="running"
          >
            <v-icon left>mdi-play</v-icon>
            {{ $t('gl.recurring_journals.run_now.confirm_run') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator';
import { RecurringJournal, RecurringJournalStatus, RecurringJournalFrequency } from '@/types/gl/recurringJournal';
import { recurringJournalService } from '@/services/gl/recurringJournalService';
import RecurringJournalDataTable from '@/components/gl/recurring/RecurringJournalDataTable.vue';
import RecurringJournalForm from '@/components/gl/recurring/RecurringJournalForm.vue';
import DeleteConfirmationDialog from '@/components/common/DeleteConfirmationDialog.vue';
import JournalEntryDetails from '@/components/gl/JournalEntryDetails.vue';

interface Filters {
  search: string;
  status: string | null;
  frequency: string | null;
  include_inactive: boolean;
}

interface TableOptions {
  page: number;
  itemsPerPage: number;
  sortBy: string[];
  sortDesc: boolean[];
  groupBy: string[];
  groupDesc: boolean[];
  multiSort: boolean;
  mustSort: boolean;
}

@Component({
  components: {
    RecurringJournalDataTable,
    RecurringJournalForm,
    DeleteConfirmationDialog,
    JournalEntryDetails,
  },
})
export default class RecurringJournalsView extends Vue {
  // Data
  loading = false;
  saving = false;
  deleting = false;
  running = false;
  loadingPreview = false;
  
  // UI State
  showDialog = false;
  showDeleteDialog = false;
  showRunNowDialog = false;
  showPreviewDialog = false;
  viewMode = false;
  previewBeforeRun = true;
  previewTab = 0;
  
  // Data
  recurringJournals: RecurringJournal[] = [];
  editedItem: RecurringJournal | null = null;
  previewData: any = null;
  
  // Filters
  filters: Filters = {
    search: '',
    status: null,
    frequency: null,
    include_inactive: false,
  };
  
  // Table options
  tableOptions: TableOptions = {
    page: 1,
    itemsPerPage: 10,
    sortBy: ['next_run_date'],
    sortDesc: [false],
    groupBy: [],
    groupDesc: [],
    multiSort: false,
    mustSort: false,
  };
  
  totalItems = 0;
  
  // Preview headers
  previewHeaders = [
    { text: this.$t('gl.recurring_journals.fields.date'), value: 'date' },
    { text: this.$t('gl.recurring_journals.fields.status'), value: 'status' },
    { text: this.$t('gl.recurring_journals.fields.reference'), value: 'reference' },
    { text: this.$t('gl.recurring_journals.fields.amount'), value: 'amount', align: 'right' },
  ];
  
  // Computed
  get hasFilters(): boolean {
    return (
      !!this.filters.search ||
      this.filters.status !== null ||
      this.filters.frequency !== null ||
      this.filters.include_inactive
    );
  }
  
  get statusOptions() {
    return [
      { text: this.$t('gl.recurring_journals.statuses.active'), value: 'active' },
      { text: this.$t('gl.recurring_journals.statuses.paused'), value: 'paused' },
      { text: this.$t('gl.recurring_journals.statuses.completed'), value: 'completed' },
      { text: this.$t('gl.recurring_journals.statuses.cancelled'), value: 'cancelled' },
    ];
  }
  
  get frequencyOptions() {
    return [
      { text: this.$t('gl.recurring_journals.frequencies.daily'), value: 'daily' },
      { text: this.$t('gl.recurring_journals.frequencies.weekly'), value: 'weekly' },
      { text: this.$t('gl.recurring_journals.frequencies.biweekly'), value: 'biweekly' },
      { text: this.$t('gl.recurring_journals.frequencies.monthly'), value: 'monthly' },
      { text: this.$t('gl.recurring_journals.frequencies.quarterly'), value: 'quarterly' },
      { text: this.$t('gl.recurring_journals.frequencies.semi_annually'), value: 'semi_annually' },
      { text: this.$t('gl.recurring_journals.frequencies.annually'), value: 'annually' },
      { text: this.$t('gl.recurring_journals.frequencies.custom'), value: 'custom' },
    ];
  }
  
  // Lifecycle hooks
  created() {
    this.fetchRecurringJournals();
  }
  
  // Methods
  async fetchRecurringJournals() {
    try {
      this.loading = true;
      
      const params: any = {
        page: this.tableOptions.page,
        per_page: this.tableOptions.itemsPerPage,
        search: this.filters.search,
        status: this.filters.status,
        frequency: this.filters.frequency,
        include_inactive: this.filters.include_inactive,
      };
      
      // Add sorting
      if (this.tableOptions.sortBy.length > 0) {
        params.sort_by = this.tableOptions.sortBy[0];
        params.sort_order = this.tableOptions.sortDesc[0] ? 'desc' : 'asc';
      }
      
      const response = await recurringJournalService.getAll(params);
      this.recurringJournals = response.data;
      this.totalItems = response.meta?.total || 0;
    } catch (error) {
      console.error('Error fetching recurring journals:', error);
      this.$error(this.$t('common.fetch_error'));
    } finally {
      this.loading = false;
    }
  }
  
  onTableOptionsChange(options: TableOptions) {
    this.tableOptions = options;
    this.fetchRecurringJournals();
  }
  
  resetFilters() {
    this.filters = {
      search: '',
      status: null,
      frequency: null,
      include_inactive: false,
    };
    this.fetchRecurringJournals();
  }
  
  // CRUD Operations
  createRecurringJournal() {
    this.showDialog = false;
    this.fetchRecurringJournals();
  }
  
  editItem(item: RecurringJournal) {
    this.editedItem = { ...item };
    this.viewMode = false;
    this.showDialog = true;
  }
  
  viewItem(item: RecurringJournal) {
    this.editedItem = { ...item };
    this.viewMode = true;
    this.showDialog = true;
  }
  
  async updateRecurringJournal(id: string, data: any) {
    try {
      this.saving = true;
      await recurringJournalService.update(id, data);
      this.$success(this.$t('common.update_success'));
      this.showDialog = false;
      this.fetchRecurringJournals();
    } catch (error) {
      console.error('Error updating recurring journal:', error);
      this.$error(this.$t('common.update_error'));
    } finally {
      this.saving = false;
    }
  }
  
  confirmDelete(item: RecurringJournal) {
    this.editedItem = { ...item };
    this.showDeleteDialog = true;
  }
  
  async deleteRecurringJournal() {
    if (!this.editedItem) return;
    
    try {
      this.deleting = true;
      await recurringJournalService.delete(this.editedItem.id);
      this.$success(this.$t('common.delete_success'));
      this.showDeleteDialog = false;
      this.fetchRecurringJournals();
    } catch (error) {
      console.error('Error deleting recurring journal:', error);
      this.$error(this.$t('common.delete_error'));
    } finally {
      this.deleting = false;
    }
  }
  
  // Status Updates
  async updateStatus(item: RecurringJournal, status: RecurringJournalStatus) {
    try {
      await recurringJournalService.updateStatus(item.id, { status });
      this.$success(this.$t('common.update_success'));
      this.fetchRecurringJournals();
    } catch (error) {
      console.error('Error updating status:', error);
      this.$error(this.$t('common.update_error'));
    }
  }
  
  // Run Now Flow
  runNow(item: RecurringJournal) {
    this.editedItem = { ...item };
    
    if (this.previewBeforeRun) {
      this.previewRun();
    } else {
      this.showRunNowDialog = true;
    }
  }
  
  async previewRun() {
    if (!this.editedItem) return;
    
    try {
      this.loadingPreview = true;
      this.previewData = await recurringJournalService.preview(this.editedItem.id);
      this.showPreviewDialog = true;
      this.previewTab = 0;
    } catch (error) {
      console.error('Error previewing run:', error);
      this.$error(this.$t('gl.recurring_journals.preview.error'));
    } finally {
      this.loadingPreview = false;
    }
  }
  
  confirmRunNow() {
    if (this.previewBeforeRun && !this.showPreviewDialog) {
      this.previewRun();
    } else {
      this.executeRunNow();
    }
  }
  
  async executeRunNow() {
    if (!this.editedItem) return;
    
    try {
      this.running = true;
      const response = await recurringJournalService.runNow(this.editedItem.id);
      
      if (response.success) {
        this.$success(this.$t('gl.recurring_journals.run_now.success'));
        this.showRunNowDialog = false;
        this.showPreviewDialog = false;
        this.fetchRecurringJournals();
      } else {
        this.$error(response.message || this.$t('gl.recurring_journals.run_now.error'));
      }
    } catch (error) {
      console.error('Error running recurring journal:', error);
      this.$error(this.$t('gl.recurring_journals.run_now.error'));
    } finally {
      this.running = false;
    }
  }
  
  // Helpers
  closeDialog() {
    this.showDialog = false;
    this.editedItem = null;
  }
  
  formatDate(date: string): string {
    return this.$dayjs(date).format('ll');
  }
  
  formatCurrency(amount: number): string {
    return new Intl.NumberFormat(this.$i18n.locale, {
      style: 'currency',
      currency: this.$store.getters['settings/currency'],
    }).format(amount);
  }
  
  getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      active: 'success',
      paused: 'warning',
      completed: 'info',
      cancelled: 'error',
      draft: 'grey',
      posted: 'primary',
      failed: 'error',
    };
    
    return colors[status] || 'grey';
  }
}
</script>

<style scoped>
/* Add any custom styles here */
</style>
