<template>
  <div class="variance-analysis">
    <div class="overview">
      <div class="card">
        <h3>Overall Variance</h3>
        <div class="metrics">
          <div class="metric">
            <span class="label">Budgeted:</span>
            <span class="value">{{ formatValue(overview.budgeted) }}</span>
          </div>
          <div class="metric">
            <span class="label">Actual:</span>
            <span class="value">{{ formatValue(overview.actual) }}</span>
          </div>
          <div class="metric">
            <span class="label">Variance:</span>
            <span class="value" :class="{ negative: overview.variance < 0 }">
              {{ formatValue(overview.variance) }}
            </span>
          </div>
          <div class="metric">
            <span class="label">Variance %:</span>
            <span class="value" :class="{ negative: overview.variance_percentage < 0 }">
              {{ formatPercentage(overview.variance_percentage) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab"
        :class="{ active: activeTab === tab }"
        @click="activeTab = tab"
      >
        {{ tab }}
      </button>
    </div>

    <div class="tab-content">
      <div v-if="activeTab === 'Department'" class="department-variance">
        <table class="variance-table">
          <thead>
            <tr>
              <th>Department</th>
              <th>Budgeted</th>
              <th>Actual</th>
              <th>Variance</th>
              <th>Variance %</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(dept, id) in varianceData.by_department" :key="id">
              <td>{{ id }}</td>
              <td>{{ formatValue(dept.budgeted) }}</td>
              <td>{{ formatValue(dept.actual) }}</td>
              <td :class="{ negative: dept.variance < 0 }">
                {{ formatValue(dept.variance) }}
              </td>
              <td :class="{ negative: dept.variance_percentage < 0 }">
                {{ formatPercentage(dept.variance_percentage) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="activeTab === 'Project'" class="project-variance">
        <table class="variance-table">
          <thead>
            <tr>
              <th>Project</th>
              <th>Budgeted</th>
              <th>Actual</th>
              <th>Variance</th>
              <th>Variance %</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(proj, id) in varianceData.by_project" :key="id">
              <td>{{ id }}</td>
              <td>{{ formatValue(proj.budgeted) }}</td>
              <td>{{ formatValue(proj.actual) }}</td>
              <td :class="{ negative: proj.variance < 0 }">
                {{ formatValue(proj.variance) }}
              </td>
              <td :class="{ negative: proj.variance_percentage < 0 }">
                {{ formatPercentage(proj.variance_percentage) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="activeTab === 'Account'" class="account-variance">
        <table class="variance-table">
          <thead>
            <tr>
              <th>Account</th>
              <th>Budgeted</th>
              <th>Actual</th>
              <th>Variance</th>
              <th>Variance %</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(acct, id) in varianceData.by_account" :key="id">
              <td>{{ id }}</td>
              <td>{{ formatValue(acct.budgeted) }}</td>
              <td>{{ formatValue(acct.actual) }}</td>
              <td :class="{ negative: acct.variance < 0 }">
                {{ formatValue(acct.variance) }}
              </td>
              <td :class="{ negative: acct.variance_percentage < 0 }">
                {{ formatPercentage(acct.variance_percentage) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { BudgetVarianceAnalysis } from '@/types/budget'

interface Props {
  data: BudgetVarianceAnalysis
  loading?: boolean
}

const props = defineProps<Props>()

const activeTab = ref('Department')
const tabs = ['Department', 'Project', 'Account']

const overview = computed(() => props.data.overall)

const varianceData = computed(() => props.data)

const formatValue = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

const formatPercentage = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
  }).format(value / 100)
}
</script>

<style scoped>
.variance-analysis {
  background: var(--card-background);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: var(--card-shadow);
}

.overview {
  margin-bottom: 2rem;
}

.card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: var(--card-shadow);
}

h3 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
}

.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--table-header-background);
  border-radius: 4px;
}

.label {
  color: var(--text-color);
  font-weight: 500;
}

.value {
  color: var(--text-color);
  font-weight: 600;
}

.negative {
  color: #ff4444;
}

.tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
}

button {
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  cursor: pointer;
  color: var(--text-color);
  font-weight: 500;
}

button.active {
  border-bottom: 2px solid var(--primary-color);
  color: var(--primary-color);
}

.tab-content {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: var(--card-shadow);
}

.variance-table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

th {
  background: var(--table-header-background);
  color: var(--text-color);
  font-weight: 600;
}

@media (max-width: 768px) {
  .variance-analysis {
    padding: 1rem;
  }
  
  .overview {
    margin-bottom: 1rem;
  }
  
  .metrics {
    grid-template-columns: 1fr;
  }
  
  .tabs {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  button {
    flex: 1;
    max-width: 200px;
  }
  
  .tab-content {
    padding: 1rem;
  }
}
</style>
