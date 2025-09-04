<template>
  <div class="email-templates">
    <div class="grid">
      <div class="col-12">
        <div class="flex justify-content-between align-items-center mb-4">
          <div>
            <h1>Email Templates</h1>
            <Breadcrumb :home="home" :model="breadcrumbItems" class="mb-4" />
          </div>
          <div>
            <Button 
              label="New Template" 
              icon="pi pi-plus" 
              class="p-button-success" 
              @click="showNewTemplateDialog" 
            />
          </div>
        </div>
      </div>

      <!-- Template List -->
      <div class="col-12">
        <Card>
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <h3>Templates</h3>
              <div>
                <span class="p-input-icon-left">
                  <i class="pi pi-search" />
                  <InputText 
                    v-model="filters.global.value" 
                    placeholder="Search templates..." 
                    class="w-full"
                  />
                </span>
              </div>
            </div>
          </template>
          <template #content>
            <DataTable 
              :value="templates" 
              :paginator="true" 
              :rows="10"
              :loading="loading"
              :filters="filters"
              :globalFilterFields="['name', 'subject', 'category']"
              :rowsPerPageOptions="[5,10,25,50]"
              class="p-datatable-sm"
              stripedRows
            >
              <template #empty>No templates found.</template>
              <Column field="name" header="Name" :sortable="true">
                <template #body="{ data }">
                  <span class="font-medium">{{ data.name }}</span>
                </template>
              </Column>
              <Column field="subject" header="Subject" :sortable="true" />
              <Column field="category" header="Category" :sortable="true" />
              <Column field="updatedAt" header="Last Updated" :sortable="true">
                <template #body="{ data }">
                  {{ formatDate(data.updatedAt) }}
                </template>
              </Column>
              <Column header="Actions" style="width: 10rem">
                <template #body="{ data }">
                  <div class="flex gap-2">
                    <Button 
                      icon="pi pi-eye" 
                      class="p-button-text p-button-sm" 
                      @click="viewTemplate(data)" 
                      v-tooltip.top="'Preview Template'"
                    />
                    <Button 
                      icon="pi pi-pencil" 
                      class="p-button-text p-button-sm p-button-warning" 
                      @click="editTemplate(data)" 
                      v-tooltip.top="'Edit Template'"
                    />
                    <Button 
                      icon="pi pi-trash" 
                      class="p-button-text p-button-sm p-button-danger" 
                      @click="confirmDeleteTemplate(data)" 
                      v-tooltip.top="'Delete Template'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <!-- Template Editor Dialog -->
    <Dialog 
      v-model:visible="templateDialog" 
      :style="{width: '800px', maxWidth: '90vw'}" 
      :header="editing ? 'Edit Email Template' : 'New Email Template'" 
      :modal="true"
      :closable="!submitting"
      :closeOnEscape="!submitting"
      class="p-fluid"
    >
      <div class="field">
        <label for="name">Template Name <span class="text-red-500">*</span></label>
        <InputText 
          id="name" 
          v-model.trim="template.name" 
          required="true" 
          autofocus 
          :class="{'p-invalid': submitted && !template.name}" 
        />
        <small class="p-error" v-if="submitted && !template.name">Name is required.</small>
      </div>

      <div class="field">
        <label for="category">Category</label>
        <Dropdown 
          id="category" 
          v-model="template.category" 
          :options="categories" 
          optionLabel="name" 
          optionValue="code" 
          placeholder="Select a category"
        />
      </div>

      <div class="field">
        <label for="subject">Email Subject <span class="text-red-500">*</span></label>
        <InputText 
          id="subject" 
          v-model.trim="template.subject" 
          required="true" 
          :class="{'p-invalid': submitted && !template.subject}" 
        />
        <small class="p-error" v-if="submitted && !template.subject">Subject is required.</small>
      </div>

      <div class="field">
        <label for="description">Description</label>
        <Textarea id="description" v-model="template.description" rows="2" />
      </div>

      <div class="field">
        <div class="flex justify-content-between align-items-center mb-2">
          <label>Email Content <span class="text-red-500">*</span></label>
          <div class="flex gap-2">
            <Button 
              icon="pi pi-code" 
              class="p-button-text p-button-sm" 
              @click="toggleHtmlEditor"
              v-tooltip.top="isHtmlMode ? 'Rich Text Editor' : 'HTML Editor'"
            />
            <Button 
              icon="pi pi-question-circle" 
              class="p-button-text p-button-sm" 
              @click="showVariablesHelp"
              v-tooltip.top="'Available Variables'"
            />
          </div>
        </div>
        
        <div v-if="isHtmlMode" class="h-20rem">
          <Editor 
            v-model="template.content" 
            editorStyle="height: 300px"
            :class="{'p-invalid': submitted && !template.content}"
          >
            <template #toolbar>
              <span class="ql-formats">
                <select class="ql-header">
                  <option value="1">Heading 1</option>
                  <option value="2">Heading 2</option>
                  <option value="3">Heading 3</option>
                  <option selected>Normal</option>
                </select>
                <button class="ql-bold"></button>
                <button class="ql-italic"></button>
                <button class="ql-underline"></button>
                <button class="ql-strike"></button>
              </span>
              <span class="ql-formats">
                <button class="ql-list" value="ordered"></button>
                <button class="ql-list" value="bullet"></button>
                <button class="ql-indent" value="-1"></button>
                <button class="ql-indent" value="+1"></button>
              </span>
              <span class="ql-formats">
                <button class="ql-link"></button>
                <button class="ql-image"></button>
                <button class="ql-video"></button>
              </span>
              <span class="ql-formats">
                <button class="ql-clean"></button>
              </span>
            </template>
          </Editor>
        </div>
        <div v-else class="h-20rem">
          <Textarea 
            v-model="template.content" 
            class="w-full h-full"
            :class="{'p-invalid': submitted && !template.content}"
          />
        </div>
        <small class="p-error" v-if="submitted && !template.content">Content is required.</small>
      </div>

      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="hideDialog" 
          :disabled="submitting"
        />
        <Button 
          :label="editing ? 'Update' : 'Save'" 
          icon="pi pi-check" 
          class="p-button-text" 
          @click="saveTemplate" 
          :loading="submitting"
        />
      </template>
    </Dialog>

    <!-- Preview Dialog -->
    <Dialog 
      v-model:visible="previewDialog" 
      :style="{width: '800px', maxWidth: '90vw'}" 
      :header="previewSubject || 'Email Preview'"
      :modal="true"
      class="preview-dialog"
    >
      <div class="email-preview" v-html="previewContent"></div>
      <template #footer>
        <Button 
          label="Close" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="previewDialog = false"
        />
        <Button 
          label="Send Test" 
          icon="pi pi-send" 
          class="p-button-primary" 
          @click="sendTestEmail"
          :loading="sendingTest"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="deleteTemplateDialog" 
      :style="{width: '450px'}" 
      header="Confirm Deletion" 
      :modal="true"
    >
      <div class="flex align-items-center justify-content-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="template">Are you sure you want to delete <b>{{ template.name }}</b>?</span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="deleteTemplateDialog = false"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-danger" 
          @click="deleteTemplate"
          :loading="deleting"
        />
      </template>
    </Dialog>

    <!-- Variables Help Dialog -->
    <Dialog 
      v-model:visible="variablesHelpDialog" 
      :style="{width: '600px'}" 
      header="Available Variables" 
      :modal="true"
    >
      <p>You can use the following variables in your email templates:</p>
      
      <div class="grid mt-3">
        <div class="col-12 md:col-6">
          <h4>Employee Information</h4>
          <ul class="list-none p-0 m-0">
            <li v-for="varName in employeeVars" :key="varName" class="mb-2">
              <code class="bg-gray-100 p-1 rounded">{{ varName }}</code> - Employee's {{ varName.replace('employee.', '') }}
            </li>
          </ul>
        </div>
        <div class="col-12 md:col-6">
          <h4>Company Information</h4>
          <ul class="list-none p-0 m-0">
            <li v-for="varName in companyVars" :key="varName" class="mb-2">
              <code class="bg-gray-100 p-1 rounded">{{ varName }}</code> - Company's {{ varName.replace('company.', '') }}
            </li>
          </ul>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Close" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="variablesHelpDialog = false"
        />
      </template>
    </Dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useRouter } from 'vue-router';
import { FilterMatchMode } from 'primevue/api';

// PrimeVue Components
import Button from 'primevue/button';
import Card from 'primevue/card';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Editor from 'primevue/editor';
import Breadcrumb from 'primevue/breadcrumb';

// Services
import { EmailTemplateService } from '@/services/email-template.service';

// Types
interface EmailTemplate {
  id?: string;
  name: string;
  subject: string;
  description: string;
  content: string;
  category: string;
  createdAt?: string;
  updatedAt?: string;
}

interface Category {
  name: string;
  code: string;
}

export default defineComponent({
  name: 'HrmEmailTemplates',
  components: {
    Button,
    Card,
    Column,
    DataTable,
    Dialog,
    Dropdown,
    InputText,
    Textarea,
    Editor,
    Breadcrumb
  },
  setup() {
    const toast = useToast();
    const router = useRouter();
    
    // State
    const loading = ref(false);
    const submitting = ref(false);
    const deleting = ref(false);
    const sendingTest = ref(false);
    const templateDialog = ref(false);
    const previewDialog = ref(false);
    const deleteTemplateDialog = ref(false);
    const variablesHelpDialog = ref(false);
    const editing = ref(false);
    const submitted = ref(false);
    const isHtmlMode = ref(true);
    
    const templates = ref<EmailTemplate[]>([]);
    const template = ref<EmailTemplate>({
      name: '',
      subject: '',
      description: '',
      content: '',
      category: ''
    });
    
    const previewContent = ref('');
    const previewSubject = ref('');
    
    const categories = ref<Category[]>([
      { name: 'Employee Onboarding', code: 'onboarding' },
      { name: 'Leave Requests', code: 'leave' },
      { name: 'Payroll', code: 'payroll' },
      { name: 'Announcements', code: 'announcement' },
      { name: 'Other', code: 'other' }
    ]);
    
    const employeeVars = ref([
      'employee.firstName',
      'employee.lastName',
      'employee.fullName',
      'employee.email',
      'employee.position',
      'employee.department',
      'employee.phone',
      'employee.hireDate'
    ]);
    
    const companyVars = ref([
      'company.name',
      'company.address',
      'company.phone',
      'company.email',
      'company.website',
      'company.logo'
    ]);
    
    const filters = ref({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS },
      name: { value: null, matchMode: FilterMatchMode.CONTAINS },
      subject: { value: null, matchMode: FilterMatchMode.CONTAINS },
      category: { value: null, matchMode: FilterMatchMode.EQUALS }
    });
    
    const home = ref({
      icon: 'pi pi-home',
      to: '/'
    });
    
    const breadcrumbItems = ref([
      { label: 'HRM', to: '/hrm' },
      { label: 'Email Templates', to: '/hrm/email-templates' }
    ]);
    
    // Methods
    const loadTemplates = async () => {
      loading.value = true;
      try {
        const response = await EmailTemplateService.getTemplates();
        templates.value = response.data || [];
      } catch (error) {
        console.error('Error loading templates:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load email templates',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };
    
    const showNewTemplateDialog = () => {
      template.value = {
        name: '',
        subject: '',
        description: '',
        content: '',
        category: ''
      };
      editing.value = false;
      submitted.value = false;
      templateDialog.value = true;
    };
    
    const editTemplate = (temp: EmailTemplate) => {
      template.value = { ...temp };
      editing.value = true;
      templateDialog.value = true;
    };
    
    const viewTemplate = (temp: EmailTemplate) => {
      previewContent.value = temp.content;
      previewSubject.value = temp.subject;
      previewDialog.value = true;
    };
    
    const hideDialog = () => {
      templateDialog.value = false;
      submitted.value = false;
    };
    
    const saveTemplate = async () => {
      submitted.value = true;
      
      if (template.value.name && template.value.subject && template.value.content) {
        submitting.value = true;
        
        try {
          if (editing.value && template.value.id) {
            // Update existing template
            await EmailTemplateService.updateTemplate(template.value.id, template.value);
            toast.add({
              severity: 'success',
              summary: 'Success',
              detail: 'Template updated successfully',
              life: 3000
            });
          } else {
            // Create new template
            await EmailTemplateService.createTemplate(template.value);
            toast.add({
              severity: 'success',
              summary: 'Success',
              detail: 'Template created successfully',
              life: 3000
            });
          }
          
          templateDialog.value = false;
          loadTemplates();
        } catch (error) {
          console.error('Error saving template:', error);
          toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to save template',
            life: 3000
          });
        } finally {
          submitting.value = false;
        }
      }
    };
    
    const confirmDeleteTemplate = (temp: EmailTemplate) => {
      template.value = { ...temp };
      deleteTemplateDialog.value = true;
    };
    
    const deleteTemplate = async () => {
      if (template.value.id) {
        deleting.value = true;
        
        try {
          await EmailTemplateService.deleteTemplate(template.value.id);
          
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Template deleted successfully',
            life: 3000
          });
          
          deleteTemplateDialog.value = false;
          loadTemplates();
        } catch (error) {
          console.error('Error deleting template:', error);
          toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete template',
            life: 3000
          });
        } finally {
          deleting.value = false;
        }
      }
    };
    
    const sendTestEmail = async () => {
      sendingTest.value = true;
      
      try {
        // In a real app, you would call an API to send a test email
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Test email sent successfully',
          life: 3000
        });
        
        previewDialog.value = false;
      } catch (error) {
        console.error('Error sending test email:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to send test email',
          life: 3000
        });
      } finally {
        sendingTest.value = false;
      }
    };
    
    const toggleHtmlEditor = () => {
      isHtmlMode.value = !isHtmlMode.value;
    };
    
    const showVariablesHelp = () => {
      variablesHelpDialog.value = true;
    };
    
    const formatDate = (dateString: string): string => {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };
    
    // Lifecycle hooks
    onMounted(() => {
      loadTemplates();
    });
    
    return {
      // State
      loading,
      submitting,
      deleting,
      sendingTest,
      templateDialog,
      previewDialog,
      deleteTemplateDialog,
      variablesHelpDialog,
      editing,
      submitted,
      isHtmlMode,
      templates,
      template,
      categories,
      employeeVars,
      companyVars,
      filters,
      home,
      breadcrumbItems,
      previewContent,
      previewSubject,
      
      // Methods
      loadTemplates,
      showNewTemplateDialog,
      editTemplate,
      viewTemplate,
      hideDialog,
      saveTemplate,
      confirmDeleteTemplate,
      deleteTemplate,
      sendTestEmail,
      toggleHtmlEditor,
      showVariablesHelp,
      formatDate
    };
  }
});
</script>

<style scoped>
.email-templates {
  padding: 1rem;
}

:deep(.p-card) {
  margin-bottom: 1rem;
}

:deep(.p-card .p-card-title) {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

:deep(.p-datatable) {
  font-size: 0.9rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f5f5f5;
  font-weight: 600;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.5rem 1rem;
}

:deep(.p-dialog .p-dialog-header) {
  padding: 1.5rem 1.5rem 0.5rem;
}

:deep(.p-dialog .p-dialog-content) {
  padding: 1.5rem;
}

:deep(.p-dialog .p-dialog-footer) {
  padding: 0.5rem 1.5rem 1.5rem;
}

.field {
  margin-bottom: 1.5rem;
}

/* Email Preview Styles */
.email-preview {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  padding: 1.5rem;
  max-width: 100%;
  overflow: auto;
}

.email-preview :deep(h1),
.email-preview :deep(h2),
.email-preview :deep(h3) {
  color: #1f2937;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

.email-preview :deep(p) {
  margin-bottom: 1rem;
  line-height: 1.6;
  color: #4b5563;
}

.email-preview :deep(a) {
  color: #3b82f6;
  text-decoration: none;
}

.email-preview :deep(a:hover) {
  text-decoration: underline;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  :deep(.p-dialog) {
    width: 95% !important;
  }
  
  .email-preview {
    padding: 1rem;
  }
}
</style>
