<template>
  <div class="grid">
    <div class="col-12">
      <div class="flex flex-column md:flex-row justify-content-between align-items-start md:align-items-center mb-4 gap-3">
        <div>
          <h1>Budget Scenarios</h1>
          <p class="text-color-secondary">Compare different budget scenarios and analyze potential outcomes.</p>
        </div>
        <div>
          <Button label="New Scenario" icon="pi pi-plus" class="p-button-success" @click="showNewScenarioDialog" />
        </div>
      </div>
    </div>

    <!-- Scenario Comparison -->
    <div class="col-12">
      <Card>
        <template #title>
          <span>Scenario Comparison</span>
        </template>
        <template #content>
          <TabView>
            <TabPanel header="Optimistic">
              <div class="p-3">
                <div class="mb-3">
                  <h4 class="text-green-600">Best Case Scenario (15% Growth)</h4>
                  <p class="text-color-secondary">Assumes favorable market conditions and strong performance</p>
                </div>
                <Chart type="line" :data="optimisticScenario" :options="scenarioChartOptions" />
                <div class="grid mt-4">
                  <div class="col-6 md:col-3">
                    <div class="p-3 border-round surface-100 text-center">
                      <div class="text-2xl font-bold text-green-600">$874,504</div>
                      <div class="text-sm text-color-secondary">Q4 Projection</div>
                    </div>
                  </div>
                  <div class="col-6 md:col-3">
                    <div class="p-3 border-round surface-100 text-center">
                      <div class="text-2xl font-bold text-green-600">15%</div>
                      <div class="text-sm text-color-secondary">Growth Rate</div>
                    </div>
                  </div>
                  <div class="col-6 md:col-3">
                    <div class="p-3 border-round surface-100 text-center">
                      <div class="text-2xl font-bold text-green-600">High</div>
                      <div class="text-sm text-color-secondary">Confidence</div>
                    </div>
                  </div>
                  <div class="col-6 md:col-3">
                    <div class="p-3 border-round surface-100 text-center">
                      <div class="text-2xl font-bold text-orange-600">Medium</div>
                      <div class="text-sm text-color-secondary">Risk Level</div>
                    </div>
                  </div>
                </div>
              </div>
            </TabPanel>
            <TabPanel header="Realistic">
              <div class="p-3">
                <div class="mb-3">
                  <h4 class="text-blue-600">Most Likely Scenario (8% Growth)</h4>
                  <p class="text-color-secondary">Based on historical data and current market trends</p>
                </div>
                <Chart type="line" :data="realisticScenario" :options="scenarioChartOptions" />
                <div class="grid mt-4">
                  <div class="col-6 md:col-3">
                    <div class="p-3 border-round surface-100 text-center">
                      <div class="text-2xl font-bold text-blue-600">$680,285</div>
                      <div class="text-sm text-color-secondary">Q4 Projection</div>
                    </div>
                  </div>
                  <div class="col-6 md:col-3">
                    <div class="p-3 border-round surface-100 text-center">
                      <div class="text-2xl font-bold text-blue-600">8%</div>
                      <div class="text-sm text-color-secondary">Growth Rate</div>
                    </div>
                  </div>
                  <div class="col-6 md:col-3">
                    <div class="p-3 border-round surface-100 text-center">
                      <div class="text-2xl font-bold text-green-600">High</div>
                      <div class="text-sm text-color-secondary">Confidence</div>
                    </div>
                  </div>
                  <div class="col-6 md:col-3">
                    <div class="p-3 border-round surface-100 text-center">
                      <div class="text-2xl font-bold text-green-600">Low</div>
                      <div class="text-sm text-color-secondary">Risk Level</div>
                    </div>
                  </div>
                </div>
              </div>
            </TabPanel>
            <TabPanel header="Pessimistic">
              <div class="p-3">
                <div class="mb-3">
                  <h4 class="text-red-600">Conservative Scenario (3% Growth)</h4>
                  <p class="text-color-secondary">Assumes challenging market conditions and conservative estimates</p>
                </div>
                <Chart type="line" :data="pessimisticScenario" :options="scenarioChartOptions" />
                <div class="grid mt-4">
                  <div class="col-6 md:col-3">
                    <div class="p-3 border-round surface-100 text-center">
                      <div class="text-2xl font-bold text-red-600">$562,754</div>
                      <div class="text-sm text-color-secondary">Q4 Projection</div>
                    </div>
                  </div>
                  <div class="col-6 md:col-3">
                    <div class="p-3 border-round surface-100 text-center">
                      <div class="text-2xl font-bold text-red-600">3%</div>
                      <div class="text-sm text-color-secondary">Growth Rate</div>
                    </div>
                  </div>
                  <div class="col-6 md:col-3">
                    <div class="p-3 border-round surface-100 text-center">
                      <div class="text-2xl font-bold text-orange-600">Medium</div>
                      <div class="text-sm text-color-secondary">Confidence</div>
                    </div>
                  </div>
                  <div class="col-6 md:col-3">
                    <div class="p-3 border-round surface-100 text-center">
                      <div class="text-2xl font-bold text-red-600">High</div>
                      <div class="text-sm text-color-secondary">Risk Level</div>
                    </div>
                  </div>
                </div>
              </div>
            </TabPanel>
          </TabView>
        </template>
      </Card>
    </div>

    <!-- Scenario Analysis -->
    <div class="col-12 lg:col-8">
      <Card>
        <template #title>
          <span>Scenario Analysis</span>
        </template>
        <template #content>
          <DataTable :value="scenarioAnalysis" responsiveLayout="scroll">
            <Column field="metric" header="Metric" />
            <Column field="optimistic" header="Optimistic">
              <template #body="{ data }">
                <span class="text-green-600 font-medium">{{ data.optimistic }}</span>
              </template>
            </Column>
            <Column field="realistic" header="Realistic">
              <template #body="{ data }">
                <span class="text-blue-600 font-medium">{{ data.realistic }}</span>
              </template>
            </Column>
            <Column field="pessimistic" header="Pessimistic">
              <template #body="{ data }">
                <span class="text-red-600 font-medium">{{ data.pessimistic }}</span>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>

    <div class="col-12 lg:col-4">
      <Card>
        <template #title>
          <span>Scenario Actions</span>
        </template>
        <template #content>
          <div class="flex flex-column gap-3">
            <Button label="Compare All Scenarios" icon="pi pi-chart-bar" class="w-full" @click.prevent="compareScenarios" />
            <Button label="Export Analysis" icon="pi pi-download" outlined class="w-full" @click.prevent="exportAnalysis" />
            <Button label="Create Budget Plan" icon="pi pi-plus" severity="success" class="w-full" @click.prevent="createBudgetPlan" />
            <Button label="Schedule Review" icon="pi pi-calendar" severity="info" class="w-full" @click.prevent="scheduleReview" />
          </div>
        </template>
      </Card>
    </div>
  </div>

  <!-- New Scenario Dialog -->
  <Dialog v-model:visible="showScenarioDialog" header="Create New Scenario" :style="{ width: '500px' }" :modal="true">
    <div class="field">
      <label for="name">Scenario Name</label>
      <InputText id="name" v-model="scenario.name" placeholder="Enter scenario name" />
    </div>
    <div class="field">
      <label for="type">Scenario Type</label>
      <Dropdown id="type" v-model="scenario.type" :options="scenarioTypes" optionLabel="label" optionValue="value" />
    </div>
    <div class="field">
      <label for="growthRate">Growth Rate (%)</label>
      <InputNumber id="growthRate" v-model="scenario.growthRate" :min="-50" :max="100" suffix="%" />
    </div>
    <div class="field">
      <label for="description">Description</label>
      <Textarea id="description" v-model="scenario.description" rows="3" />
    </div>
    <template #footer>
      <Button label="Cancel" icon="pi pi-times" outlined @click="showScenarioDialog = false" />
      <Button label="Create" icon="pi pi-check" @click="saveScenario" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()

const optimisticScenario = ref({
  labels: ['Q1', 'Q2', 'Q3', 'Q4'],
  datasets: [{
    label: 'Optimistic (15% growth)',
    data: [575000, 661250, 760438, 874504],
    borderColor: '#66BB6A',
    backgroundColor: 'rgba(102, 187, 106, 0.1)',
    fill: true
  }]
})

const realisticScenario = ref({
  labels: ['Q1', 'Q2', 'Q3', 'Q4'],
  datasets: [{
    label: 'Realistic (8% growth)',
    data: [540000, 583200, 629856, 680285],
    borderColor: '#42A5F5',
    backgroundColor: 'rgba(66, 165, 245, 0.1)',
    fill: true
  }]
})

const pessimisticScenario = ref({
  labels: ['Q1', 'Q2', 'Q3', 'Q4'],
  datasets: [{
    label: 'Pessimistic (3% growth)',
    data: [515000, 530450, 546364, 562754],
    borderColor: '#EF5350',
    backgroundColor: 'rgba(239, 83, 80, 0.1)',
    fill: true
  }]
})

const scenarioChartOptions = ref({
  responsive: true,
  plugins: { legend: { position: 'top' } },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { callback: (value) => '$' + value.toLocaleString() }
    }
  }
})

const scenarioAnalysis = ref([
  { metric: 'Total Revenue', optimistic: '$2,871,192', realistic: '$2,433,341', pessimistic: '$2,154,568' },
  { metric: 'Growth Rate', optimistic: '15%', realistic: '8%', pessimistic: '3%' },
  { metric: 'Risk Level', optimistic: 'Medium', realistic: 'Low', pessimistic: 'High' },
  { metric: 'Confidence', optimistic: '75%', realistic: '90%', pessimistic: '65%' },
  { metric: 'Break-even Point', optimistic: 'Q1', realistic: 'Q2', pessimistic: 'Q3' }
])

const showScenarioDialog = ref(false)
const scenario = ref({
  name: '',
  type: 'realistic',
  growthRate: 8,
  description: ''
})

const scenarioTypes = [
  { label: 'Optimistic', value: 'optimistic' },
  { label: 'Realistic', value: 'realistic' },
  { label: 'Pessimistic', value: 'pessimistic' }
]

const showNewScenarioDialog = () => {
  scenario.value = { name: '', type: 'realistic', growthRate: 8, description: '' }
  showScenarioDialog.value = true
}

const saveScenario = () => {
  showScenarioDialog.value = false
  toast.add({ severity: 'success', summary: 'Scenario Created', detail: `${scenario.value.name} scenario has been created` })
}

const compareScenarios = () => {
  console.log('Compare scenarios clicked')
  toast.add({ severity: 'info', summary: 'Comparing Scenarios', detail: 'Scenario comparison analysis started' })
}

const exportAnalysis = () => {
  console.log('Export analysis clicked')
  toast.add({ severity: 'info', summary: 'Exporting', detail: 'Scenario analysis is being exported' })
}

const createBudgetPlan = () => {
  console.log('Create budget plan clicked')
  toast.add({ severity: 'success', summary: 'Budget Plan', detail: 'Creating budget plan from selected scenario' })
}

const scheduleReview = () => {
  console.log('Schedule review clicked')
  toast.add({ severity: 'info', summary: 'Review Scheduled', detail: 'Scenario review has been scheduled' })
}
</script>