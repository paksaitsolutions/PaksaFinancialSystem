<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      <v-icon class="mr-2">mdi-magnify</v-icon>
      Advanced Search & Filter
      <v-spacer />
      <v-btn size="small" @click="clearFilters">Clear All</v-btn>
    </v-card-title>

    <v-card-text>
      <v-row>
        <v-col cols="12" md="3">
          <v-text-field
            v-model="filters.searchTerm"
            label="Search Term"
            prepend-inner-icon="mdi-magnify"
            clearable
          />
        </v-col>
        <v-col cols="12" md="3">
          <v-select
            v-model="filters.accountType"
            :items="accountTypes"
            label="Account Type"
            clearable
          />
        </v-col>
        <v-col cols="12" md="3">
          <v-text-field
            v-model="filters.dateFrom"
            type="date"
            label="Date From"
          />
        </v-col>
        <v-col cols="12" md="3">
          <v-text-field
            v-model="filters.dateTo"
            type="date"
            label="Date To"
          />
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" md="3">
          <v-select
            v-model="filters.status"
            :items="statusOptions"
            label="Status"
            clearable
          />
        </v-col>
        <v-col cols="12" md="3">
          <v-text-field
            v-model="filters.amountFrom"
            type="number"
            label="Amount From"
            prefix="$"
          />
        </v-col>
        <v-col cols="12" md="3">
          <v-text-field
            v-model="filters.amountTo"
            type="number"
            label="Amount To"
            prefix="$"
          />
        </v-col>
        <v-col cols="12" md="3">
          <v-select
            v-model="filters.createdBy"
            :items="users"
            label="Created By"
            clearable
          />
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <v-btn color="primary" @click="applyFilters" :loading="searching">
            <v-icon start>mdi-filter</v-icon>
            Apply Filters
          </v-btn>
          <v-btn class="ml-2" @click="saveFilter">
            <v-icon start>mdi-content-save</v-icon>
            Save Filter
          </v-btn>
        </v-col>
      </v-row>

      <!-- Saved Filters -->
      <v-row v-if="savedFilters.length > 0" class="mt-4">
        <v-col cols="12">
          <v-divider class="mb-4" />
          <h4 class="mb-2">Saved Filters</h4>
          <v-chip-group>
            <v-chip
              v-for="filter in savedFilters"
              :key="filter.id"
              @click="loadFilter(filter)"
              closable
              @click:close="deleteFilter(filter.id)"
            >
              {{ filter.name }}
            </v-chip>
          </v-chip-group>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, watch } from 'vue'

const emit = defineEmits(['filter-changed'])

const searching = ref(false)

const filters = ref({
  searchTerm: '',
  accountType: null,
  dateFrom: '',
  dateTo: '',
  status: null,
  amountFrom: null,
  amountTo: null,
  createdBy: null
})

const accountTypes = ['Asset', 'Liability', 'Equity', 'Revenue', 'Expense']
const statusOptions = ['Draft', 'Posted', 'Reversed', 'Pending Approval']
const users = ['John Doe', 'Jane Smith', 'Mike Johnson']

const savedFilters = ref([
  { id: '1', name: 'Large Transactions', filters: { amountFrom: 10000 } },
  { id: '2', name: 'This Month', filters: { dateFrom: '2024-01-01', dateTo: '2024-01-31' } }
])

const applyFilters = () => {
  searching.value = true
  setTimeout(() => {
    emit('filter-changed', { ...filters.value })
    searching.value = false
  }, 500)
}

const clearFilters = () => {
  Object.keys(filters.value).forEach(key => {
    filters.value[key] = key.includes('amount') ? null : ''
  })
  applyFilters()
}

const saveFilter = () => {
  const name = prompt('Enter filter name:')
  if (name) {
    savedFilters.value.push({
      id: Date.now().toString(),
      name,
      filters: { ...filters.value }
    })
  }
}

const loadFilter = (filter) => {
  Object.assign(filters.value, filter.filters)
  applyFilters()
}

const deleteFilter = (filterId) => {
  const index = savedFilters.value.findIndex(f => f.id === filterId)
  if (index !== -1) {
    savedFilters.value.splice(index, 1)
  }
}

// Auto-apply filters on change
watch(filters, () => {
  applyFilters()
}, { deep: true })
</script>