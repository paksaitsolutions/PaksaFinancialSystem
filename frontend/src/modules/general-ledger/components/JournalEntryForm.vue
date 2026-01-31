<template>
  <Card>
    <template #title>{{ editMode ? 'Edit' : 'New' }} Journal Entry</template>
    
    <template #content>
      <form @submit.prevent="saveEntry">
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="entry_date" class="font-semibold">Entry Date *</label>
              <Calendar
                id="entry_date"
                v-model="journalEntry.entry_date"
                :class="{ 'p-invalid': !journalEntry.entry_date }"
                class="w-full"
                showIcon
              />
              <small v-if="!journalEntry.entry_date" class="p-error">Date is required</small>
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="reference" class="font-semibold">Reference</label>
              <InputText
                id="reference"
                v-model="journalEntry.reference"
                placeholder="Optional reference"
                class="w-full"
              />
            </div>
          </div>
        </div>
        
        <div class="field">
          <label for="description" class="font-semibold">Description *</label>
          <Textarea
            id="description"
            v-model="journalEntry.description"
            :class="{ 'p-invalid': !journalEntry.description }"
            rows="2"
            class="w-full"
          />
          <small v-if="!journalEntry.description" class="p-error">Description is required</small>
        </div>

        <h3 class="mb-4">Journal Entry Lines</h3>
        
        <DataTable
          :value="journalEntry.lines"
          class="mb-4"
          responsiveLayout="scroll"
        >
          <template #empty>No journal lines added.</template>
          <Column field="account_id" header="Account">
            <template #body="{ data, index }">
              <Dropdown
                v-model="data.account_id"
                :options="accounts"
                optionLabel="display_name"
                optionValue="id"
                placeholder="Select Account"
                class="w-full"
                @change="updateLine(index)"
              />
            </template>
          </Column>
          
          <Column field="description" header="Description">
            <template #body="{ data, index }">
              <InputText
                v-model="data.description"
                placeholder="Line description"
                class="w-full"
                @input="updateLine(index)"
              />
            </template>
          </Column>
          
          <Column field="debit_amount" header="Debit">
            <template #body="{ data, index }">
              <InputNumber
                v-model="data.debit_amount"
                mode="currency"
                currency="USD"
                locale="en-US"
                :min="0"
                class="w-full"
                @input="updateLine(index)"
              />
            </template>
          </Column>
          
          <Column field="credit_amount" header="Credit">
            <template #body="{ data, index }">
              <InputNumber
                v-model="data.credit_amount"
                mode="currency"
                currency="USD"
                locale="en-US"
                :min="0"
                class="w-full"
                @input="updateLine(index)"
              />
            </template>
          </Column>
          
          <Column header="Actions" style="width: 4rem">
            <template #body="{ index }">
              <Button
                icon="pi pi-trash"
                class="p-button-text p-button-sm p-button-danger"
                @click="removeLine(index)"
              />
            </template>
          </Column>
        </DataTable>
        
        <Button
          icon="pi pi-plus"
          label="Add Line"
          class="p-button-outlined mb-4"
          @click="addLine"
        />
        
        <div class="grid mt-4">
          <div class="col-6">
            <div class="field">
              <label class="font-semibold">Total Debits</label>
              <InputText
                :value="formatCurrency(totalDebits)"
                readonly
                :class="isBalanced ? 'p-inputtext-success' : 'p-inputtext-error'"
                class="w-full"
              />
            </div>
          </div>
          <div class="col-6">
            <div class="field">
              <label class="font-semibold">Total Credits</label>
              <InputText
                :value="formatCurrency(totalCredits)"
                readonly
                :class="isBalanced ? 'p-inputtext-success' : 'p-inputtext-error'"
                class="w-full"
              />
            </div>
          </div>
        </div>
        
        <Message v-if="!isBalanced" severity="warn" class="mb-4">
          Debits and credits must be equal
        </Message>
      </form>
    </template>
    
    <template #footer>
      <div class="flex justify-content-end gap-2">
        <Button label="Cancel" severity="secondary" @click="$emit('cancel')" />
        <Button
          label="Save Entry"
          :disabled="!isValid || !isBalanced || journalEntry.lines.length < 2"
          @click="saveEntry"
        />
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface JournalLine {
  account_id: number | null
  description: string
  debit_amount: number
  credit_amount: number
}

interface JournalEntry {
  entry_date: Date | null
  description: string
  reference: string
  lines: JournalLine[]
}

const props = defineProps<{
  entry?: JournalEntry | null
}>()

const emit = defineEmits<{
  save: [entry: JournalEntry]
  cancel: []
}>()

const journalEntry = ref<JournalEntry>({
  entry_date: new Date(),
  description: '',
  reference: '',
  lines: []
})

const accounts = ref([
  { id: 1, code: '1010', name: 'Cash', display_name: '1010 - Cash' },
  { id: 2, code: '1200', name: 'Accounts Receivable', display_name: '1200 - Accounts Receivable' },
  { id: 3, code: '2010', name: 'Accounts Payable', display_name: '2010 - Accounts Payable' },
  { id: 4, code: '4010', name: 'Sales Revenue', display_name: '4010 - Sales Revenue' },
  { id: 5, code: '5010', name: 'Cost of Goods Sold', display_name: '5010 - Cost of Goods Sold' }
])

const editMode = computed(() => !!props.entry)

const totalDebits = computed(() => {
  return journalEntry.value.lines.reduce((sum, line) => 
    sum + (Number(line.debit_amount) || 0), 0)
})

const totalCredits = computed(() => {
  return journalEntry.value.lines.reduce((sum, line) => 
    sum + (Number(line.credit_amount) || 0), 0)
})

const isBalanced = computed(() => {
  return Math.abs(totalDebits.value - totalCredits.value) < 0.01
})

const isValid = computed(() => {
  return journalEntry.value.entry_date && journalEntry.value.description
})

const addLine = () => {
  journalEntry.value.lines.push({
    account_id: null,
    description: '',
    debit_amount: 0,
    credit_amount: 0
  })
}

const removeLine = (index: number) => {
  if (journalEntry.value.lines.length > 2) {
    journalEntry.value.lines.splice(index, 1)
  }
}

const updateLine = (index: number) => {
  // Ensure only debit or credit has value, not both
  const line = journalEntry.value.lines[index]
  if (line.debit_amount > 0) {
    line.credit_amount = 0
  } else if (line.credit_amount > 0) {
    line.debit_amount = 0
  }
}

const saveEntry = () => {
  if (isValid.value && isBalanced.value) {
    emit('save', journalEntry.value)
  }
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

onMounted(() => {
  if (props.entry) {
    journalEntry.value = { ...props.entry }
  } else {
    addLine()
    addLine()
  }
})
</script>