<template>
  <div class="recurring-journal-list">
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon left>mdi-calendar-refresh</v-icon>
        {{ $t('gl.recurring_journals.title') }}
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          :label="$t('common.search')"
          single-line
          hide-details
          class="mr-4"
          style="max-width: 300px;"
        ></v-text-field>
        <v-btn
          color="primary"
          :to="{ name: 'gl-recurring-journals-create' }"
        >
          <v-icon left>mdi-plus</v-icon>
          {{ $t('gl.recurring_journals.create') }}
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-tabs v-model="activeTab" grow>
          <v-tab>
            <v-icon left>mdi-calendar-check</v-icon>
            {{ $t('gl.recurring_journals.tabs.active') }}
            <v-chip
              v-if="stats.active > 0"
              color="primary"
              x-small
              class="ml-2"
              label
            >
              {{ stats.active }}
            </v-chip>
          </v-tab>
          <v-tab>
            <v-icon left>mdi-pause-circle-outline</v-icon>
            {{ $t('gl.recurring_journals.tabs.paused') }}
            <v-chip
              v-if="stats.paused > 0"
              color="warning"
              x-small
              class="ml-2"
              label
            >
              {{ stats.paused }}
            </v-chip>
          </v-tab>
          <v-tab>
            <v-icon left>mdi-check-circle-outline</v-icon>
            {{ $t('gl.recurring_journals.tabs.completed') }}
            <v-chip
              v-if="stats.completed > 0"
              color="success"
              x-small
              class="ml-2"
              label
            >
              {{ stats.completed }}
            </v-chip>
          </v-tab>
          <v-tab>
            <v-icon left>mdi-close-circle-outline</v-icon>
            {{ $t('gl.recurring_journals.tabs.cancelled') }}
            <v-chip
              v-if="stats.cancelled > 0"
              color="error"
              x-small
              class="ml-2"
              label
            >
              {{ stats.cancelled }}
            </v-chip>
          </v-tab>
        </v-tabs>

        <v-tabs-items v-model="activeTab" class="mt-4">
          <v-tab-item>
            <recurring-journal-data-table
              :items="activeItems"
              :loading="loading"
              :options.sync="options"
              :total-items="pagination.total"
              @edit="editItem"
              @delete="confirmDelete"
              @run-now="runNow"
              @update:status="updateStatus"
            />
          </v-tab-item>
          <v-tab-item>
            <recurring-journal-data-table
              :items="pausedItems"
              :loading="loading"
              :options.sync="pausedOptions"
              :total-items="pausedPagination.total"
              @edit="editItem"
              @delete="confirmDelete"
              @run-now="runNow"
              @update:status="updateStatus"
            />
          </v-tab-item>
          <v-tab-item>
            <recurring-journal-data-table
              :items="completedItems"
              :loading="loading"
              :options.sync="completedOptions"
              :total-items="completedPagination.total"
              @edit="editItem"
              @delete="confirmDelete"
              @run-now="runNow"
              @update:status="updateStatus"
            />
          </v-tab-item>
          <v-tab-item>
            <recurring-journal-data-table
              :items="cancelledItems"
              :loading="loading"
              :options.sync="cancelledOptions"
              :total-items="cancelledPagination.total"
              @edit="editItem"
              @delete="confirmDelete"
              @run-now="runNow"
              @update:status="updateStatus"
            />
          </v-tab-item>
        </v-tabs-items>
      </v-card-text>
    </v-card>

    <!-- Delete Confirmation Dialog -->
    <confirm-dialog
      v-model="deleteDialog"
      :title="$t('common.confirm_delete_title')"
      :message="$t('gl.recurring_journals.delete_confirm', { name: selectedItem?.name })"
      :loading="deleting"
      @confirm="deleteItem"
    />

    <!-- Run Now Dialog -->
    <v-dialog v-model="runDialog" max-width="600" persistent>
      <v-card v-if="selectedItem">
        <v-card-title class="text-h5">
          {{ $t('gl.recurring_journals.run_now.title', { name: selectedItem.name }) }}
        </v-card-title>
        <v-card-text>
          <v-form ref="runForm" v-model="runFormValid">
            <v-menu
              v-model="runDateMenu"
              :close-on-content-click="false"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              min-width="auto"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-text-field
                  v-model="runDateFormatted"
                  :label="$t('gl.recurring_journals.run_now.run_date')"
                  prepend-icon="mdi-calendar"
                  readonly
                  v-bind="attrs"
                  v-on="on"
                  :rules="[v => !!v || $t('validation.required')]"
                  required
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="runDate"
                @input="runDateMenu = false"
                :min="$dayjs().format('YYYY-MM-DD')"
              ></v-date-picker>
            </v-menu>

            <v-checkbox
              v-model="postJournal"
              :label="$t('gl.recurring_journals.run_now.post_journal')"
              hide-details
              class="mt-0"
            ></v-checkbox>

            <v-checkbox
              v-model="notifyOnCompletion"
              :label="$t('gl.recurring_journals.run_now.notify_on_completion')"
              hide-details
              class="mt-0"
            ></v-checkbox>

            <v-expand-transition>
              <v-text-field
                v-if="notifyOnCompletion"
                v-model="notificationEmails"
                :label="$t('gl.recurring_journals.run_notification_emails')"
                :hint="$t('gl.recurring_journals.run_notification_emails_hint')"
                persistent-hint
                multiple
                chips
                small-chips
                :rules="[
                  v => !notifyOnCompletion || (v && v.length > 0) || $t('validation.required')
                ]"
                class="mt-2"
              ></v-text-field>
            </v-expand-transition>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            text
            @click="runDialog = false"
            :disabled="running"
          >
            {{ $t('common.cancel') }}
          </v-btn>
          <v-btn
            color="primary"
            @click="runItem"
            :loading="running"
            :disabled="!runFormValid"
          >
            <v-icon left>mdi-play</v-icon>
            {{ $t('gl.recurring_journals.run_now.run') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator';
import { mapGetters } from 'vuex';
import { RecurringJournal, RecurringJournalStatus } from '@/types/gl/recurringJournal';
import { recurringJournalService } from '@/services/gl/recurringJournalService';
import ConfirmDialog from '@/components/common/ConfirmDialog.vue';
import RecurringJournalDataTable from '@/components/gl/recurring/RecurringJournalDataTable.vue';

interface Pagination {
  page: number;
  itemsPerPage: number;
  sortBy: string[];
  sortDesc: boolean[];
  total: number;
}

interface DataOptions {
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
    ConfirmDialog,
    RecurringJournalDataTable,
  },
  computed: {
    ...mapGetters(['currentCompanyId']),
  },
})
export default class RecurringJournalListView extends Vue {
  loading = false;
  search = '';
  activeTab = 0;
  deleteDialog = false;
  deleting = false;
  runDialog = false;
  running = false;
  runDateMenu = false;
  runFormValid = false;
  postJournal = true;
  notifyOnCompletion = false;
  notificationEmails: string[] = [];
  selectedItem: RecurringJournal | null = null;
  
  // Active items
  activeItems: RecurringJournal[] = [];
  options: DataOptions = {
    page: 1,
    itemsPerPage: 10,
    sortBy: ['next_run_date'],
    sortDesc: [false],
    groupBy: [],
    groupDesc: [],
    multiSort: false,
    mustSort: false,
  };
  
  // Paused items
  pausedItems: RecurringJournal[] = [];
  pausedOptions: DataOptions = {
    page: 1,
    itemsPerPage: 10,
    sortBy: ['name'],
    sortDesc: [false],
    groupBy: [],
    groupDesc: [],
    multiSort: false,
    mustSort: false,
  };
  
  // Completed items
  completedItems: RecurringJournal[] = [];
  completedOptions: DataOptions = {
    page: 1,
    itemsPerPage: 10,
    sortBy: ['last_run_date'],
    sortDesc: [true],
    groupBy: [],
    groupDesc: [],
    multiSort: false,
    mustSort: false,
  };
  
  // Cancelled items
  cancelledItems: RecurringJournal[] = [];
  cancelledOptions: DataOptions = {
    page: 1,
    itemsPerPage: 10,
    sortBy: ['updated_at'],
    sortDesc: [true],
    groupBy: [],
    groupDesc: [],
    multiSort: false,
    mustSort: false,
  };
  
  // Stats
  stats = {
    active: 0,
    paused: 0,
    completed: 0,
    cancelled: 0,
    next_run: null as string | null,
    last_run: null as string | null,
  };
  
  // Computed
  get runDate() {
    return this.$dayjs().format('YYYY-MM-DD');
  }
  
  set runDate(value: string) {
    // No-op, just to make v-model happy
  }
  
  get runDateFormatted() {
    return this.runDate ? this.$dayjs(this.runDate).format('LL') : '';
  }
  
  get pagination(): Pagination {
    return this.getPaginationForTab(this.activeTab);
  }
  
  get pausedPagination(): Pagination {
    return this.getPaginationForTab(1);
  }
  
  get completedPagination(): Pagination {
    return this.getPaginationForTab(2);
  }
  
  get cancelledPagination(): Pagination {
    return this.getPaginationForTab(3);
  }
  
  // Watchers
  @Watch('activeTab')
  onTabChanged() {
    this.fetchData();
  }
  
  @Watch('options', { deep: true })
  onOptionsChanged() {
    this.fetchData();
  }
  
  @Watch('pausedOptions', { deep: true })
  onPausedOptionsChanged() {
    if (this.activeTab === 1) {
      this.fetchData();
    }
  }
  
  @Watch('completedOptions', { deep: true })
  onCompletedOptionsChanged() {
    if (this.activeTab === 2) {
      this.fetchData();
    }
  }
  
  @Watch('cancelledOptions', { deep: true })
  onCancelledOptionsChanged() {
    if (this.activeTab === 3) {
      this.fetchData();
    }
  }
  
  // Hooks
  mounted() {
    this.fetchData();
    this.fetchStats();
  }
  
  // Methods
  getPaginationForTab(tabIndex: number): Pagination {
    const options = [
      this.options,
      this.pausedOptions,
      this.completedOptions,
      this.cancelledOptions,
    ][tabIndex];
    
    return {
      page: options.page,
      itemsPerPage: options.itemsPerPage,
      sortBy: options.sortBy,
      sortDesc: options.sortDesc,
      total: 0, // Will be updated after fetch
    };
  }
  
  async fetchData() {
    try {
      this.loading = true;
      
      // Determine which tab is active and fetch corresponding data
      switch (this.activeTab) {
        case 0: // Active
          await this.fetchActiveItems();
          break;
        case 1: // Paused
          await this.fetchPausedItems();
          break;
        case 2: // Completed
          await this.fetchCompletedItems();
          break;
        case 3: // Cancelled
          await this.fetchCancelledItems();
          break;
      }
      
      // Refresh stats when data changes
      await this.fetchStats();
    } catch (error) {
      this.$error(this.$t('gl.recurring_journals.error_fetching'));
      console.error('Error fetching recurring journals:', error);
    } finally {
      this.loading = false;
    }
  }
  
  async fetchActiveItems() {
    const response = await recurringJournalService.getRecurringJournals({
      status: ['active'],
      page: this.options.page,
      per_page: this.options.itemsPerPage,
      sort_by: this.options.sortBy[0] || 'next_run_date',
      sort_order: this.options.sortDesc[0] ? 'desc' : 'asc',
      search: this.search,
    });
    
    this.activeItems = response.data;
    this.options.page = response.pagination.page;
    this.options.itemsPerPage = response.pagination.per_page;
  }
  
  async fetchPausedItems() {
    const response = await recurringJournalService.getRecurringJournals({
      status: ['paused'],
      page: this.pausedOptions.page,
      per_page: this.pausedOptions.itemsPerPage,
      sort_by: this.pausedOptions.sortBy[0] || 'name',
      sort_order: this.pausedOptions.sortDesc[0] ? 'desc' : 'asc',
      search: this.search,
    });
    
    this.pausedItems = response.data;
    this.pausedOptions.page = response.pagination.page;
    this.pausedOptions.itemsPerPage = response.pagination.per_page;
  }
  
  async fetchCompletedItems() {
    const response = await recurringJournalService.getRecurringJournals({
      status: ['completed'],
      page: this.completedOptions.page,
      per_page: this.completedOptions.itemsPerPage,
      sort_by: this.completedOptions.sortBy[0] || 'last_run_date',
      sort_order: this.completedOptions.sortDesc[0] ? 'desc' : 'asc',
      search: this.search,
    });
    
    this.completedItems = response.data;
    this.completedOptions.page = response.pagination.page;
    this.completedOptions.itemsPerPage = response.pagination.per_page;
  }
  
  async fetchCancelledItems() {
    const response = await recurringJournalService.getRecurringJournals({
      status: ['cancelled'],
      page: this.cancelledOptions.page,
      per_page: this.cancelledOptions.itemsPerPage,
      sort_by: this.cancelledOptions.sortBy[0] || 'updated_at',
      sort_order: this.cancelledOptions.sortDesc[0] ? 'desc' : 'asc',
      search: this.search,
    });
    
    this.cancelledItems = response.data;
    this.cancelledOptions.page = response.pagination.page;
    this.cancelledOptions.itemsPerPage = response.pagination.per_page;
  }
  
  async fetchStats() {
    try {
      const stats = await recurringJournalService.getRecurringJournalStats();
      this.stats = stats;
    } catch (error) {
      console.error('Error fetching recurring journal stats:', error);
    }
  }
  
  editItem(item: RecurringJournal) {
    this.$router.push({
      name: 'gl-recurring-journals-edit',
      params: { id: item.id },
    });
  }
  
  confirmDelete(item: RecurringJournal) {
    this.selectedItem = item;
    this.deleteDialog = true;
  }
  
  async deleteItem() {
    if (!this.selectedItem) return;
    
    try {
      this.deleting = true;
      await recurringJournalService.deleteRecurringJournal(this.selectedItem.id);
      
      this.$success(this.$t('gl.recurring_journals.deleted', { name: this.selectedItem.name }));
      this.fetchData();
      this.deleteDialog = false;
      this.selectedItem = null;
    } catch (error) {
      this.$error(this.$t('gl.recurring_journals.error_deleting'));
      console.error('Error deleting recurring journal:', error);
    } finally {
      this.deleting = false;
    }
  }
  
  runNow(item: RecurringJournal) {
    this.selectedItem = item;
    this.notificationEmails = [this.$store.state.auth.user?.email].filter(Boolean);
    this.runDialog = true;
  }
  
  async runItem() {
    if (!this.selectedItem || !this.runFormValid) return;
    
    try {
      this.running = true;
      
      const params = {
        run_date: this.runDate,
        post_journal: this.postJournal,
        notify_on_completion: this.notifyOnCompletion,
        notification_emails: this.notifyOnCompletion ? this.notificationEmails : undefined,
      };
      
      const response = await recurringJournalService.runRecurringJournal(
        this.selectedItem.id,
        params
      );
      
      if (response.success) {
        this.$success(this.$t('gl.recurring_journals.run_success'));
        this.runDialog = false;
        this.fetchData();
      } else {
        this.$error(response.message || this.$t('gl.recurring_journals.run_error'));
      }
    } catch (error) {
      this.$error(this.$t('gl.recurring_journals.run_error'));
      console.error('Error running recurring journal:', error);
    } finally {
      this.running = false;
    }
  }
  
  async updateStatus(item: RecurringJournal, status: RecurringJournalStatus) {
    try {
      await recurringJournalService.updateRecurringJournalStatus(item.id, status);
      this.$success(this.$t('gl.recurring_journals.status_updated'));
      this.fetchData();
    } catch (error) {
      this.$error(this.$t('gl.recurring_journals.error_updating_status'));
      console.error('Error updating recurring journal status:', error);
    }
  }
}
</script>

<style scoped>
.recurring-journal-list {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
