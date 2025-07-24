<template>
  <v-form ref="form" v-model="valid">
    <v-row>
      <v-col cols="12" md="6">
        <v-text-field
          v-model="budgetData.name"
          label="Budget Name"
          :rules="[v => !!v || 'Name is required']"
          required
        ></v-text-field>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-text-field
          v-model="budgetData.amount"
          label="Budget Amount"
          type="number"
          prefix="$"
          :rules="[v => !!v || 'Amount is required', v => v > 0 || 'Amount must be positive']"
          required
        ></v-text-field>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12" md="6">
        <v-select
          v-model="budgetData.type"
          :items="budgetTypes"
          label="Budget Type"
          :rules="[v => !!v || 'Type is required']"
          required
        ></v-select>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-select
          v-model="budgetData.status"
          :items="budgetStatuses"
          label="Status"
          :rules="[v => !!v || 'Status is required']"
          required
        ></v-select>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12" md="6">
        <v-text-field
          v-model="budgetData.startDate"
          label="Start Date"
          type="date"
          :rules="[v => !!v || 'Start date is required']"
          required
        ></v-text-field>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-text-field
          v-model="budgetData.endDate"
          label="End Date"
          type="date"
          :rules="[v => !!v || 'End date is required', validateEndDate]"
          required
        ></v-text-field>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12">
        <v-textarea
          v-model="budgetData.description"
          label="Description"
          rows="3"
        ></v-textarea>
      </v-col>
    </v-row>
    
    <!-- Budget Line Items -->
    <v-row>
      <v-col cols="12">
        <h3 class="mb-4">Budget Line Items</h3>
        
        <v-data-table
          :headers="lineItemHeaders"
          :items="budgetData.lineItems"
          hide-default-footer
          class="mb-4"
        >
          <template v-slot:item.category="{ item, index }">
            <v-select
              v-model="item.category"
              :items="categories"
              label="Category"
              density="compact"
              @update:modelValue="updateLineItem(index)"
            ></v-select>
          </template>
          
          <template v-slot:item.description="{ item, index }">
            <v-text-field
              v-model="item.description"
              placeholder="Description"
              density="compact"
              @update:modelValue="updateLineItem(index)"
            ></v-text-field>
          </template>
          
          <template v-slot:item.amount="{ item, index }">
            <v-text-field
              v-model="item.amount"
              type="number"
              prefix="$"
              density="compact"
              @update:modelValue="updateLineItem(index)"
            ></v-text-field>
          </template>
          
          <template v-slot:item.actions="{ index }">
            <v-btn icon small color="error" @click="removeLineItem(index)">
              <v-icon small>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-data-table>
        
        <v-btn color="primary" variant="outlined" @click="addLineItem" class="mb-4">
          <v-icon left>mdi-plus</v-icon>
          Add Line Item
        </v-btn>
        
        <v-row>
          <v-col cols="6">
            <v-text-field
              :value="formatCurrency(totalLineItems)"
              label="Total Line Items"
              readonly
              variant="outlined"
            ></v-text-field>
          </v-col>
          <v-col cols="6">
            <v-text-field
              :value="formatCurrency(budgetData.amount - totalLineItems)"
              label="Remaining Budget"
              readonly
              variant="outlined"
              :color="budgetData.amount - totalLineItems >= 0 ? 'success' : 'error'"
            ></v-text-field>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12" class="d-flex justify-end">
        <v-btn @click="$emit('cancel')" class="mr-2">Cancel</v-btn>
        <v-btn 
          color="primary" 
          @click="submit" 
          :disabled="!valid || loading"
          :loading="loading"
        >
          Save Budget
        </v-btn>
      </v-col>
    </v-row>
  </v-form>
</template>

<script>
export default {
  name: 'BudgetForm',
  
  props: {
    budget: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['submit', 'cancel'],
  
  data: () => ({
    valid: false,
    budgetData: {
      name: '',
      amount: 0,
      type: 'OPERATIONAL',
      status: 'DRAFT',
      startDate: '',
      endDate: '',
      description: '',
      lineItems: []
    },
    budgetTypes: [
      'OPERATIONAL',
      'CAPITAL',
      'PROJECT',
      'DEPARTMENT'
    ],
    budgetStatuses: [
      'DRAFT',
      'PENDING_APPROVAL',
      'APPROVED',
      'REJECTED',
      'ARCHIVED'
    ],
    categories: [
      'Personnel',
      'Equipment',
      'Supplies',
      'Travel',
      'Training',
      'Utilities',
      'Maintenance',
      'Other'
    ],
    lineItemHeaders: [
      { title: 'Category', key: 'category', sortable: false },
      { title: 'Description', key: 'description', sortable: false },
      { title: 'Amount', key: 'amount', sortable: false },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
  }),
  
  computed: {
    totalLineItems() {
      return this.budgetData.lineItems.reduce((sum, item) => 
        sum + (parseFloat(item.amount) || 0), 0)
    }
  },
  
  watch: {
    budget: {
      handler(newBudget) {
        if (newBudget) {
          this.budgetData = {
            ...newBudget,
            lineItems: newBudget.lineItems || []
          }
        }
      },
      immediate: true,
      deep: true
    }
  },
  
  methods: {
    addLineItem() {
      this.budgetData.lineItems.push({
        category: '',
        description: '',
        amount: 0
      })
    },
    
    removeLineItem(index) {
      this.budgetData.lineItems.splice(index, 1)
    },
    
    updateLineItem(index) {
      // Trigger reactivity
      this.$forceUpdate()
    },
    
    validateEndDate(value) {
      if (!value || !this.budgetData.startDate) return true
      return new Date(value) > new Date(this.budgetData.startDate) || 'End date must be after start date'
    },
    
    async submit() {
      const { valid } = await this.$refs.form.validate()
      if (valid) {
        this.$emit('submit', { ...this.budgetData })
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