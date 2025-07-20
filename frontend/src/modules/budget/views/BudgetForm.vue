<template>
  <v-form ref="form" v-model="valid" lazy-validation>
    <v-container fluid>
      <v-row>
        <!-- Basic Info -->
        <v-col cols="12">
          <v-card class="mb-4">
            <v-card-title>Basic Information</v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="budget.name"
                    label="Budget Name"
                    :rules="[v => !!v || 'Name is required']"
                    required
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-select
                    v-model="budget.budget_type"
                    :items="Object.values(BudgetType)"
                    label="Budget Type"
                    :rules="[v => !!v || 'Type is required']"
                    required
                  ></v-select>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="budget.description"
                    label="Description"
                    textarea
                    rows="2"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="budget.total_amount"
                    label="Total Amount"
                    type="number"
                    :rules="[
                      v => !!v || 'Amount is required',
                      v => v > 0 || 'Amount must be greater than 0'
                    ]"
                    required
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="budget.start_date"
                    label="Start Date"
                    type="date"
                    :rules="[v => !!v || 'Start date is required']"
                    required
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="budget.end_date"
                    label="End Date"
                    type="date"
                    :rules="[
                      v => !!v || 'End date is required',
                      v => new Date(v) >= new Date(budget.start_date) || 'End date must be after start date'
                    ]"
                    required
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Budget Lines -->
        <v-col cols="12">
          <v-card class="mb-4">
            <v-card-title>Budget Lines</v-card-title>
            <v-card-text>
              <v-data-table
                :headers="lineHeaders"
                :items="budget.lines"
                :items-per-page="-1"
                hide-default-footer
              >
                <template v-slot:top>
                  <v-btn
                    color="primary"
                    small
                    class="mb-2"
                    @click="addLine"
                  >
                    Add Line
                  </v-btn>
                </template>
                <template v-slot:item.actions="{ item }">
                  <v-btn icon small @click="removeLine(item)">
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Allocations -->
        <v-col cols="12">
          <v-card class="mb-4">
            <v-card-title>Allocations</v-card-title>
            <v-card-text>
              <v-data-table
                :headers="allocationHeaders"
                :items="budget.allocations"
                :items-per-page="-1"
                hide-default-footer
              >
                <template v-slot:top>
                  <v-btn
                    color="primary"
                    small
                    class="mb-2"
                    @click="addAllocation"
                  >
                    Add Allocation
                  </v-btn>
                </template>
                <template v-slot:item.actions="{ item }">
                  <v-btn icon small @click="removeAllocation(item)">
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Rules -->
        <v-col cols="12">
          <v-card>
            <v-card-title>Rules</v-card-title>
            <v-card-text>
              <v-data-table
                :headers="ruleHeaders"
                :items="budget.rules"
                :items-per-page="-1"
                hide-default-footer
              >
                <template v-slot:top>
                  <v-btn
                    color="primary"
                    small
                    class="mb-2"
                    @click="addRule"
                  >
                    Add Rule
                  </v-btn>
                </template>
                <template v-slot:item.actions="{ item }">
                  <v-btn icon small @click="removeRule(item)">
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Actions -->
      <v-row>
        <v-col cols="12" class="text-right">
          <v-btn text @click="cancel">
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            @click="save"
            :loading="saving"
            :disabled="!valid"
          >
            Save
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { BudgetType } from '../../types/budget'

const props = defineProps<{
  budget?: any
}>()

const emit = defineEmits(['save', 'cancel'])

// Form state
const form = ref()
const valid = ref(true)
const saving = ref(false)

// Headers for tables
const lineHeaders = [
  { text: 'Account', value: 'account_id' },
  { text: 'Department', value: 'department_id' },
  { text: 'Project', value: 'project_id' },
  { text: 'Amount', value: 'amount', align: 'right' },
  { text: 'Description', value: 'description' },
  { text: 'Actions', value: 'actions', sortable: false, align: 'right' }
]

const allocationHeaders = [
  { text: 'Department', value: 'department_id' },
  { text: 'Project', value: 'project_id' },
  { text: 'Amount', value: 'amount', align: 'right' },
  { text: 'Percentage', value: 'percentage', align: 'right' },
  { text: 'Description', value: 'description' },
  { text: 'Actions', value: 'actions', sortable: false, align: 'right' }
]

const ruleHeaders = [
  { text: 'Type', value: 'rule_type' },
  { text: 'Data', value: 'rule_data' },
  { text: 'Description', value: 'description' },
  { text: 'Actions', value: 'actions', sortable: false, align: 'right' }
]

// Budget state
const budget = ref({
  name: '',
  description: '',
  budget_type: BudgetType.OPERATIONAL,
  start_date: '',
  end_date: '',
  total_amount: 0,
  lines: [],
  allocations: [],
  rules: []
})

// Watch props for changes
watch(() => props.budget, (newBudget) => {
  if (newBudget) {
    Object.assign(budget.value, newBudget)
  }
}, { immediate: true })

// Methods
const addLine = () => {
  budget.value.lines.push({
    account_id: null,
    department_id: null,
    project_id: null,
    amount: 0,
    description: ''
  })
}

const removeLine = (line: any) => {
  const index = budget.value.lines.indexOf(line)
  if (index !== -1) {
    budget.value.lines.splice(index, 1)
  }
}

const addAllocation = () => {
  budget.value.allocations.push({
    department_id: null,
    project_id: null,
    amount: 0,
    percentage: null,
    description: ''
  })
}

const removeAllocation = (allocation: any) => {
  const index = budget.value.allocations.indexOf(allocation)
  if (index !== -1) {
    budget.value.allocations.splice(index, 1)
  }
}

const addRule = () => {
  budget.value.rules.push({
    rule_type: '',
    rule_data: {},
    description: ''
  })
}

const removeRule = (rule: any) => {
  const index = budget.value.rules.indexOf(rule)
  if (index !== -1) {
    budget.value.rules.splice(index, 1)
  }
}

const save = async () => {
  if (!form.value.validate()) return

  try {
    saving.value = true
    emit('save', budget.value)
  } finally {
    saving.value = false
  }
}

const cancel = () => {
  emit('cancel')
}
</script>
