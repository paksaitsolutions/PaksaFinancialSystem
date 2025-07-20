<template>
  <div class="recurring-journal-data-table">
    <v-data-table
      :headers="headers"
      :items="items"
      :loading="loading"
      :options.sync="options"
      :server-items-length="totalItems"
      :footer-props="{
        'items-per-page-options': [10, 25, 50, 100],
        'show-first-last-page': true,
      }"
      :items-per-page="options.itemsPerPage"
      :page.sync="options.page"
      :sort-by.sync="options.sortBy"
      :sort-desc.sync="options.sortDesc"
      :must-sort="options.mustSort"
      :multi-sort="options.multiSort"
      :group-by.sync="options.groupBy"
      :group-desc.sync="options.groupDesc"
      class="elevation-1"
      dense
    >
      <!-- Name Column -->
      <template v-slot:item.name="{ item }">
        <div class="d-flex align-center">
          <v-icon
            small
            class="mr-2"
            :color="getStatusColor(item.status)"
          >
            {{ getStatusIcon(item.status) }}
          </v-icon>
          <router-link
            :to="{ name: 'gl-recurring-journals-view', params: { id: item.id } }"
            class="text-decoration-none"
          >
            {{ item.name }}
          </router-link>
        </div>
        <div class="caption text--secondary">
          {{ item.description || $t('common.no_description') }}
        </div>
      </template>

      <!-- Frequency Column -->
      <template v-slot:item.frequency="{ item }">
        <div class="text-no-wrap">
          {{ $t(`gl.recurring_journals.frequencies.${item.frequency}`) }}
          <span v-if="item.interval > 1">
            ({{ $t('gl.recurring_journals.every_x', { interval: item.interval }) }})
          </span>
        </div>
      </template>

      <!-- Next Run Column -->
      <template v-slot:item.next_run_date="{ item }">
        <div v-if="item.next_run_date" class="d-flex align-center">
          <v-icon
            small
            :color="isDueSoon(item.next_run_date) ? 'warning' : 'primary'"
            class="mr-1"
          >
            mdi-alarm
          </v-icon>
          <span :class="{ 'font-weight-bold': isDueToday(item.next_run_date) }">
            {{ formatDate(item.next_run_date) }}
          </span>
          <v-tooltip v-if="isDueToday(item.next_run_date)" bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-icon
                small
                color="warning"
                class="ml-1"
                v-bind="attrs"
                v-on="on"
              >
                mdi-alert
              </v-icon>
            </template>
            <span>{{ $t('gl.recurring_journals.due_today') }}</span>
          </v-tooltip>
        </div>
        <span v-else class="text--disabled">
          {{ $t('gl.recurring_journals.no_next_run') }}
        </span>
      </template>

      <!-- Last Run Column -->
      <template v-slot:item.last_run_date="{ item }">
        <div v-if="item.last_run_date" class="d-flex align-center">
          <v-icon small class="mr-1">mdi-update</v-icon>
          {{ formatDate(item.last_run_date) }}
        </div>
        <span v-else class="text--disabled">
          {{ $t('common.never') }}
        </span>
      </template>

      <!-- Status Column -->
      <template v-slot:item.status="{ item }">
        <v-chip
          small
          :color="getStatusColor(item.status)"
          text-color="white"
          class="text-capitalize"
        >
          {{ $t(`gl.recurring_journals.statuses.${item.status}`) }}
        </v-chip>
      </template>

      <!-- Actions Column -->
      <template v-slot:item.actions="{ item }">
        <div class="d-flex justify-end">
          <!-- View Button -->
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                icon
                small
                color="primary"
                v-bind="attrs"
                v-on="on"
                :to="{ name: 'gl-recurring-journals-view', params: { id: item.id } }"
              >
                <v-icon small>mdi-eye</v-icon>
              </v-btn>
            </template>
            <span>{{ $t('common.view') }}</span>
          </v-tooltip>

          <!-- Edit Button -->
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                icon
                small
                color="primary"
                v-bind="attrs"
                v-on="on"
                @click="$emit('edit', item)"
              >
                <v-icon small>mdi-pencil</v-icon>
              </v-btn>
            </template>
            <span>{{ $t('common.edit') }}</span>
          </v-tooltip>

          <!-- Run Now Button (only for active/paused) -->
          <v-tooltip v-if="['active', 'paused'].includes(item.status)" bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                icon
                small
                color="success"
                v-bind="attrs"
                v-on="on"
                @click="$emit('run-now', item)"
              >
                <v-icon small>mdi-play</v-icon>
              </v-btn>
            </template>
            <span>{{ $t('gl.recurring_journals.run_now.title_short') }}</span>
          </v-tooltip>

          <!-- Toggle Status Button -->
          <v-menu offset-y left v-if="item.status !== 'completed' && item.status !== 'cancelled'">
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                icon
                small
                :color="item.status === 'paused' ? 'success' : 'warning'"
                v-bind="attrs"
                v-on="on"
              >
                <v-icon small>
                  {{ item.status === 'paused' ? 'mdi-play' : 'mdi-pause' }}
                </v-icon>
              </v-btn>
            </template>
            <v-list dense>
              <v-list-item
                v-for="status in availableStatuses(item.status)"
                :key="status"
                @click="updateStatus(item, status)"
              >
                <v-list-item-icon class="mr-2">
                  <v-icon small :color="getStatusColor(status)">
                    {{ getStatusIcon(status) }}
                  </v-icon>
                </v-list-item-icon>
                <v-list-item-title>
                  {{ $t(`gl.recurring_journals.actions.${status}`) }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>

          <!-- Delete Button -->
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                icon
                small
                color="error"
                v-bind="attrs"
                v-on="on"
                @click="$emit('delete', item)"
              >
                <v-icon small>mdi-delete</v-icon>
              </v-btn>
            </template>
            <span>{{ $t('common.delete') }}</span>
          </v-tooltip>
        </div>
      </template>

      <!-- No Data State -->
      <template v-slot:no-data>
        <v-alert
          :value="true"
          color="info"
          icon="mdi-information"
          class="ma-2"
        >
          {{ $t('gl.recurring_journals.no_recurring_journals') }}
        </v-alert>
      </template>

      <!-- Loading State -->
      <template v-slot:loading>
        <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
      </template>
    </v-data-table>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator';
import { RecurringJournal, RecurringJournalStatus } from '../../types/recurringJournal';

interface DataOptions {
  page: number;
  itemsPerPage: number;
  sortBy: string[];
  sortDesc: boolean[];
  groupBy: string[];
  groupDesc: boolean[];
  multiSort: boolean;
  mustSort: boolean;
  [key: string]: any;
}

@Component
export default class RecurringJournalDataTable extends Vue {
  @Prop({ type: Array, required: true }) readonly items!: RecurringJournal[];
  @Prop({ type: Boolean, default: false }) readonly loading!: boolean;
  @Prop({ type: Object, required: true }) readonly options!: DataOptions;
  @Prop({ type: Number, default: 0 }) readonly totalItems!: number;

  // Computed
  get headers() {
    return [
      {
        text: this.$t('gl.recurring_journals.fields.name'),
        value: 'name',
        sortable: true,
        width: '25%',
      },
      {
        text: this.$t('gl.recurring_journals.fields.frequency'),
        value: 'frequency',
        sortable: true,
        width: '15%',
      },
      {
        text: this.$t('gl.recurring_journals.fields.next_run_date'),
        value: 'next_run_date',
        sortable: true,
        width: '15%',
      },
      {
        text: this.$t('gl.recurring_journals.fields.last_run_date'),
        value: 'last_run_date',
        sortable: true,
        width: '15%',
      },
      {
        text: this.$t('gl.recurring_journals.fields.status'),
        value: 'status',
        sortable: true,
        width: '15%',
      },
      {
        text: '',
        value: 'actions',
        sortable: false,
        align: 'right',
        width: '15%',
      },
    ];
  }

  // Methods
  formatDate(date: string): string {
    return this.$dayjs(date).format('ll');
  }

  isDueToday(date: string): boolean {
    return this.$dayjs(date).isSame(this.$dayjs(), 'day');
  }

  isDueSoon(date: string, days = 3): boolean {
    const today = this.$dayjs().startOf('day');
    const targetDate = this.$dayjs(date).startOf('day');
    const diffInDays = targetDate.diff(today, 'day');
    return diffInDays >= 0 && diffInDays <= days;
  }

  getStatusColor(status: RecurringJournalStatus): string {
    const colors: Record<RecurringJournalStatus, string> = {
      active: 'success',
      paused: 'warning',
      completed: 'info',
      cancelled: 'error',
    };
    return colors[status] || 'grey';
  }

  getStatusIcon(status: RecurringJournalStatus): string {
    const icons: Record<RecurringJournalStatus, string> = {
      active: 'mdi-calendar-check',
      paused: 'mdi-pause-circle',
      completed: 'mdi-check-circle',
      cancelled: 'mdi-close-circle',
    };
    return icons[status] || 'mdi-calendar-question';
  }

  availableStatuses(currentStatus: RecurringJournalStatus): RecurringJournalStatus[] {
    const statusMap: Record<RecurringJournalStatus, RecurringJournalStatus[]> = {
      active: ['paused', 'completed', 'cancelled'],
      paused: ['active', 'completed', 'cancelled'],
      completed: ['active', 'cancelled'],
      cancelled: ['active', 'paused'],
    };
    return statusMap[currentStatus] || [];
  }

  updateStatus(item: RecurringJournal, status: RecurringJournalStatus) {
    this.$emit('update:status', item, status);
  }
}
</script>

<style scoped>
.recurring-journal-data-table {
  width: 100%;
}

/* Make sure the table takes full width */
:deep(.v-data-table) {
  width: 100%;
}

/* Add some spacing between action buttons */
:deep(.v-data-table td) {
  padding: 0 8px !important;
}

:deep(.v-data-table th) {
  padding: 0 8px !important;
  font-weight: 600;
  white-space: nowrap;
}

/* Style the status chip */
.v-chip {
  height: 24px;
  font-size: 12px;
}

/* Make sure the action buttons are properly aligned */
:deep(.v-data-table__mobile-row) {
  display: flex;
  flex-direction: column;
  padding: 8px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

:deep(.v-data-table__mobile-row__cell) {
  padding: 4px 0;
  width: 100%;
}

:deep(.v-data-table__mobile-row__header) {
  font-weight: 500;
  color: rgba(0, 0, 0, 0.6);
  margin-right: 8px;
  min-width: 120px;
}
</style>
