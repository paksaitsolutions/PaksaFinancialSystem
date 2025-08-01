<template>
  <div class="p-4">
    <Card>
      <template #title>Tax Settings</template>
      <template #content>
        <div class="grid">
          <div class="col-12">
            <Message severity="info" :closable="false">
              <p>Configure tax settings for payroll processing.</p>
              <p class="mt-2">This section allows you to manage tax brackets, exemptions, and other tax-related configurations.</p>
            </Message>
          </div>
          
          <div class="col-12 md:col-6">
            <Card class="h-full">
              <template #title>Tax Brackets</template>
              <template #content>
                <p class="text-color-secondary mb-4">Set up tax brackets for different income ranges.</p>
                <Button 
                  label="Configure Tax Brackets" 
                  icon="pi pi-cog"
                  class="p-button-outlined"
                  @click="openTaxBracketDialog"
                />
              </template>
            </Card>
          </div>

          <div class="col-12 md:col-6">
            <Card class="h-full">
              <template #title>Tax Exemptions</template>
              <template #content>
                <p class="text-color-secondary mb-4">Manage tax exemptions and deductions.</p>
                <Button 
                  label="Configure Exemptions" 
                  icon="pi pi-tag"
                  class="p-button-outlined"
                  @click="openExemptionsDialog"
                />
              </template>
            </Card>
          </div>

          <div class="col-12">
            <Card>
              <template #title>Tax Reports</template>
              <template #content>
                <div class="grid">
                  <div class="col-12 md:col-4">
                  <Button 
                    label="Generate Tax Report" 
                    icon="pi pi-file-pdf"
                    class="p-button-outlined p-button-help w-full"
                    @click="generateTaxReport"
                  />
                </div>
                <div class="col-12 md:col-4">
                  <Button 
                    label="View Tax History" 
                    icon="pi pi-history"
                    class="p-button-outlined p-button-info w-full"
                    @click="viewTaxHistory"
                  />
                </div>
                <div class="col-12 md:col-4">
                  <Button 
                    label="Export Tax Data" 
                    icon="pi pi-download"
                    class="p-button-outlined p-button-success w-full"
                    @click="exportTaxData"
                  />
                </div>
                </div> <!-- Close grid div -->
              </template>
            </Card>
          </div>
        </div>
      </template>
    </Card>

    <!-- Dialogs -->
    <Dialog 
      v-model:visible="showTaxBracketDialog" 
      header="Configure Tax Brackets" 
      :modal="true"
      :style="{ width: '50vw' }"
      :maximizable="true"
    >
      <p>Tax bracket configuration dialog content will appear here.</p>
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" @click="showTaxBracketDialog = false" class="p-button-text" />
        <Button label="Save" icon="pi pi-check" @click="saveTaxBrackets" autofocus />
      </template>
    </Dialog>

    <Dialog 
      v-model:visible="showExemptionsDialog" 
      header="Configure Tax Exemptions" 
      :modal="true"
      :style="{ width: '50vw' }"
    >
      <p>Tax exemptions configuration dialog content will appear here.</p>
      <template #footer>
        <Button label="Close" icon="pi pi-times" @click="showExemptionsDialog = false" class="p-button-text" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Message from 'primevue/message';
import { useToast } from 'primevue/usetoast';

const toast = useToast();

const showTaxBracketDialog = ref(false);
const showExemptionsDialog = ref(false);

const openTaxBracketDialog = () => {
  showTaxBracketDialog.value = true;
};

const openExemptionsDialog = () => {
  showExemptionsDialog.value = true;
};

const saveTaxBrackets = () => {
  showTaxBracketDialog.value = false;
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: 'Tax brackets have been saved',
    life: 3000
  });
};

const generateTaxReport = () => {
  toast.add({
    severity: 'info',
    summary: 'Info',
    detail: 'Generating tax report...',
    life: 3000
  });};

const viewTaxHistory = () => {
  toast.add({
    severity: 'info',
    summary: 'Info',
    detail: 'Loading tax history...',
    life: 3000
  });
};

const exportTaxData = () => {
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: 'Tax data exported successfully',
    life: 3000
  });
};
</script>

<style scoped>
.p-card {
  margin-bottom: 1rem;
}

:deep(.p-card-title) {
  font-size: 1.25rem;
  font-weight: 600;
}

:deep(.p-card-content) {
  padding: 1.25rem 1.5rem;
}
</style>
