<template>
  <div class="budget-templates">
    <h2>Budget Templates</h2>
    
    <div class="grid">
      <div class="col-12 lg:col-8">
        <Card>
          <template #title>Available Templates</template>
          <template #content>
            <div class="template-grid">
              <div v-for="template in templates" :key="template.id" class="template-card" @click="selectTemplate(template)">
                <div class="template-icon">
                  <i class="pi pi-file-o text-3xl text-primary"></i>
                </div>
                <h4>{{ template.name }}</h4>
                <p>{{ template.description }}</p>
                <Tag :value="template.category" />
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-4">
        <Card>
          <template #title>Import Options</template>
          <template #content>
            <div class="import-options">
              <div class="field">
                <label>Fiscal Year</label>
                <InputNumber v-model="importOptions.fiscal_year" class="w-full" />
              </div>
              <div class="field">
                <label>Budget Name</label>
                <InputText v-model="importOptions.name" placeholder="Enter budget name" class="w-full" />
              </div>
              <div class="field">
                <label>Adjustment Factor</label>
                <InputNumber v-model="importOptions.adjustment_factor" :min="0.5" :max="2.0" :step="0.05" class="w-full" />
                <small class="text-color-secondary">1.0 = no change, 1.1 = 10% increase</small>
              </div>
              <Button label="Import Template" icon="pi pi-download" @click="importTemplate" :loading="importing" :disabled="!selectedTemplate" class="w-full" />
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import budgetService from '@/services/budgetService'

const router = useRouter()
const toast = useToast()
const importing = ref(false)
const templates = ref([])
const selectedTemplate = ref(null)

const importOptions = ref({
  fiscal_year: new Date().getFullYear(),
  name: '',
  adjustment_factor: 1.0
})

const selectTemplate = (template) => {
  selectedTemplate.value = template
  importOptions.value.name = `${template.name} - FY ${importOptions.value.fiscal_year}`
}

const importTemplate = async () => {
  if (!selectedTemplate.value) return
  
  importing.value = true
  try {
    const budget = await budgetService.importTemplate(selectedTemplate.value.id)
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'Template imported successfully' 
    })
    router.push(`/budget/manage?id=${budget.id}`)
  } catch (error) {
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to import template' 
    })
  } finally {
    importing.value = false
  }
}

onMounted(async () => {
  try {
    templates.value = await budgetService.getTemplates()
  } catch (error) {
    console.error('Error loading templates:', error)
  }
})
</script>

<style scoped>
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.template-card {
  padding: 1.5rem;
  border: 1px solid var(--surface-border);
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.template-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.template-icon {
  margin-bottom: 1rem;
}

.template-card h4 {
  margin: 0.5rem 0;
  color: var(--text-color);
}

.template-card p {
  margin: 0.5rem 0;
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

.import-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>