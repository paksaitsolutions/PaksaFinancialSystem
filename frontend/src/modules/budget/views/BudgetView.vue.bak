<template>
  <div class="budget-view">
    <!-- Header Section -->
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="text-2xl font-bold">Budget Management</h1>
        <p class="text-gray-600">View and manage your organization's budgets</p>
      </div>
      <div class="flex gap-2">
        <Button 
          label="New Budget" 
          icon="pi pi-plus" 
          @click="openCreateDialog"
          class="p-button-primary"
        />
        <Button 
          label="Export" 
          icon="pi pi-download" 
          @click="showExportDialog = true" 
          :disabled="!budgets.length"
          :loading="isExporting"
          class="p-button-secondary"
        />
      </div>
    </div>

    <!-- Budget List -->
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <span>Budgets</span>
          <div class="flex gap-2">
            <Button 
              label="New Budget" 
              icon="pi pi-plus" 
              @click="openCreateDialog"
              class="p-button-text"
            />
            <Button 
              label="Export" 
              icon="pi pi-download" 
              @click="showExportDialog = true" 
              :disabled="!budgets.length"
              :loading="isExporting"
              class="p-button-text"
            />
          </div>
        </div>
      </template>
      
      <template #content>
        <!-- Filters -->
        <div class="grid mb-4">
          <div class="col-12 md:col-3">
            <span class="p-float-label">
              <InputText id="search" v-model="filters.search" class="w-full" />
              <label for="search">Search</label>
            </span>
          </div>
          <div class="col-12 md:col-3">
            <span class="p-float-label">
              <Dropdown 
                v-model="filters.status" 
                :options="budgetStatuses" 
                optionLabel="name" 
                optionValue="value" 
                class="w-full"
                showClear
              />
              <label>Status</label>
            </span>
          </div>
          <div class="col-12 md:col-3">
            <span class="p-float-label">
              <Dropdown 
                v-model="filters.type" 
                :options="budgetTypes" 
                optionLabel="name" 
                optionValue="value" 
                class="w-full"
                showClear
              />
              <label>Type</label>
            </span>
          </div>
          <div class="col-12 md:col-3 flex align-items-end">
            <Button 
              label="Clear" 
              icon="pi pi-filter-slash" 
              class="p-button-outlined w-full"
              @click="clearFilters"
            />
          </div>
        </div>

        <!-- Budgets Table -->
        <DataTable 
          :value="filteredBudgets" 
          :loading="loading" 
          :paginator="true" 
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20, 50]"
          v-model:selection="selectedBudgets"
          dataKey="id"
          responsiveLayout="scroll"
          class="p-datatable-sm"
        >
          <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
          
          <Column field="name" header="Name" :sortable="true">
            <template #body="{ data }">
              <a href="#" @click.prevent="openEditDialog(data)" class="text-primary">{{ data.name }}</a>
            </template>
          </Column>
          
          <Column field="amount" header="Amount" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.amount) }}
            </template>
          </Column>
          
          <Column field="type" header="Type" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.type" :severity="getBudgetTypeSeverity(data.type)" />
            </template>
          </Column>
          
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          
          <Column field="startDate" header="Start Date" :sortable="true">
            <template #body="{ data }">
              {{ formatDate(data.startDate) }}
            </template>
          </Column>
          
          <Column field="endDate" header="End Date" :sortable="true">
            <template #body="{ data }">
              {{ formatDate(data.endDate) }}
            </template>
          </Column>
          
          <Column headerStyle="width: 10rem; text-align: center" bodyStyle="text-align: center; overflow: visible">
            <template #body="{ data }">
              <Button 
                icon="pi pi-pencil" 
                class="p-button-rounded p-button-text p-button-sm" 
                @click="openEditDialog(data)"
                v-tooltip.top="'Edit'"
              />
              <Button 
                icon="pi pi-trash" 
                class="p-button-rounded p-button-text p-button-sm p-button-danger" 
                @click="confirmDelete(data.id)"
                v-tooltip.top="'Delete'"
              />
              <Button 
                v-if="data.status === 'PENDING_APPROVAL'"
                icon="pi pi-check" 
                class="p-button-rounded p-button-text p-button-sm p-button-success" 
                @click="openApprovalDialog(data)"
                v-tooltip.top="'Approve'"
              />
              <Button 
                v-if="data.status === 'PENDING_APPROVAL'"
                icon="pi pi-times" 
                class="p-button-rounded p-button-text p-button-sm p-button-warning" 
                @click="openRejectDialog(data)"
                v-tooltip.top="'Reject'"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Budget Form Dialog -->
    <Dialog 
      v-model:visible="dialog.visible" 
      :style="{width: '650px'}" 
      :header="dialog.mode === 'create' ? 'New Budget' : 'Edit Budget'"
      :modal="true"
      :closable="!dialog.loading" 
      :closeOnEscape="!dialog.loading"
    >
      <BudgetForm 
        v-if="dialog.visible"
        :budget="form"
        :loading="dialog.loading"
        @submit="handleSave"
        @cancel="dialog.visible = false"
      />
    </Dialog>

    <!-- Approval Dialog -->
    <Dialog 
      v-model:visible="approvalDialog.visible" 
      :style="{width: '450px'}" 
      header="Approve Budget" 
      :modal="true"
    >
      <div class="confirmation-content">
        <i class="pi pi-check-circle mr-3" style="font-size: 2rem" />
        <span>Are you sure you want to approve this budget?</span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="approvalDialog.visible = false" 
          :disabled="approvalDialog.loading"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-success" 
          @click="handleApproval" 
          :loading="approvalDialog.loading" 
        />
      </template>
    </Dialog>

    <!-- Reject Dialog -->
    <Dialog 
      v-model:visible="rejectDialog.visible" 
      :style="{width: '450px'}" 
      header="Reject Budget" 
      :modal="true"
    >
      <div class="field">
        <label for="rejectReason">Reason for rejection</label>
        <Textarea 
          id="rejectReason" 
          v-model="rejectDialog.reason" 
          :autoResize="true" 
          rows="3" 
          class="w-full"
          :class="{'p-invalid': rejectDialog.error}"
        />
        <small v-if="rejectDialog.error" class="p-error">{{ rejectDialog.error }}</small>
      </div>
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="rejectDialog.visible = false"
          :disabled="rejectDialog.loading"
        />
        <Button 
          label="Reject" 
          icon="pi pi-times" 
          class="p-button-danger" 
          @click="handleReject" 
          :loading="rejectDialog.loading"
        />
      </template>
    </Dialog>

    <!-- Export Dialog -->
    <ExportDialog 
      v-model:visible="showExportDialog"
      :formats="['pdf', 'excel', 'csv']"
      :loading="isExporting"
      @export="exportBudgets"
    />

    <!-- Delete Confirmation -->
    <ConfirmDialog />
  </div>
    <!-- Header Section -->
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="text-2xl font-bold">Budget Management</h1>
        <p class="text-gray-600">View and manage your organization's budgets</p>
      </div>
      <div class="flex gap-2">
        <Button 
          label="New Budget" 
          icon="pi pi-plus" 
          @click="openCreateDialog"
          class="p-button-primary"
        />
        <Button 
          label="Export" 
          icon="pi pi-download" 
          @click="showExportDialog = true" 
          :disabled="!budgets.length"
          :loading="isExporting"
          class="p-button-secondary"
        />
      </div>
    </div>

    <!-- Budget List -->
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <span>Budgets</span>
          <div class="flex gap-2">
            <Button 
              label="New Budget" 
              icon="pi pi-plus" 
              @click="openCreateDialog"
              class="p-button-text"
            />
            <Button 
              label="Export" 
              icon="pi pi-download" 
              @click="showExportDialog = true" 
              :disabled="!budgets.length"
              :loading="isExporting"
              class="p-button-text"
            />
          </div>
        </div>
      </template>
      
      <template #content>
        <!-- Filters -->
        <div class="grid mb-4">
          <div class="col-12 md:col-3">
            <span class="p-float-label">
              <InputText id="search" v-model="filters.search" class="w-full" />
              <label for="search">Search</label>
            </span>
          </div>
          <div class="col-12 md:col-3">
            <span class="p-float-label">
              <Dropdown 
                v-model="filters.status" 
                :options="budgetStatuses" 
                optionLabel="name" 
                optionValue="value" 
                class="w-full"
                showClear
              />
              <label>Status</label>
            </span>
          </div>
          <div class="col-12 md:col-3">
            <span class="p-float-label">
              <Dropdown 
                v-model="filters.type" 
                :options="budgetTypes" 
                optionLabel="name" 
                optionValue="value" 
                class="w-full"
                showClear
              />
              <label>Type</label>
            </span>
          </div>
          <div class="col-12 md:col-3 flex align-items-end">
            <Button 
              label="Clear" 
              icon="pi pi-filter-slash" 
              class="p-button-outlined w-full"
              @click="clearFilters"
            />
          </div>
        </div>

        <!-- Budgets Table -->
        <DataTable 
          :value="filteredBudgets" 
          :loading="loading" 
          :paginator="true" 
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20, 50]"
          :selection.sync="selectedBudgets"
          :filters="filters"
          dataKey="id"
          responsiveLayout="scroll"
          class="p-datatable-sm"
        >
          <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
          
          <Column field="name" header="Name" :sortable="true">
            <template #body="{ data }">
              <a href="#" @click="openEditDialog(data)" class="text-primary">{{ data.name }}</a>
            </template>
          </Column>
          
          <Column field="amount" header="Amount" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.amount) }}
            </template>
          </Column>
          
          <Column field="type" header="Type" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.type" :severity="getBudgetTypeSeverity(data.type)" />
            </template>
          </Column>
          
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          
          <Column field="startDate" header="Start Date" :sortable="true">
            <template #body="{ data }">
              {{ formatDate(data.startDate) }}
            </template>
          </Column>
          
          <Column field="endDate" header="End Date" :sortable="true">
            <template #body="{ data }">
              {{ formatDate(data.endDate) }}
            </template>
          </Column>
          
          <Column headerStyle="width: 10rem; text-align: center" bodyStyle="text-align: center; overflow: visible">
            <template #body="{ data }">
              <Button 
                icon="pi pi-pencil" 
                class="p-button-rounded p-button-text p-button-sm" 
                @click="openEditDialog(data)"
                v-tooltip.top="'Edit'"
              />
              <Button 
                icon="pi pi-trash" 
                class="p-button-rounded p-button-text p-button-sm p-button-danger" 
                @click="confirmDelete(data.id)"
                v-tooltip.top="'Delete'"
              />
              <Button 
                v-if="data.status === 'PENDING_APPROVAL'"
                icon="pi pi-check" 
                class="p-button-rounded p-button-text p-button-sm p-button-success" 
                @click="openApprovalDialog(data)"
                v-tooltip.top="'Approve'"
              />
              <Button 
                v-if="data.status === 'PENDING_APPROVAL'"
                icon="pi pi-times" 
                class="p-button-rounded p-button-text p-button-sm p-button-warning" 
                @click="openRejectDialog(data)"
                v-tooltip.top="'Reject'"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Budget Form Dialog -->
    <Dialog 
      v-model:visible="dialog" 
      :style="{width: '650px'}" 
      :header="form.id ? 'Edit Budget' : 'New Budget'" 
      :modal="true"
      :closable="!submitting" 
      :closeOnEscape="!submitting"
    >
      <BudgetForm 
        v-if="dialog"
        :budget="form"
        :loading="submitting"
        @submit="handleSave"
        @cancel="dialog = false"
      />
    </Dialog>

    <!-- Approval Dialog -->
    <Dialog 
      v-model:visible="approvalDialog.visible" 
      :style="{width: '450px'}" 
      header="Approve Budget" 
      :modal="true"
    >
      <div class="confirmation-content">
        <i class="pi pi-check-circle mr-3" style="font-size: 2rem" />
        <span>Are you sure you want to approve this budget?</span>
      </div>
      <template #footer>
        <Button label="No" icon="pi pi-times" class="p-button-text" @click="approvalDialog.visible = false" />
        <Button label="Yes" icon="pi pi-check" class="p-button-success" @click="handleApproval" :loading="approvalDialog.loading" />
      </template>
    </Dialog>

    <!-- Reject Dialog -->
    <Dialog 
      v-model:visible="rejectDialog.visible" 
      :style="{width: '450px'}" 
      header="Reject Budget" 
      :modal="true"
    >
      <div class="field">
        <label for="rejectReason">Reason for rejection</label>
        <Textarea 
          id="rejectReason" 
          v-model="rejectDialog.reason" 
          :autoResize="true" 
          rows="3" 
          class="w-full"
          :class="{'p-invalid': rejectDialog.error}"
        />
        <small v-if="rejectDialog.error" class="p-error">{{ rejectDialog.error }}</small>
      </div>
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="rejectDialog.visible = false" />
        <Button label="Reject" icon="pi pi-times" class="p-button-danger" @click="handleReject" :loading="rejectDialog.loading" />
      </template>
    </Dialog>

    <!-- Export Dialog -->
    <ExportDialog 
      v-model:visible="showExportDialog"
      :formats="['pdf', 'excel', 'csv']"
      :loading="isExporting"
      @export="exportBudgets"
    />

    <!-- Delete Confirmation -->
    <ConfirmDialog></ConfirmDialog>
  </div>
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="text-2xl font-bold">Budget Management</h1>
        <p class="text-gray-600">View and manage your organization's budgets</p>
      </div>
      <div class="flex gap-2">
        <Button 
          label="New Budget" 
          icon="pi pi-plus" 
          @click="openCreateDialog"
          class="p-button-primary"
        />
        <Button 
          label="Export" 
          icon="pi pi-download" 
          @click="showExportDialog = true" 
          :disabled="!budgets.length"
          :loading="isExporting"
          class="p-button-secondary"
        />
      </div>
    </div>
    <v-row>
      <!-- Budget List -->
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-row align="center">
              <v-col cols="8">
                <h2>Budgets</h2>
              </v-col>
              <v-col cols="4" class="text-right">
                <v-btn color="primary" @click="openCreateDialog" class="mr-2">
                  <v-icon left>mdi-plus</v-icon>
                  New Budget
                </v-btn>
                <v-btn color="secondary" @click="showExportDialog = true" :disabled="!budgets.length" :loading="isExporting">
                  <v-icon left>mdi-download</v-icon>
                  {{ isExporting ? 'Exporting...' : 'Export' }}
                </v-btn>
              </v-col>
            </v-row>
          </v-card-title>

          <v-card-text>
            <!-- Filters -->
            <v-row class="mb-4">
              <v-col cols="12" sm="3">
                <v-select
                  v-model="filters.status"
                  :items="Object.values(BudgetStatus)"
                  label="Status"
                  clearable
                ></v-select>
              </v-col>
              <v-col cols="12" sm="3">
                <v-select
                  v-model="filters.type"
                  :items="Object.values(BudgetType)"
                  label="Type"
                  clearable
                ></v-select>
              </v-col>
              <v-col cols="12" sm="3">
                <v-text-field
                  v-model="filters.startDate"
                  label="Start Date"
                  type="date"
                  clearable
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="3">
                <v-text-field
                  v-model="filters.endDate"
                  label="End Date"
                  type="date"
                  clearable
                ></v-text-field>
              </v-col>
            </v-row>

            <!-- Budget Table -->
            <v-data-table
              :headers="headers"
              :items="filteredBudgets"
              :loading="loading"
              :items-per-page="10"
              class="elevation-1"
              @click:row="(item) => selectBudget(item)"
            >
              <template v-slot:item.status="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  small
                >
                  {{ item.status }}
                </v-chip>
              </template>
              <template v-slot:item.actions="{ item }">
                <v-btn icon @click="openEditDialog(item)">
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <v-btn
                  v-if="item.status === BudgetStatus.DRAFT"
                  icon
                  @click="openApprovalDialog(item)"
                >
                  <v-icon>mdi-check</v-icon>
                </v-btn>
                <v-btn
                  v-if="item.status === BudgetStatus.DRAFT"
                  icon
                  @click="openRejectDialog(item)"
                >
                  <v-icon>mdi-close</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Create/Edit Dialog -->
    <v-dialog v-model="dialog" max-width="800">
      <v-card>
        <v-card-title>
          {{ selectedBudget ? 'Edit Budget' : 'Create Budget' }}
        </v-card-title>
        <v-card-text>
          <BudgetForm
            v-if="dialog"
            :budget="selectedBudget"
            @save="handleSave"
            @cancel="dialog = false"
          />
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Approval Dialog -->
    <v-dialog v-model="approvalDialog" max-width="500">
      <v-card>
        <v-card-title>Approve Budget</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="approvalNotes"
            label="Approval Notes (Optional)"
            rows="3"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="approvalDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="handleApproval">Approve</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Reject Dialog -->
    <v-dialog v-model="rejectDialog" max-width="500">
      <v-card>
        <v-card-title>Reject Budget</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="rejectNotes"
            label="Rejection Notes (Required)"
            rows="3"
            :rules="[v => !!v || 'Notes are required']"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="rejectDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="handleReject">Reject</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>

  <!-- Export Dialog -->
  <Dialog 
    v-model:visible="showExportDialog" 
    header="Export Budgets" 
    :modal="true"
    :style="{ width: '50vw' }"
    :closable="!isExporting"
    :closeOnEscape="!isExporting"
  >
    <div class="p-fluid">
      <div class="field">
        <label for="exportType">Export Format</label>
        <Dropdown
          v-model="exportFormat"
          :options="['PDF', 'Excel', 'CSV']"
          optionLabel=""
          placeholder="Select Format"
          class="w-full"
        />
      </div>
      <div class="field">
        <label for="exportScope">Export Scope</label>
        <div class="flex flex-column gap-2">
          <div class="flex align-items-center">
            <RadioButton 
              v-model="exportScope" 
              inputId="currentView" 
              name="exportScope" 
              value="current" 
              :disabled="isExporting"
            />
            <label for="currentView" class="ml-2">Current View</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              v-model="exportScope" 
              inputId="allData" 
              name="exportScope" 
              value="all"
              :disabled="isExporting"
            />
            <label for="allData" class="ml-2">All Data</label>
          </div>
        </div>
      </div>
    </div>
    <template #footer>
      <Button 
        label="Cancel" 
        icon="pi pi-times" 
        @click="showExportDialog = false" 
        class="p-button-text"
        :disabled="isExporting"
      />
      <Button 
        label="Export" 
        icon="pi pi-download" 
        @click="exportBudgets"
        :loading="isExporting"
        class="p-button-primary"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useBudgetStore } from '@/stores/budget';
import { BudgetStatus, BudgetType, type BudgetResponse } from '@/types/budget';
import Button from 'primevue/button';
import Card from 'primevue/card';
import Dialog from 'primevue/dialog';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import RadioButton from 'primevue/radiobutton';
import Tag from 'primevue/tag';
import InputNumber from 'primevue/inputnumber';
import Textarea from 'primevue/textarea';
import { format } from 'date-fns';

// Types
interface BudgetResponse {
  id: number;
  name: string;
  description: string;
  type: BudgetType;
  status: BudgetStatus;
  start_date: string;
  end_date: string;
  amount: number;
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
  department_id?: number;
  project_id?: number;
  approvals: BudgetApproval[];
}

interface BudgetForm {
  id?: number;
  name: string;
  description: string;
  type: BudgetType;
  status: BudgetStatus;
  start_date: string;
  end_date: string;
  amount: number;
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
  department_id?: number;
  project_id?: number;
}

interface BudgetRequest {
  id?: number;
  name: string;
  description: string;
  type: BudgetType;
  status: BudgetStatus;
  start_date: string;
  end_date: string;
  amount: number;
  department_id?: number;
  project_id?: number;
}

interface BudgetApproval {
  id: number;
  budget_id: number;
  user_id: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  notes?: string;
  created_at: string;
  updated_at: string;
}

// Router and Stores
const router = useRouter();
const budgetStore = useBudgetStore();
const toast = useToast();

// State
const dialog = ref(false);
const isExporting = ref(false);
const showExportDialog = ref(false);
const exportFormat = ref('PDF');
const exportScope = ref('current');
const approvalDialog = ref(false);
const rejectDialog = ref(false);
const selectedBudget = ref<BudgetResponse | null>(null);
const approvalNotes = ref('');
const rejectNotes = ref('');
const submitted = ref(false);

// Filters
const filters = ref({
  global: '',
  status: null as string | null,
  type: null as string | null
});

// Form Data
const form = ref<BudgetForm>({
  id: undefined,
  name: '',
  description: '',
  amount: 0,
  start_date: new Date().toISOString().split('T')[0],
  end_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  status: BudgetStatus.DRAFT,
  type: BudgetType.OPERATIONAL,
  created_at: '',
  updated_at: '',
  created_by: '',
  updated_by: ''
});

// Computed
const budgets = computed<BudgetResponse[]>(() => budgetStore.budgets);
const loading = computed<boolean>(() => budgetStore.loading);
const error = computed<string | null>(() => budgetStore.error);

const budgetStatuses = computed(() => [
  { label: 'Draft', value: BudgetStatus.DRAFT },
  { label: 'Submitted', value: BudgetStatus.SUBMITTED },
  { label: 'Approved', value: BudgetStatus.APPROVED },
  { label: 'Rejected', value: BudgetStatus.REJECTED },
  { label: 'Archived', value: BudgetStatus.ARCHIVED }
]);

const budgetTypes = computed(() => [
  { label: 'Operational', value: BudgetType.OPERATIONAL },
  { label: 'Capital', value: BudgetType.CAPITAL },
  { label: 'Project', value: BudgetType.PROJECT },
  { label: 'Departmental', value: BudgetType.DEPARTMENTAL }
]);

const filteredBudgets = computed<BudgetResponse[]>(() => {
  if (!budgets.value) return [];
  
  return budgets.value.filter((budget: BudgetResponse) => {
    const matchesSearch = !filters.value.global || 
      budget.name.toLowerCase().includes(filters.value.global.toLowerCase()) ||
      budget.description?.toLowerCase().includes(filters.value.global.toLowerCase());
      
    const matchesStatus = !filters.value.status || budget.status === filters.value.status;
    const matchesType = !filters.value.type || budget.type === filters.value.type;
    
    return matchesSearch && matchesStatus && matchesType;
  });
});

// Methods
const openCreateDialog = (): void => {
  form.value = {
    id: undefined,
    name: '',
    description: '',
    amount: 0,
    start_date: new Date().toISOString().split('T')[0],
    end_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    status: BudgetStatus.DRAFT,
    type: BudgetType.OPERATIONAL,
    created_at: '',
    updated_at: '',
    created_by: '',
    updated_by: ''
  };
  submitted.value = false;
  dialog.value = true;
};

const openEditDialog = (budget: BudgetResponse): void => {
  selectedBudget.value = { ...budget };
  form.value = { ...budget };
  submitted.value = false;
  dialog.value = true;
};

const openApprovalDialog = (budget: BudgetResponse): void => {
  selectedBudget.value = budget;
  approvalNotes.value = '';
  approvalDialog.value = true;
};

const openRejectDialog = (budget: BudgetResponse): void => {
  selectedBudget.value = budget;
  rejectNotes.value = '';
  rejectDialog.value = true;
};

const clearFilters = (): void => {
  filters.value = {
    global: '',
    status: null,
    type: null
  };
};

const getTypeSeverity = (type: string): string => {
  switch (type) {
    case BudgetType.OPERATIONAL: return 'info';
    case BudgetType.CAPITAL: return 'warning';
    case BudgetType.PROJECT: return 'success';
    case BudgetType.DEPARTMENTAL: return 'primary';
    default: return 'secondary';
  }
};

const saveBudget = async (): Promise<void> => {
  try {
    submitted.value = true;
    
    if (!form.value.name || !form.value.amount || !form.value.start_date || !form.value.end_date) {
      toast.add({ 
        severity: 'warn', 
        summary: 'Validation Error', 
        detail: 'Please fill in all required fields', 
        life: 3000 
      });
      return;
    }
    
    if (form.value.id) {
      await budgetStore.updateBudget(form.value.id, form.value as BudgetRequest);
      toast.add({ 
        severity: 'success', 
        summary: 'Success', 
        detail: 'Budget updated successfully', 
        life: 3000 
      });
    } else {
      await budgetStore.createBudget(form.value as BudgetRequest);
      toast.add({ 
        severity: 'success', 
        summary: 'Success', 
        detail: 'Budget created successfully', 
        life: 3000 
      });
    }
    
    dialog.value = false;
    resetForm();
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
    console.error('Error saving budget:', error);
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: `Failed to save budget: ${errorMessage}`, 
      life: 5000 
    });
  } finally {
    submitted.value = false;
  }
};

const deleteBudget = async (budget: BudgetResponse): Promise<void> => {
  if (!budget.id) {
    toast.add({ 
      severity: 'warn', 
      summary: 'Warning', 
      detail: 'Cannot delete budget: Invalid budget ID', 
      life: 3000 
    });
    return;
  }
  
  try {
    await budgetStore.deleteBudget(budget.id);
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'Budget deleted successfully', 
      life: 3000 
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
    console.error('Error deleting budget:', error);
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: `Failed to delete budget: ${errorMessage}`, 
      life: 5000 
    });
  }
};

const submitForApproval = async (budget: BudgetResponse): Promise<void> => {
  if (!budget.id) {
    toast.add({ 
      severity: 'warn', 
      summary: 'Warning', 
      detail: 'Cannot submit budget: Invalid budget ID', 
      life: 3000 
    });
    return;
  }
  
  try {
    await budgetStore.submitForApproval(budget.id);
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'Budget submitted for approval', 
      life: 3000 
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
    console.error('Error submitting budget for approval:', error);
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: `Failed to submit budget for approval: ${errorMessage}`, 
      life: 5000 
    });
  }
};

const approveBudget = async (): Promise<void> => {
  if (!selectedBudget.value?.id) {
    toast.add({ 
      severity: 'warn', 
      summary: 'Warning', 
      detail: 'Cannot approve budget: No budget selected', 
      life: 3000 
    });
    return;
  }
  
  try {
    await budgetStore.approveBudget(selectedBudget.value.id, approvalNotes.value);
    approvalDialog.value = false;
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'Budget approved successfully', 
      life: 3000 
    });
    approvalNotes.value = '';
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
    console.error('Error approving budget:', error);
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: `Failed to approve budget: ${errorMessage}`, 
      life: 5000 
    });
  }
};

const rejectBudget = async (): Promise<void> => {
  if (!selectedBudget.value?.id) {
    toast.add({ 
      severity: 'warn', 
      summary: 'Warning', 
      detail: 'Cannot reject budget: No budget selected', 
      life: 3000 
    });
    return;
  }
  
  if (!rejectNotes.value.trim()) {
    toast.add({ 
      severity: 'warn', 
      summary: 'Warning', 
      detail: 'Please provide a reason for rejection', 
      life: 3000 
    });
    return;
  }
  
  try {
    await budgetStore.rejectBudget(selectedBudget.value.id, rejectNotes.value);
    rejectDialog.value = false;
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'Budget rejected', 
      life: 3000 
    });
    rejectNotes.value = '';
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
    console.error('Error rejecting budget:', error);
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: `Failed to reject budget: ${errorMessage}`, 
      life: 5000 
    });
  }
};

const exportBudgets = async (): Promise<void> => {
  try {
    isExporting.value = true;
    const exportData = {
      format: exportFormat.value.toLowerCase(),
      scope: exportScope.value,
      filters: {
        status: budgetStore.filters?.status || undefined,
        type: budgetStore.filters?.type || undefined,
        startDate: budgetStore.filters?.startDate || undefined,
        endDate: budgetStore.filters?.endDate || undefined
      }
    };

    await budgetStore.exportBudgets(exportData);
    showExportDialog.value = false;
    
    toast.add({
      severity: 'success',
      summary: 'Export Successful',
      detail: `Budgets exported to ${exportFormat.value} successfully`,
      life: 3000
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
    console.error('Error exporting budgets:', error);
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: `Failed to export budgets: ${errorMessage}`,
      life: 5000
    });
  } finally {
    isExporting.value = false;
  }
};

const formatDate = (dateString: string): string => {
  if (!dateString) return '';
  return format(new Date(dateString), 'MMM dd, yyyy');
};

const rejectBudget = async (): Promise<void> => {
  if (!rejectNotes.value) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Please provide a reason for rejection',
      life: 5000
    });
    return;
  }
  
  if (!selectedBudget.value) {
    console.error('No budget selected for rejection');
    return;
  }
  
  try {
    await budgetStore.rejectBudget(selectedBudget.value.id, rejectNotes.value);
    rejectDialog.value = false;
    await budgetStore.fetchBudgets();
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Budget rejected successfully',
      life: 3000
    });
  } catch (error) {
    console.error('Error rejecting budget:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to reject budget',
      life: 5000
    });
  }
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD', // TODO: Make this dynamic based on user preferences
    minimumFractionDigits: 2
  }).format(value);
};

const getStatusSeverity = (status: string) => {
  switch (status) {
    case BudgetStatus.APPROVED: return 'success';
    case BudgetStatus.REJECTED: return 'danger';
    case BudgetStatus.SUBMITTED: return 'info';
    case BudgetStatus.ARCHIVED: return 'secondary';
    default: return 'warning';
  }
};

// Lifecycle hooks
onMounted(async () => {
  try {
    await budgetStore.fetchBudgets();
  } catch (error) {
    console.error('Error initializing budget view:', error);
    toast.add({
      severity: 'error',
      summary: 'Initialization Error',
      detail: 'Failed to load budget data',
      life: 5000
    });
  }
});
  switch (status) {
    case BudgetStatus.DRAFT:
      return 'blue'
    case BudgetStatus.APPROVED:
      return 'green'
    case BudgetStatus.REJECTED:
      return 'red'
    case BudgetStatus.ARCHIVED:
      return 'grey'
    default:
      return 'grey'
  }
}

// Fetch initial data
budgetStore.fetchBudgets()
</script>
