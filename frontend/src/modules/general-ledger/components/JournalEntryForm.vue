<template>
  <ResponsiveContainer>
    <v-card>
      <v-card-title>{{ editMode ? 'Edit' : 'New' }} Journal Entry</v-card-title>
      
      <v-card-text>
        <v-form ref="form" v-model="valid">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="journalEntry.entry_date"
                label="Entry Date"
                type="date"
                :rules="[v => !!v || 'Date is required']"
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="journalEntry.reference"
                label="Reference"
                placeholder="Optional reference"
              ></v-text-field>
            </v-col>
          </v-row>
          
          <v-textarea
            v-model="journalEntry.description"
            label="Description"
            :rules="[v => !!v || 'Description is required']"
            required
          ></v-textarea>

          <h3 class="mb-4">Journal Entry Lines</h3>
          
          <v-data-table
            :headers="lineHeaders"
            :items="journalEntry.lines"
            hide-default-footer
            class="mb-4"
          >
            <template v-slot:item.account_id="{ item, index }">
              <v-select
                v-model="item.account_id"
                :items="accounts"
                item-title="display_name"
                item-value="id"
                label="Account"
                :rules="[v => !!v || 'Account is required']"
                @update:modelValue="updateLine(index)"
              ></v-select>
            </template>
            
            <template v-slot:item.description="{ item, index }">
              <v-text-field
                v-model="item.description"
                placeholder="Line description"
                @update:modelValue="updateLine(index)"
              ></v-text-field>
            </template>
            
            <template v-slot:item.debit_amount="{ item, index }">
              <v-text-field
                v-model="item.debit_amount"
                type="number"
                step="0.01"
                min="0"
                @update:modelValue="updateLine(index)"
              ></v-text-field>
            </template>
            
            <template v-slot:item.credit_amount="{ item, index }">
              <v-text-field
                v-model="item.credit_amount"
                type="number"
                step="0.01"
                min="0"
                @update:modelValue="updateLine(index)"
              ></v-text-field>
            </template>
            
            <template v-slot:item.actions="{ index }">
              <v-btn icon small color="error" @click="removeLine(index)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </template>
          </v-data-table>
          
          <v-btn color="primary" variant="outlined" @click="addLine" class="mb-4">
            <v-icon left>mdi-plus</v-icon>
            Add Line
          </v-btn>
          
          <v-row class="mt-4">
            <v-col cols="6">
              <v-text-field
                :value="formatCurrency(totalDebits)"
                label="Total Debits"
                readonly
                :color="isBalanced ? 'success' : 'error'"
              ></v-text-field>
            </v-col>
            <v-col cols="6">
              <v-text-field
                :value="formatCurrency(totalCredits)"
                label="Total Credits"
                readonly
                :color="isBalanced ? 'success' : 'error'"
              ></v-text-field>
            </v-col>
          </v-row>
          
          <v-alert v-if="!isBalanced" type="warning" class="mb-4">
            Debits and credits must be equal
          </v-alert>
        </v-form>
      </v-card-text>
      
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="$emit('cancel')">Cancel</v-btn>
        <v-btn 
          color="primary" 
          @click="saveEntry" 
          :disabled="!valid || !isBalanced || journalEntry.lines.length < 2"
        >
          Save Entry
        </v-btn>
      </v-card-actions>
    </v-card>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'

export default {
  name: 'JournalEntryForm',
  components: { ResponsiveContainer },
  
  props: {
    entry: {
      type: Object,
      default: null
    }
  },
  
  emits: ['save', 'cancel'],
  
  data: () => ({
    valid: false,
    journalEntry: {
      entry_date: new Date().toISOString().substr(0, 10),
      description: '',
      reference: '',
      lines: []
    },
    accounts: [
      { id: 1, code: '1010', name: 'Cash', display_name: '1010 - Cash' },
      { id: 2, code: '1200', name: 'Accounts Receivable', display_name: '1200 - Accounts Receivable' },
      { id: 3, code: '2010', name: 'Accounts Payable', display_name: '2010 - Accounts Payable' },
      { id: 4, code: '4010', name: 'Sales Revenue', display_name: '4010 - Sales Revenue' },
      { id: 5, code: '5010', name: 'Cost of Goods Sold', display_name: '5010 - Cost of Goods Sold' }
    ],
    lineHeaders: [
      { title: 'Account', key: 'account_id', sortable: false },
      { title: 'Description', key: 'description', sortable: false },
      { title: 'Debit', key: 'debit_amount', sortable: false },
      { title: 'Credit', key: 'credit_amount', sortable: false },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
  }),
  
  computed: {
    editMode() {
      return !!this.entry
    },
    
    totalDebits() {
      return this.journalEntry.lines.reduce((sum, line) => 
        sum + (parseFloat(line.debit_amount) || 0), 0)
    },
    
    totalCredits() {
      return this.journalEntry.lines.reduce((sum, line) => 
        sum + (parseFloat(line.credit_amount) || 0), 0)
    },
    
    isBalanced() {
      return Math.abs(this.totalDebits - this.totalCredits) < 0.01
    }
  },
  
  mounted() {
    if (this.entry) {
      this.journalEntry = { ...this.entry }
    } else {
      this.addLine()
      this.addLine()
    }
  },
  
  methods: {
    addLine() {
      this.journalEntry.lines.push({
        account_id: null,
        description: '',
        debit_amount: 0,
        credit_amount: 0
      })
    },
    
    removeLine(index) {
      if (this.journalEntry.lines.length > 2) {
        this.journalEntry.lines.splice(index, 1)
      }
    },
    
    updateLine(index) {
      // Ensure only debit or credit has value, not both
      const line = this.journalEntry.lines[index]
      if (line.debit_amount > 0) {
        line.credit_amount = 0
      } else if (line.credit_amount > 0) {
        line.debit_amount = 0
      }
    },
    
    saveEntry() {
      if (this.$refs.form.validate() && this.isBalanced) {
        this.$emit('save', this.journalEntry)
      }
    },
    
    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    }
  }
}
</script>