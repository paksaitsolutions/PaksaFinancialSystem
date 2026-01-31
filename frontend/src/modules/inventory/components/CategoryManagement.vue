<template>
  <div class="category-management">
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <div>
            <h2 class="m-0">Inventory Categories</h2>
            <p class="text-600 mt-1 mb-0">Organize your inventory items into categories</p>
          </div>
          <Button icon="pi pi-plus" label="Add Category" @click="openCreateDialog" />
        </div>
      </template>
      
      <template #content>
        <!-- Search and Filters -->
        <div class="grid mb-4">
          <div class="col-12 md:col-6">
            <span class="p-input-icon-left w-full">
              <i class="pi pi-search" />
              <InputText v-model="searchQuery" placeholder="Search categories" class="w-full" @input="debouncedFetchCategories" />
            </span>
          </div>
          <div class="col-12 md:col-6">
            <div class="flex justify-content-end gap-2">
              <Button icon="pi pi-refresh" severity="secondary" outlined @click="fetchCategories" />
              <Button icon="pi pi-download" severity="help" outlined @click="exportCategories" />
            </div>
          </div>
        </div>
        
        <!-- Categories Tree/Table -->
        <DataTable
          :value="categories"
          :loading="loading"
          dataKey="id"
          responsiveLayout="scroll"
          class="p-datatable-sm"
        >
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <span class="text-900 font-semibold">{{ categories.length }} categories</span>
            </div>
          </template>
          
          <Column field="code" header="Code" sortable>
            <template #body="{ data }">
              <div class="flex align-items-center gap-2">
                <Tag :value="data.code" severity="info" />
              </div>
            </template>
          </Column>
          
          <Column field="name" header="Name" sortable>
            <template #body="{ data }">
              <div>
                <div class="font-medium text-900">{{ data.name }}</div>
                <div v-if="data.description" class="text-sm text-500 mt-1">{{ data.description }}</div>
              </div>
            </template>
          </Column>
          
          <Column field="item_count" header="Items" sortable>
            <template #body="{ data }">
              <div class="text-center">
                <span class="font-medium">{{ data.item_count || 0 }}</span>
              </div>
            </template>
          </Column>
          
          <Column field="parent" header="Parent Category">
            <template #body="{ data }">
              <Tag v-if="data.parent" :value="data.parent.name" severity="secondary" />
              <span v-else class="text-500">-</span>
            </template>
          </Column>
          
          <Column header="Actions" :exportable="false">
            <template #body="{ data }">
              <div class="flex gap-1">
                <Button icon="pi pi-eye" size="small" text @click="viewCategory(data)" v-tooltip="'View Details'" />
                <Button icon="pi pi-pencil" size="small" text severity="warning" @click="editCategory(data)" v-tooltip="'Edit Category'" />
                <Button icon="pi pi-plus" size="small" text severity="success" @click="addSubcategory(data)" v-tooltip="'Add Subcategory'" />
                <Button icon="pi pi-trash" size="small" text severity="danger" @click="confirmDelete(data)" v-tooltip="'Delete Category'" />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
    
    <!-- Create/Edit Dialog -->
    <Dialog v-model:visible="dialog.show" modal :header="dialog.isEdit ? 'Edit Category' : 'Add Category'" :style="{ width: '600px' }">
      <form @submit.prevent="saveCategory">
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="code" class="font-semibold">Code *</label>
              <InputText
                id="code"
                v-model="dialog.formData.code"
                :class="{ 'p-invalid': errors.code }"
                placeholder="Enter category code"
                class="w-full"
              />
              <small v-if="errors.code" class="p-error">{{ errors.code }}</small>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="name" class="font-semibold">Name *</label>
              <InputText
                id="name"
                v-model="dialog.formData.name"
                :class="{ 'p-invalid': errors.name }"
                placeholder="Enter category name"
                class="w-full"
              />
              <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
            </div>
          </div>
          
          <div class="col-12">
            <div class="field">
              <label for="parent" class="font-semibold">Parent Category</label>
              <Dropdown
                id="parent"
                v-model="dialog.formData.parent_id"
                :options="parentCategoryOptions"
                optionLabel="name"
                optionValue="id"
                placeholder="Select parent category (optional)"
                class="w-full"
                showClear
              />
            </div>
          </div>
          
          <div class="col-12">
            <div class="field">
              <label for="description" class="font-semibold">Description</label>
              <Textarea
                id="description"
                v-model="dialog.formData.description"
                placeholder="Enter category description"
                rows="3"
                class="w-full"
              />
            </div>
          </div>
        </div>
      </form>
      
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="dialog.show = false" />
        <Button
          :label="dialog.isEdit ? 'Update' : 'Create'"
          :loading="dialog.saving"
          @click="saveCategory"
        />
      </template>
    </Dialog>
    
    <!-- Delete Confirmation Dialog -->
    <Dialog v-model:visible="deleteDialog.show" modal header="Delete Category" :style="{ width: '450px' }">
      <div class="flex align-items-center gap-3 mb-3">
        <i class="pi pi-exclamation-triangle text-red-500" style="font-size: 2rem"></i>
        <span>Are you sure you want to delete category <strong>"{{ deleteDialog.category?.name }}"</strong>?</span>
      </div>
      <p class="text-600">This action cannot be undone. All items in this category will need to be reassigned.</p>
      
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="deleteDialog.show = false" />
        <Button label="Delete" severity="danger" @click="deleteCategory" />
      </template>
    </Dialog>
    
    <!-- Category Details Dialog -->
    <Dialog v-model:visible="viewDialog.show" modal header="Category Details" :style="{ width: '700px' }">
      <div v-if="viewDialog.category">
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label class="font-semibold text-900">Code</label>
              <p class="mt-1 mb-0">
                <Tag :value="viewDialog.category.code" severity="info" />
              </p>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label class="font-semibold text-900">Name</label>
              <p class="mt-1 mb-0">{{ viewDialog.category.name }}</p>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label class="font-semibold text-900">Items Count</label>
              <p class="mt-1 mb-0">{{ viewDialog.category.item_count || 0 }} items</p>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label class="font-semibold text-900">Parent Category</label>
              <p class="mt-1 mb-0">
                <Tag v-if="viewDialog.category.parent" :value="viewDialog.category.parent.name" severity="secondary" />
                <span v-else class="text-500">None</span>
              </p>
            </div>
          </div>
          
          <div v-if="viewDialog.category.description" class="col-12">
            <div class="field">
              <label class="font-semibold text-900">Description</label>
              <p class="mt-1 mb-0">{{ viewDialog.category.description }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Close" @click="viewDialog.show = false" />
        <Button label="Edit" severity="warning" @click="editFromView" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { debounce } from '@/utils/debounce'
import { apiClient } from '@/utils/apiClient'
import Dialog from 'primevue/dialog'

// Composables
const toast = useToast()

// Data
const categories = ref([
  {
    id: 1,
    code: 'ELEC',
    name: 'Electronics',
    description: 'Electronic components and devices',
    item_count: 45,
    parent: null
  },
  {
    id: 2,
    code: 'COMP',
    name: 'Components',
    description: 'Hardware components and parts',
    item_count: 23,
    parent: { id: 1, name: 'Electronics' }
  },
  {
    id: 3,
    code: 'ACC',
    name: 'Accessories',
    description: 'Various accessories and add-ons',
    item_count: 12,
    parent: null
  }
])

const loading = ref(false)
const searchQuery = ref('')

// Dialog states
const dialog = reactive({
  show: false,
  isEdit: false,
  saving: false,
  formData: {
    code: '',
    name: '',
    description: '',
    parent_id: null
  },
  editId: null
})

const deleteDialog = reactive({
  show: false,
  category: null
})

const viewDialog = reactive({
  show: false,
  category: null
})

// Validation errors
const errors = reactive({})

// Computed
const parentCategoryOptions = computed(() => {
  return categories.value.filter(cat => 
    !dialog.editId || cat.id !== dialog.editId
  )
})

// Methods
const fetchCategories = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) {
      params.name = searchQuery.value
    }
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500))
    // const response = await apiClient.get('/api/v1/inventory/categories', { params })
    // categories.value = response.data
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load categories' })
    console.error('Error fetching categories:', error)
  } finally {
    loading.value = false
  }
}

const debouncedFetchCategories = debounce(fetchCategories, 300)

const validateForm = () => {
  const newErrors = {}
  
  if (!dialog.formData.code.trim()) {
    newErrors.code = 'Code is required'
  }
  
  if (!dialog.formData.name.trim()) {
    newErrors.name = 'Name is required'
  }
  
  Object.assign(errors, newErrors)
  return Object.keys(newErrors).length === 0
}

const openCreateDialog = () => {
  dialog.isEdit = false
  dialog.editId = null
  dialog.formData = {
    code: '',
    name: '',
    description: '',
    parent_id: null
  }
  Object.keys(errors).forEach(key => delete errors[key])
  dialog.show = true
}

const viewCategory = (category) => {
  viewDialog.category = category
  viewDialog.show = true
}

const editCategory = (category) => {
  dialog.isEdit = true
  dialog.editId = category.id
  dialog.formData = {
    code: category.code,
    name: category.name,
    description: category.description || '',
    parent_id: category.parent?.id || null
  }
  Object.keys(errors).forEach(key => delete errors[key])
  dialog.show = true
}

const editFromView = () => {
  if (viewDialog.category) {
    viewDialog.show = false
    editCategory(viewDialog.category)
  }
}

const addSubcategory = (parentCategory) => {
  dialog.isEdit = false
  dialog.editId = null
  dialog.formData = {
    code: '',
    name: '',
    description: '',
    parent_id: parentCategory.id
  }
  Object.keys(errors).forEach(key => delete errors[key])
  dialog.show = true
}

const saveCategory = async () => {
  if (!validateForm()) {
    toast.add({ severity: 'error', summary: 'Validation Error', detail: 'Please fix the errors and try again' })
    return
  }
  
  dialog.saving = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (dialog.isEdit) {
      // await apiClient.put(`/api/v1/inventory/categories/${dialog.editId}`, dialog.formData)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Category updated successfully' })
    } else {
      // await apiClient.post('/api/v1/inventory/categories', dialog.formData)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Category created successfully' })
    }
    
    dialog.show = false
    fetchCategories()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save category' })
    console.error('Error saving category:', error)
  } finally {
    dialog.saving = false
  }
}

const confirmDelete = (category) => {
  deleteDialog.category = category
  deleteDialog.show = true
}

const deleteCategory = async () => {
  if (!deleteDialog.category) return
  
  try {
    // await apiClient.delete(`/api/v1/inventory/categories/${deleteDialog.category.id}`)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Category deleted successfully' })
    fetchCategories()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete category' })
    console.error('Error deleting category:', error)
  } finally {
    deleteDialog.show = false
    deleteDialog.category = null
  }
}

const exportCategories = () => {
  toast.add({ severity: 'info', summary: 'Export', detail: 'Category export functionality will be implemented' })
}

// Lifecycle hooks
onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.category-management {
  padding: 1.5rem;
}

.field {
  margin-bottom: 1.5rem;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.75rem;
}

:deep(.p-tag) {
  font-size: 0.75rem;
}

:deep(.p-dialog .p-dialog-content) {
  padding: 1.5rem;
}
</style>