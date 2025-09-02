<template>
  <div>
    <div class="grid">
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="name" class="block text-900 font-medium mb-2">Budget Name *</label>
          <InputText
            id="name"
            v-model="budgetData.name"
            class="w-full"
            :class="{ 'p-invalid': !budgetData.name && submitted }"
          />
          <small v-if="!budgetData.name && submitted" class="p-error">Name is required</small>
        </div>
      </div>
      
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="amount" class="block text-900 font-medium mb-2">Budget Amount *</label>
          <InputNumber
            id="amount"
            v-model="budgetData.amount"
            mode="currency"
            currency="USD"
            locale="en-US"
            class="w-full"
            :class="{ 'p-invalid': (!budgetData.amount || budgetData.amount <= 0) && submitted }"
          />
          <small v-if="(!budgetData.amount || budgetData.amount <= 0) && submitted" class="p-error">Amount is required and must be positive</small>
        </div>
      </div>
    </div>
    
    <div class="grid">
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="type" class="block text-900 font-medium mb-2">Budget Type *</label>
          <Dropdown
            id="type"
            v-model="budgetData.type"
            :options="budgetTypes"
            class="w-full"
            :class="{ 'p-invalid': !budgetData.type && submitted }"
          />
          <small v-if="!budgetData.type && submitted" class="p-error">Type is required</small>
        </div>
      </div>
      
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="status" class="block text-900 font-medium mb-2">Status *</label>
          <Dropdown
            id="status"
            v-model="budgetData.status"
            :options="budgetStatuses"
            class="w-full"
            :class="{ 'p-invalid': !budgetData.status && submitted }"
          />
          <small v-if="!budgetData.status && submitted" class="p-error">Status is required</small>
        </div>
      </div>
    </div>
    
    <div class="grid">
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="startDate" class="block text-900 font-medium mb-2">Start Date *</label>
          <Calendar
            id="startDate"
            v-model="budgetData.startDate"
            dateFormat="yy-mm-dd"
            class="w-full"
            :class="{ 'p-invalid': !budgetData.startDate && submitted }"
          />
          <small v-if="!budgetData.startDate && submitted" class="p-error">Start date is required</small>
        </div>
      </div>
      
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="endDate" class="block text-900 font-medium mb-2">End Date *</label>
          <Calendar
            id="endDate"
            v-model="budgetData.endDate"
            dateFormat="yy-mm-dd"
            class="w-full"
            :class="{ 'p-invalid': (!budgetData.endDate || !validateEndDate()) && submitted }"
          />
          <small v-if="(!budgetData.endDate || !validateEndDate()) && submitted" class="p-error">End date is required and must be after start date</small>
        </div>
      </div>
    </div>
    
    <div class="grid">
      <div class="col-12">
        <div class="field">
          <label for="description" class="block text-900 font-medium mb-2">Description</label>
          <Textarea
            id="description"
            v-model="budgetData.description"
            rows="3"
            class="w-full"
          />
        </div>
      </div>
    </div>
    
    <!-- Budget Line Items -->
    <div class="grid">
      <div class="col-12">
        <h3 class="mb-4">Budget Line Items</h3>
        
        <DataTable
          :value="budgetData.lineItems"
          class="mb-4"
        >
          <Column field="category" header="Category">
            <template #body="{ data, index }">
              <Dropdown
                v-model="data.category"
                :options="categories"
                class="w-full"
                @change="updateLineItem(index)"
              />
            </template>
          </Column>
          
          <Column field="description" header="Description">
            <template #body="{ data, index }">
              <InputText
                v-model="data.description"
                placeholder="Description"
                class="w-full"
                @input="updateLineItem(index)"
              />
            </template>
          </Column>
          
          <Column field="amount" header="Amount">
            <template #body="{ data, index }">
              <InputNumber
                v-model="data.amount"
                mode="currency"
                currency="USD"
                locale="en-US"
                class="w-full"
                @input="updateLineItem(index)"
              />
            </template>
          </Column>
          
          <Column header="Actions">
            <template #body="{ index }">
              <Button 
                icon="pi pi-trash" 
                size="small" 
                severity="danger" 
                @click="removeLineItem(index)"
              />
            </template>
          </Column>
        </DataTable>
        
        <Button 
          label="Add Line Item" 
          icon="pi pi-plus" 
          severity="info" 
          outlined 
          @click="addLineItem" 
          class="mb-4"
        />
        
        <div class="grid">
          <div class="col-6">
            <div class="field">
              <label class="block text-900 font-medium mb-2">Total Line Items</label>
              <InputText
                :value="formatCurrency(totalLineItems)"
                readonly
                class="w-full"
              />
            </div>
          </div>
          <div class="col-6">
            <div class="field">
              <label class="block text-900 font-medium mb-2">Remaining Budget</label>
              <InputText
                :value="formatCurrency(budgetData.amount - totalLineItems)"
                readonly
                class="w-full"
                :class="budgetData.amount - totalLineItems >= 0 ? 'text-green-600' : 'text-red-600'"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="flex justify-content-end gap-2 mt-4">
      <Button 
        label="Cancel" 
        severity="secondary" 
        @click="$emit('cancel')"
      />
      <Button 
        label="Save Budget" 
        @click="submit" 
        :disabled="loading"
        :loading="loading"
      />
    </div>
  </div>
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
    submitted: false,
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
    
    validateEndDate() {
      if (!this.budgetData.endDate || !this.budgetData.startDate) return false
      return new Date(this.budgetData.endDate) > new Date(this.budgetData.startDate)
    },
    
    isFormValid() {
      return this.budgetData.name && 
             this.budgetData.amount > 0 && 
             this.budgetData.type && 
             this.budgetData.status && 
             this.budgetData.startDate && 
             this.budgetData.endDate && 
             this.validateEndDate()
    },
    
    submit() {
      this.submitted = true
      if (this.isFormValid()) {
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