<template>
  <div class="report-templates-view">
    <div class="header">
      <h1>Report Templates</h1>
      <Button icon="pi pi-plus" label="New Template" @click="showCreateDialog = true" />
    </div>

    <div class="templates-grid">
      <div 
        v-for="template in templates" 
        :key="template.id"
        class="template-card"
        @click="selectTemplate(template)"
      >
        <div class="template-header">
          <h3>{{ template.template_name }}</h3>
          <Tag v-if="template.is_default" value="Default" severity="info" />
        </div>
        <p>{{ enhancedReportsService.utils.formatReportType(template.report_type) }}</p>
        <div class="template-actions">
          <Button icon="pi pi-pencil" class="p-button-text p-button-sm" @click.stop="editTemplate(template)" />
          <Button icon="pi pi-copy" class="p-button-text p-button-sm" @click.stop="duplicateTemplate(template)" />
          <Button icon="pi pi-trash" class="p-button-text p-button-sm" severity="danger" @click.stop="deleteTemplate(template)" />
        </div>
      </div>
    </div>

    <!-- Create/Edit Template Dialog -->
    <Dialog v-model:visible="showCreateDialog" header="Create Report Template" modal>
      <div class="template-form">
        <div class="field">
          <label>Template Name</label>
          <InputText v-model="templateForm.template_name" />
        </div>
        <div class="field">
          <label>Report Type</label>
          <Dropdown 
            v-model="templateForm.report_type" 
            :options="reportTypes" 
            optionLabel="label" 
            optionValue="value" 
          />
        </div>
        <div class="field">
          <label>Configuration</label>
          <Textarea v-model="templateConfigJson" rows="10" />
        </div>
        <div class="field">
          <Checkbox v-model="templateForm.is_default" inputId="isDefault" />
          <label for="isDefault" class="ml-2">Set as Default Template</label>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="showCreateDialog = false" />
        <Button label="Save" @click="saveTemplate" :loading="saving" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useEnhancedReportsStore } from '@/stores/enhancedReports';
import enhancedReportsService from '@/services/enhancedReportsService';

const store = useEnhancedReportsStore();
const toast = useToast();

const showCreateDialog = ref(false);
const saving = ref(false);
const templates = computed(() => store.templates);

const templateForm = ref({
  template_name: '',
  report_type: '',
  template_config: {},
  is_default: false
});

const templateConfigJson = ref('{}');

const reportTypes = enhancedReportsService.utils.getReportTypes();

const selectTemplate = (template: any) => {
  // Navigate to report with template
  console.log('Selected template:', template);
};

const editTemplate = (template: any) => {
  templateForm.value = { ...template };
  templateConfigJson.value = JSON.stringify(template.template_config, null, 2);
  showCreateDialog.value = true;
};

const duplicateTemplate = async (template: any) => {
  try {
    await store.createTemplate({
      ...template,
      template_name: `${template.template_name} (Copy)`,
      is_default: false
    });
    toast.add({
      severity: 'success',
      summary: 'Template Duplicated',
      detail: 'Template has been duplicated successfully',
      life: 3000
    });
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Duplication Failed',
      detail: 'Failed to duplicate template',
      life: 5000
    });
  }
};

const deleteTemplate = async (template: any) => {
  // Implementation for delete
  console.log('Delete template:', template);
};

const saveTemplate = async () => {
  saving.value = true;
  try {
    const templateData = {
      ...templateForm.value,
      template_config: JSON.parse(templateConfigJson.value)
    };
    
    await store.createTemplate(templateData);
    
    toast.add({
      severity: 'success',
      summary: 'Template Saved',
      detail: 'Report template has been saved successfully',
      life: 3000
    });
    
    showCreateDialog.value = false;
    resetForm();
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Save Failed',
      detail: 'Failed to save template',
      life: 5000
    });
  } finally {
    saving.value = false;
  }
};

const resetForm = () => {
  templateForm.value = {
    template_name: '',
    report_type: '',
    template_config: {},
    is_default: false
  };
  templateConfigJson.value = '{}';
};

onMounted(() => {
  // Load templates would be implemented here
});
</script>

<style scoped>
.report-templates-view {
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.template-card {
  border: 1px solid var(--surface-border);
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.template-header h3 {
  margin: 0;
}

.template-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.template-form {
  display: grid;
  gap: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}
</style>