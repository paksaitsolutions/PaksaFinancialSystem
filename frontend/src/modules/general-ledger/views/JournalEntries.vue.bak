<template>
  <div class="grid">
    <div class="col-12">
      <!-- Header with Title and Actions -->
      <div class="flex flex-column md:flex-row md:justify-content-between md:align-items-center mb-4">
        <div class="mb-3 md:mb-0">
          <h1 class="text-3xl font-light mb-0">Journal Entries</h1>
          <p class="text-600 mt-2">Manage and review all journal entries</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <Button 
            v-if="walletAddress"
            :label="`${walletAddress.substring(0, 6)}...${walletAddress.substring(38)}`"
            icon="pi pi-wallet"
            class="p-button-outlined p-button-success"
            v-tooltip.top="'Connected wallet'"
          />
          <Button 
            v-else
            label="Connect Wallet"
            icon="pi pi-wallet"
            class="p-button-outlined"
            :loading="isConnecting"
            @click="connectWallet"
            v-tooltip.top="'Connect your MetaMask wallet'"
          />
          <Button 
            icon="pi pi-refresh" 
            class="p-button-text p-button-rounded p-button-outlined" 
            :loading="loading" 
            @click="fetchJournalEntries"
            v-tooltip.top="'Refresh data'"
          />
          <Button 
            icon="pi pi-file-export" 
            label="Export" 
            class="p-button-outlined"
            @click="showExportDialog = true"
            v-tooltip.top="'Export journal entries'"
          />
          <Button 
            icon="pi pi-plus" 
            label="New Journal Entry" 
            @click="openCreateModal"
            class="p-button-primary"
          />
        </div>
      </div>

      <!-- Filters Card -->
      <div class="card mb-4">
        <div class="flex justify-content-between align-items-center mb-3">
          <h5 class="m-0">Filters</h5>
          <div>
            <Button 
              label="Clear" 
              icon="pi pi-filter-slash" 
              class="p-button-text p-button-sm" 
              @click="clearFilters"
              :disabled="!hasActiveFilters"
            />
          </div>
        </div>
        
        <div class="grid">
          <div class="col-12 md:col-4 lg:col-3">
            <div class="field">
              <label for="dateFrom" class="block text-600 text-sm font-medium mb-2">From Date</label>
              <Calendar 
                id="dateFrom"
                v-model="filters.dateFrom" 
                dateFormat="yy-mm-dd" 
                showIcon
                :showButtonBar="true"
                :disabled="loading"
                class="w-full"
                @date-select="onFilterChange"
              />
            </div>
          </div>
          <div class="col-12 md:col-4 lg:col-3">
            <div class="field">
              <label for="dateTo" class="block text-600 text-sm font-medium mb-2">To Date</label>
              <Calendar 
                id="dateTo"
                v-model="filters.dateTo" 
                dateFormat="yy-mm-dd" 
                showIcon
                :showButtonBar="true"
                :disabled="loading"
                class="w-full"
                @date-select="onFilterChange"
              />
            </div>
          </div>
          <div class="col-12 md:col-4 lg:3">
            <div class="field">
              <label for="status" class="block text-600 text-sm font-medium mb-2">Status</label>
              <Dropdown
                id="status"
                v-model="filters.status"
                :options="statusOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Select Status"
                :showClear="true"
                :filter="true"
                class="w-full"
                @change="onFilterChange"
              >
                <template #value="slotProps">
                  <Tag 
                    v-if="slotProps.value" 
                    :value="getStatusLabel(slotProps.value)"
                    :severity="getStatusSeverity(slotProps.value)"
                    class="mr-2"
                  />
                  <span v-else>
                    {{ slotProps.placeholder }}
                  </span>
                </template>
                <template #option="slotProps">
                  <Tag 
                    :value="slotProps.option.label"
                    :severity="getStatusSeverity(slotProps.option.value)"
                    class="mr-2"
                  />
                </template>
              </Dropdown>
            </div>
          </div>
                v-model="filters.status"
                :options="statusOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Select Status"
                :showClear="true"
                :filter="true"
                class="w-full"
                @change="onFilterChange"
              >
                <template #value="slotProps">
                  <Tag 
                    v-if="slotProps.value" 
                    :value="getStatusLabel(slotProps.value)"
                    :severity="getStatusSeverity(slotProps.value)"
                    class="mr-2"
                  />
                  <span v-else>
                    {{ slotProps.placeholder }}
                  </span>
                </template>
                <template #option="slotProps">
                  <Tag 
                    :value="slotProps.option.label"
                    :severity="getStatusSeverity(slotProps.option.value)"
                    class="mr-2"
                  />
                </template>
              </Dropdown>
            </div>
          </div>
          <div class="col-12 md:col-4 lg:3">
            <div class="field">
              <label for="reference" class="block text-600 text-sm font-medium mb-2">Reference</label>
              <InputText 
                id="reference"
                v-model="filters.reference"
                placeholder="Search by reference"
                class="w-full"
                @keyup.enter="onFilterChange"
              />
            </div>
          </div>
                id="dateTo"
                v-model="filters.dateTo" 
                dateFormat="yy-mm-dd" 
                showIcon
                :showButtonBar="true"
                :disabled="loading"
              />
            </div>
          </div>
          <div class="p-col-12 p-md-3">
            <div class="field">
              <label for="statusFilter">Status</label>
              <Dropdown 
                id="statusFilter"
                v-model="filters.status" 
                :options="statusOptions" 
                optionLabel="label" 
                optionValue="value"
                :disabled="loading"
                placeholder="All Status"
              />
            </div>
          </div>
          <div class="p-col-12 p-md-3">
            <div class="field">
              <label for="search">Search</label>
              <span class="p-input-icon-left w-full">
                <i class="pi pi-search" />
                <InputText 
                  id="search"
                  v-model="filters.search" 
                  placeholder="Search by reference or description"
                  :disabled="loading"
                  class="w-full"
                />
              </span>
            </div>
          </div>
        </div>
      </div>
    

    <div class="col-12">
      <!-- Journal Entries Table -->
      <div class="card">
        <div v-if="loading" class="flex justify-content-center p-4">
          <ProgressSpinner style="width: 50px; height: 50px" strokeWidth="4" />
        </div>
        
        <div v-else>
          <!-- Table Toolbar -->
          <div class="flex flex-column md:flex-row justify-content-between align-items-center p-4 border-bottom-1 surface-border">
            <div class="text-xl font-semibold">Journal Entries</div>
            <div class="mt-2 md:mt-0">
              <span class="p-input-icon-left">
                <i class="pi pi-search" />
                <InputText 
                  v-model="filters.global" 
                  placeholder="Search..." 
                  class="p-inputtext-sm"
                  @input="onFilterChange"
                />
              </span>
            </div>
          </div>
          
          <!-- DataTable -->
          <DataTable 
            :value="filteredJournalEntries"
            :paginator="true"
            :rows="rowsPerPage"
            :rowsPerPageOptions="[10, 25, 50, 100]"
            :totalRecords="totalRecords"
            :loading="loading"
            :filters="filters"
            :scrollable="true"
            scrollHeight="flex"
            dataKey="id"
            filterDisplay="menu"
            paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
            currentPageReportTemplate="Showing {first} to {last} of {totalRecords} entries"
            @page="onPageChange"
            @sort="onSort"
            class="p-datatable-sm"
            :lazy="true"
          >
            <template #empty>
              <div class="text-center p-4">
                <i class="pi pi-inbox text-4xl text-400 mb-3" />
                <p class="text-600">No journal entries found</p>
              </div>
            </template>
            
            <Column field="entryNumber" header="Entry #" :sortable="true">
              <template #body="{ data }">
                <span class="font-medium text-primary cursor-pointer hover:underline" @click="viewEntry(data)">
                  {{ data.entryNumber }}
                </span>
              </template>
            </Column>
            
            <Column field="date" header="Date" :sortable="true" dataType="date">
              <template #body="{ data }">
                {{ formatDate(data.date) }}
              </template>
            </Column>
            
            <Column field="description" header="Description" :sortable="true" />
            
            <Column field="reference" header="Reference" :sortable="true" />
            
            <Column field="totalDebit" header="Debit" :sortable="true" dataType="numeric">
              <template #body="{ data }">
                {{ formatCurrency(data.totalDebit) }}
              </template>
            </Column>
            
            <Column field="totalCredit" header="Credit" :sortable="true" dataType="numeric">
              <template #body="{ data }">
                {{ formatCurrency(data.totalCredit) }}
              </template>
            </Column>
            
            <Column field="status" header="Status" :sortable="true">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
              <template #filter>
                <Dropdown 
                  v-model="filters.status" 
                  :options="statusOptions" 
                  optionLabel="label" 
                  optionValue="value"
                  placeholder="Select Status"
                  class="p-column-filter"
                  :showClear="true"
                  @change="onFilterChange"
                >
                  <template #option="slotProps">
                    <Tag :value="slotProps.option.label" :severity="getStatusSeverity(slotProps.option.value)" />
                  </template>
                </Dropdown>
              </template>
            </Column>
            
            <Column :exportable="false" style="min-width: 10rem">
              <template #body="{ data }">
                <div class="flex gap-2">
                  <Button 
                    icon="pi pi-eye" 
                    class="p-button-text p-button-sm p-button-rounded"
                    @click="viewEntry(data)"
                    v-tooltip.top="'View Details'"
                  />
                  <Button 
                    icon="pi pi-pencil" 
                    class="p-button-text p-button-sm p-button-rounded p-button-success"
                    @click="editEntry(data)"
                    :disabled="data.status === 'posted'"
                    v-tooltip.top="data.status === 'posted' ? 'Posted entries cannot be edited' : 'Edit'"
                  />
                  <Button 
                    icon="pi pi-check" 
                    class="p-button-text p-button-sm p-button-rounded p-button-info"
                    @click="postEntry(data)"
                    :disabled="data.status === 'posted'"
                    v-tooltip.top="data.status === 'posted' ? 'Already posted' : 'Post Entry'"
                  />
                  <Button 
                    icon="pi pi-trash" 
                    class="p-button-text p-button-sm p-button-rounded p-button-danger"
                    @click="confirmDeleteEntry(data)"
                    :disabled="data.status === 'posted'"
                    v-tooltip.top="data.status === 'posted' ? 'Posted entries cannot be deleted' : 'Delete'"
                  />
                </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </div> 
              v-model="filters.dateFrom" 
              dateFormat="yy-mm-dd" 
              showIcon
              :showButtonBar="true"
            />
          </div>
          <div class="field col-12 md:col-3">
            <label for="dateTo">To Date</label>
            <Calendar 
              id="dateTo" 
              v-model="filters.dateTo" 
              dateFormat="yy-mm-dd" 
              showIcon
              :showButtonBar="true"
            />
          </div>
          <div class="field col-12 md:col-3">
            <label for="status">Status</label>
            <Dropdown 
              id="status"
              v-model="filters.status" 
              :options="statusOptions" 
              optionLabel="label" 
              optionValue="value"
              placeholder="All Status"
            />
          </div>
          <div class="field col-12 md:col-3 flex align-items-end">
            <Button 
              label="Apply Filters" 
              icon="pi pi-filter" 
              class="p-button-outlined w-full"
              @click="applyFilters"
            />
          </div>
        </div>
      

      <!-- Journal Entries Table -->
      <div class="card">
        <div class="flex justify-content-between align-items-center p-4 border-bottom-1 surface-border">
          <h2 class="text-xl m-0">Journal Entries</h2>
          <div class="flex align-items-center gap-2">
            <Button 
              icon="pi pi-refresh" 
              class="p-button-text" 
              :loading="loading" 
              @click="fetchJournalEntries"
              v-tooltip.top="'Refresh'"/>
            <Button 
              icon="pi pi-download" 
              class="p-button-text" 
              @click="showExportDialog = true"
              :disabled="journalEntries.length === 0"
              v-tooltip.top="'Export to Excel'"/>
          </div>
        </div>
        
        <DataTable 
          :value="filteredJournalEntries"
          :paginator="true" 
          :rows="10"
          :loading="loading"
          :rowHover="true"
          :globalFilterFields="['entryNumber', 'description', 'reference']"
          responsiveLayout="scroll"
          stripedRows
          :scrollable="true"
          scrollHeight="flex"
          columnResizeMode="expand"
          
          class="p-datatable-sm"
        
        >
          <template #empty>
            <div class="text-center p-4">
              <i class="pi pi-search" style="font-size: 2rem; color: var(--text-color-secondary)"></i>
              <p class="text-color-secondary">No journal entries found</p>
            </div>
          </template>
          
          <Column field="entryNumber" header="Entry #" :sortable="true">
            <template #body="{ data }">
              <span class="font-medium">{{ data.entryNumber }}</span>
            </template>
          </Column>
          
          <Column field="date" header="Date" :sortable="true">
            <template #body="{ data }">
              {{ formatDate(data.date) }}
            </template>
          </Column>
          
          <Column field="description" header="Description" :sortable="true" style="min-width: 200px" />
          
          <Column field="reference" header="Reference" :sortable="true" />
          
          <Column field="totalDebit" header="Debit" :sortable="true">
            <template #body="{ data }">
              <span class="font-medium" :class="{ 'text-red-500': data.totalDebit > 0 }">
                {{ formatCurrency(data.totalDebit) }}
              </span>
            </template>
          </Column>
          
          <Column field="totalCredit" header="Credit" :sortable="true">
            <template #body="{ data }">
              <span class="font-medium" :class="{ 'text-green-500': data.totalCredit > 0 }">
                {{ formatCurrency(data.totalCredit) }}
              </span>
            </template>
          </Column>
          
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag 
                :value="data.status" 
                :severity="getStatusSeverity(data.status)"
                class="capitalize"
              />
            </template>
          </Column>
          
          <Column header="Actions" :exportable="false" style="min-width: 8rem">
            <template #body="{ data }">
              <div class="flex gap-1">
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-text p-button-sm p-button-rounded" 
                  @click="editEntry(data)"
                  v-tooltip.top="'Edit'"
                />
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-text p-button-sm p-button-rounded" 
                  @click="viewEntry(data)"
                  v-tooltip.top="'View'"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-sm p-button-rounded p-button-danger" 
                  @click="confirmDeleteEntry(data)"
                  v-tooltip.top="'Delete'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    

    <!-- Create/Edit Dialog -->
    <Dialog 
      v-model:visible="showCreateModal" 
      :style="{ width: 'min(95vw, 1000px)' }" 
      :header="editingEntry ? 'Edit Journal Entry' : 'Create New Journal Entry'"
      :modal="true"
      :closable="!saving"
      :closeOnEscape="!saving"
      class="p-fluid"
      :breakpoints="{ '960px': '75vw', '641px': '90vw' }"
    >
      <form @submit.prevent="saveEntry" class="p-fluid">
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="entryDate" class="font-medium block mb-2">
                Date <span class="text-red-500">*</span>
              </label>
              <Calendar 
                id="entryDate"
                v-model="entryForm.date"
                dateFormat="yy-mm-dd"
                :showIcon="true"
                :disabled="saving"
                :class="{ 'p-invalid': v$.date.$error }"
                class="w-full"
              />
              <small v-if="v$.date.$error" class="p-error">
                {{ v$.date.$errors[0].$message }}
              </small>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="reference" class="font-medium block mb-2">Reference</label>
              <InputText 
                id="reference"
                v-model="entryForm.reference"
                :disabled="saving"
                placeholder="Reference number"
                class="w-full"
              />
            </div>
          </div>
          
          <div class="col-12">
            <div class="field">
              <label for="description" class="font-medium block mb-2">
                Description <span class="text-red-500">*</span>
              </label>
              <Textarea 
                id="description"
                v-model="entryForm.description"
                :disabled="saving"
                :autoResize="true"
                rows="2"
                :class="{ 'p-invalid': v$.description.$error }"
                class="w-full"
              />
              <small v-if="v$.description.$error" class="p-error">
                {{ v$.description.$errors[0].$message }}
              </small>
            </div>
          </div>
        </div>
        
        <div class="mt-5">
          <div class="flex justify-content-between align-items-center mb-3">
            <h4 class="m-0">Journal Lines</h4>
            <Button 
              type="button" 
              icon="pi pi-plus" 
              label="Add Line" 
              class="p-button-sm"
              @click="addLine"
              :disabled="saving"
            />
          </div>
          
          <div class="border-1 border-300 border-round">
            <DataTable 
              :value="entryForm.lines" 
              :scrollable="true" 
              scrollHeight="300px"
              :loading="saving"
              class="p-datatable-sm"
              :rowHover="true"
              :removableSort="true"
              :paginator="entryForm.lines.length > 5"
              :rows="5"
              :rowsPerPageOptions="[5, 10, 20]"
            >
              <Column field="accountName" header="Account" style="min-width: 200px">
                <template #body="{ data, index }">
                  <AutoComplete 
                    v-model="data.accountName"
                    :suggestions="accountSuggestions[data.id] || []"
                    @complete="searchAccounts($event, data)"
                    field="name"
                    placeholder="Search account..."
                    :dropdown="true"
                    :loading="accountLoading[data.id]"
                    @item-select="onAccountSelect($event, data)"
                    class="w-full"
                    :class="{ 'p-invalid': v$.lines.$each.$response.$data[index].accountId.$error }"
                  >
                    <template #item="slotProps">
                      <div class="flex align-items-center">
                        <div>
                          <div class="font-medium">{{ slotProps.item.code }}</div>
                          <div class="text-sm text-600">{{ slotProps.item.name }}</div>
                        </div>
                      </div>
                    </template>
                  </AutoComplete>
                  <small v-if="v$.lines.$each.$response.$data[index].accountId.$error" class="p-error">
                    {{ v$.lines.$each.$response.$data[index].accountId.$errors[0].$message }}
                  </small>
                </template>
              </Column>
              
              <Column field="description" header="Description" style="min-width: 200px">
                <template #body="{ data, index }">
                  <InputText 
                    v-model="data.description" 
                    class="w-full" 
                    :disabled="saving"
                    :class="{ 'p-invalid': v$.lines.$each.$response.$data[index].description.$error }"
                  />
                  <small v-if="v$.lines.$each.$response.$data[index].description.$error" class="p-error">
                    {{ v$.lines.$each.$response.$data[index].description.$errors[0].$message }}
                  </small>
                </template>
              </Column>
              
              <Column field="debit" header="Debit" style="width: 150px">
                <template #body="{ data, index }">
                  <InputNumber 
                    v-model="data.debit" 
                    mode="currency" 
                    currency="USD" 
                    locale="en-US"
                    class="w-full"
                    :minFractionDigits="2"
                    :maxFractionDigits="2"
                    :disabled="saving"
                    @input="updateCreditDebit(index, 'debit')"
                    :class="{ 'p-invalid': v$.lines.$each.$response.$data[index].debit.$error }"
                  />
                  <small v-if="v$.lines.$each.$response.$data[index].debit.$error" class="p-error">
                    {{ v$.lines.$each.$response.$data[index].debit.$errors[0].$message }}
                  </small>
                </template>
              </Column>
              
              <Column field="credit" header="Credit" style="width: 150px">
                <template #body="{ data, index }">
                  <InputNumber 
                    v-model="data.credit" 
                    mode="currency" 
                    currency="USD" 
                    locale="en-US"
                    class="w-full"
                    :minFractionDigits="2"
                    :maxFractionDigits="2"
                    :disabled="saving"
                    @input="updateCreditDebit(index, 'credit')"
                    :class="{ 'p-invalid': v$.lines.$each.$response.$data[index].credit.$error }"
                  />
                  <small v-if="v$.lines.$each.$response.$data[index].credit.$error" class="p-error">
                    {{ v$.lines.$each.$response.$data[index].credit.$errors[0].$message }}
                  </small>
                </template>
              </Column>
              
              <Column header="" style="width: 3.5rem">
                <template #body="{ index }">
                  <Button 
                    icon="pi pi-trash" 
                    class="p-button-text p-button-danger p-button-sm"
                    @click="removeLine(index)"
                    :disabled="saving || entryForm.lines.length <= 1"
                    v-tooltip.top="entryForm.lines.length <= 1 ? 'At least one line is required' : 'Remove line'"
                  />
                </template>
              </Column>
              
              <template #footer>
                <div class="grid w-full">
                  <div class="col-6 text-right font-bold">Total Debit:</div>
                  <div class="col-6 text-right font-bold">{{ formatCurrency(totalDebit) }}</div>
                  <div class="col-6 text-right font-bold">Total Credit:</div>
                  <div class="col-6 text-right font-bold">{{ formatCurrency(totalCredit) }}</div>
                  <div class="col-6 text-right font-bold">Difference:</div>
                  <div class="col-6 text-right font-bold" :class="{ 'text-red-500': !isBalanced }">
                    {{ formatCurrency(Math.abs(totalDebit - totalCredit)) }}
                    <span v-if="!isBalanced"> (Out of Balance)</span>
                  </div>
                </div>
              </template>
            </DataTable>
          </div>
        </div>
        
        <template #footer>
          <div class="flex justify-content-between w-full">
            <Button 
              label="Cancel" 
              icon="pi pi-times" 
              class="p-button-text"
              @click="closeModal"
              :disabled="saving"
            />
            <div class="flex gap-2">
              <Button 
                v-if="editingEntry"
                label="Delete" 
                icon="pi pi-trash" 
                class="p-button-danger"
                @click="confirmDeleteEntry(editingEntry)"
                :disabled="saving || (editingEntry && editingEntry.status === 'posted')"
                v-tooltip.top="editingEntry && editingEntry.status === 'posted' ? 'Posted entries cannot be deleted' : ''"
              />
              <Button 
                :label="editingEntry ? 'Update' : 'Save'" 
                icon="pi pi-check" 
                class="p-button-primary"
                type="submit"
                :loading="saving"
                :disabled="!isFormValid || !isBalanced"
              />
            </div>
          </div>
        </template>
      </form>
            
            <div class="col-12 mt-3" v-if="Math.abs(totalDebit - totalCredit) > 0.01">
              <Message severity="error">
                Debit and Credit totals must be equal. Current difference: {{ formatCurrency(Math.abs(totalDebit - totalCredit)) }}
              </Message>
            </div>
          
       
        
        <template #footer>
          <Button 
            type="button" 
            label="Cancel" 
            icon="pi pi-times" 
            class="p-button-text"
            @click="closeModal"
            :disabled="submitting"
          />
          <Button 
            type="submit" 
            :label="editingEntry ? 'Update Entry' : 'Create Entry'" 
            icon="pi pi-check" 
            class="p-button-primary"
            :loading="submitting"
            :disabled="!isFormValid || submitting"
          />
        </template>
     
    </Dialog>

    <!-- Export Dialog -->
    <ExportDialog
      v-model:visible="showExportDialog"
      title="Export Journal Entries"
      :file-name="exportFileName"
      :columns="exportColumns"
      :data="journalEntries"
      :meta="{
        title: 'Journal Entries Report',
        description: 'List of all journal entries with details',
        generatedOn: new Date().toLocaleString(),
        generatedBy: 'System',
        includeSummary: true,
        filters: {
          'Date Range': filters.dateFrom && filters.dateTo 
            ? `${filters.dateFrom} to ${filters.dateTo}` 
            : 'All dates',
          'Status': filters.status || 'All statuses'
        }
</template>

<script setup lang="ts">
// Import only what's needed
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { required } from '@vuelidate/validators'
import { useVuelidate } from '@vuelidate/core'
import { format, parseISO } from 'date-fns'

// Types
interface Account {
  id: number
  code: string
  name: string
  type: string
  balance: number
}

interface JournalLine {
  id?: number
  accountId: number | null
  accountCode?: string
  accountName: string
  description: string
  debit: number
  credit: number
}

interface JournalEntry {
  id?: number
  entryNumber: string
  date: string
  reference: string
  description: string
  status: 'draft' | 'posted' | 'reversed' | 'void'
  totalDebit: number
  totalCredit: number
  lines: JournalLine[]
  createdAt?: string
  updatedAt?: string
  createdBy?: string
  updatedBy?: string
}

interface FilterValues {
  global: string | null
  dateFrom: string | null
  dateTo: string | null
  status: string | null
  reference: string | null
}

interface StatusOption {
  label: string
  value: string
}

// PrimeVue and Vue Composition API setup
const toast = useToast()
const confirm = useConfirm()

// UI State
const loading = ref(false)
const submitting = ref(false)
const showCreateModal = ref(false)
const editingEntry = ref<JournalEntry | null>(null)

// Status options for filtering
type JournalStatus = 'draft' | 'posted' | 'reversed' | 'void'

const statusOptions = [
  { label: 'All Statuses', value: '' },
  { label: 'Draft', value: 'draft' as const },
  { label: 'Posted', value: 'posted' as const },
  { label: 'Reversed', value: 'reversed' as const },
  { label: 'Void', value: 'void' as const }
] as const

// Data State
const journalEntries = ref<JournalEntry[]>([])
const accounts = ref<Account[]>([])
const totalRecords = ref(0)

// Pagination and Sorting
const rowsPerPage = ref(10)
const first = ref(0)
const sortField = ref('date')
const sortOrder = ref(-1) // -1 for descending, 1 for ascending

// Filters
const filters = reactive({
  global: null as string | null,
  dateFrom: null as string | null,
  dateTo: null as string | null,
  status: null as string | null,
  reference: null as string | null
})

// Form data with reactive state
interface JournalFormData {
  id?: number
  entryNumber: string
  date: string
  reference: string
  description: string
  status: JournalStatus
  totalDebit: number
  totalCredit: number
  lines: JournalLine[]
}

const entryForm = reactive<JournalFormData>({
  id: undefined,
  entryNumber: '',
  date: new Date().toISOString().split('T')[0],
  reference: '',
  description: '',
  status: 'draft',
  totalDebit: 0,
  totalCredit: 0,
  lines: [
    {
      id: undefined,
      accountId: null,
      accountName: '',
      accountCode: '',
      description: '',
      debit: 0,
      credit: 0
    }
  ]
})

// Form validation rules
const rules = {
  entryNumber: { required },
  date: { required },
  reference: { required },
  status: { required },
  lines: {
    $each: {
      accountId: { required },
      description: { required },
      debit: { required },
      credit: { required }
    }
  }
}

const v$ = useVuelidate(rules, entryForm, { $autoDirty: true })

// Computed properties
const totalDebit = computed(() => {
  return entryForm.lines.reduce((sum, line) => sum + (Number(line.debit) || 0), 0)
})

const totalCredit = computed(() => {
  return entryForm.lines.reduce((sum, line) => sum + (Number(line.credit) || 0), 0)
})

const isFormValid = computed(() => {
  return (
    entryForm.date &&
    entryForm.reference &&
    entryForm.lines.length > 0 &&
    entryForm.lines.every(line => 
      line.accountId !== null && 
      (Number(line.debit) > 0 || Number(line.credit) > 0) &&
      (Number(line.debit) === 0 || Number(line.credit) === 0)
    ) && Math.abs(totalDebit.value - totalCredit.value) < 0.01
  )
})

// Status helpers
const getStatusSeverity = (status: JournalStatus) => {
  switch (status) {
    case 'draft': return 'info'
    case 'posted': return 'success'
    case 'reversed': return 'warning'
    case 'void': return 'danger'
    default: return 'secondary'
  }
}

const getStatusLabel = (status: JournalStatus) => {
  const statusLabels: Record<JournalStatus, string> = {
    draft: 'Draft',
    posted: 'Posted',
    reversed: 'Reversed',
    void: 'Void'
  }
  return statusLabels[status] || status
}

// Utility functions
const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

// Filtering and pagination - implemented in template but not used in script
// Keeping the functions for future implementation
const clearFilters = () => {
  // Reset all filters
  filters.value = {}
}

const onFilterChange = (e: any) => {
  // Handle filter changes
  filters.value = { ...filters.value, ...e.filters }
}

const onPageChange = (e: any) => {
  // Handle pagination
  // pagination.value = { ...pagination.value, ...e }
}

const onSort = (e: any) => {
  // Handle sorting
  // sorting.value = { ...sorting.value, ...e }
}

// CRUD Operations
const fetchJournalEntries = async () => {
  try {
    loading.value = true
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Mock data - replace with actual API call
    journalEntries.value = [
      {
        id: 1,
        entryNumber: 'JE-2023-001',
        date: new Date().toISOString(),
        reference: 'INV-001',
        description: 'Sample journal entry',
        status: 'draft',
        lines: [
          { id: 1, accountId: 1, accountCode: '1000', accountName: 'Cash', description: 'Initial deposit', debit: 1000, credit: 0 },
          { id: 2, accountId: 2, accountCode: '4000', accountName: 'Revenue', description: 'Initial deposit', debit: 0, credit: 1000 }
        ],
        totalDebit: 1000,
        totalCredit: 1000,
        createdAt: new Date().toISOString(),
        createdBy: 'System'
      }
    ]
    totalRecords.value = journalEntries.value.length
  } catch (error) {
    console.error('Error fetching journal entries:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load journal entries',
      life: 5000
    })
  } finally {
    loading.value = false
  }
}

const viewEntry = (entry: JournalEntry) => {
  // TODO: Implement view entry details
  console.log('View entry:', entry)
}

const editEntry = (entry: JournalEntry) => {
  editingEntry.value = { ...entry }
  Object.assign(entryForm, {
    date: entry.date,
    description: entry.description,
    reference: entry.reference,
    lines: entry.lines.map(line => ({
      ...line,
      id: line.id || Date.now() + Math.random()
    }))
  })
  showCreateModal.value = true
}

const confirmDeleteEntry = (entry: JournalEntry) => {
  confirm.require({
    message: 'Are you sure you want to delete this journal entry? This action cannot be undone.',
    header: 'Confirm Deletion',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: () => deleteEntry(entry)
  })
}

const deleteEntry = async (entry: JournalEntry) => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 500))
  
  journalEntries.value = journalEntries.value.filter(e => e.id !== entry.id)
  
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: 'Journal entry deleted successfully',
    life: 3000
  })
}

const postEntry = async (entry: JournalEntry) => {
  if (!entry.id) {
    console.error('Cannot post entry without an ID')
    return
  }
  
  try {
    loading.value = true
    // In a real app, this would be an API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const index = journalEntries.value.findIndex(e => e.id === entry.id)
    if (index !== -1) {
      journalEntries.value[index].status = 'posted'  // Use lowercase to match type
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Journal entry posted successfully',
        life: 3000
      })
    }
  } catch (error) {
    console.error('Error posting journal entry:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to post journal entry',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

const updateCreditDebit = (index: number, field: 'debit' | 'credit'): void => {
  const line = entryForm.lines[index]
  if (!line) return
  
  if (field === 'debit' && Number(line.debit) > 0) {
    line.credit = 0
  } else if (field === 'credit' && Number(line.credit) > 0) {
    line.debit = 0
  }
  
  // Ensure only numbers are entered
  if (field === 'debit') {
    line.debit = Number(line.debit) || 0
  } else {
    line.credit = Number(line.credit) || 0
  }
}

const handleAccountSelect = (index: number, accountId: number | null): void => {
  if (accountId === null) return
  
  const line = entryForm.lines[index]
  if (!line) return
  
  // In a real app, you would fetch the account details by ID
  const account = accounts.value.find(a => a.id === accountId)
  if (account) {
    line.accountName = account.name
    line.accountCode = account.code
  }
}

const saveEntry = async (): Promise<void> => {
  const isValid = await v$.value.$validate()
  
  if (!isValid || !isFormValid.value) {
    toast.add({
      severity: 'error',
      summary: 'Validation Error',
      detail: 'Please fill in all required fields and ensure debits equal credits',
      life: 5000
    })
    return
  }

  try {
    submitting.value = true
    const entryData = {
      ...entryForm,
      totalDebit: totalDebit.value,
      totalCredit: totalCredit.value
    }
    
    // TODO: Implement save API call
    // const response = await journalEntryService.save(entryData)
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Journal entry saved successfully',
      life: 3000
    })
    
    closeModal()
    await fetchJournalEntries()
  } catch (error) {
    console.error('Error saving journal entry:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save journal entry',
      life: 3000
    })
  } finally {
    submitting.value = false
  }
}

const addLine = () => {
  const newLine: JournalLine = {
    id: undefined,
    accountId: null,
    accountName: '',
    accountCode: '',
    description: '',
    debit: 0,
    credit: 0
  }
  entryForm.lines.push(newLine)
}

const removeLine = (index: number) => {
  if (entryForm.lines.length > 2) {
    entryForm.lines.splice(index, 1)
    // Update totals after removal
    const totals = entryForm.lines.reduce(
      (acc, curr) => {
        acc.debit += curr.debit || 0
        acc.credit += curr.credit || 0
        return acc
      },
      { debit: 0, credit: 0 }
    )
    
    entryForm.totalDebit = totals.debit
    entryForm.totalCredit = totals.credit
  } else {
    toast.add({
      severity: 'warn',
      summary: 'Warning',
      detail: 'At least two lines are required',
      life: 3000
    })
  }
}

const resetForm = () => {
  entryForm.id = undefined
  entryForm.entryNumber = ''
  entryForm.date = new Date().toISOString().split('T')[0]
  entryForm.reference = ''
  entryForm.description = ''
  entryForm.status = 'draft'
  entryForm.lines = [
    { 
      id: undefined,
      accountId: null, 
      accountName: '', 
      accountCode: undefined,
      description: '', 
      debit: 0, 
      credit: 0 
    },
    { 
      id: undefined,
      accountId: null, 
      accountName: '', 
      accountCode: undefined,
      description: '', 
      debit: 0, 
      credit: 0 
    }
  ]
}

const closeModal = () => {
  if (!submitting.value) {
    showCreateModal.value = false
    resetForm()
  }
}

// Lifecycle hooks
onMounted(async () => {
  await fetchJournalEntries()
  
  // Mock accounts for development
  accounts.value = [
    { id: 1, code: '1000', name: 'Cash', type: 'asset', balance: 0 },
    { id: 2, code: '2000', name: 'Accounts Payable', type: 'liability', balance: 0 },
    { id: 3, code: '3000', name: 'Equity', type: 'equity', balance: 0 },
    { id: 4, code: '4000', name: 'Revenue', type: 'revenue', balance: 0 },
    { id: 5, code: '5000', name: 'Expenses', type: 'expense', balance: 0 }
  ]
})
</script>

<style scoped>
.journal-entries {
  min-height: 100vh;
  background: #f5f7fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e0e6ed;
  padding: 20px 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.header-content p {
  color: #718096;
  margin: 5px 0 0 0;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #1976D2;
  color: white;
}

.btn-secondary {
  background: #e2e8f0;
  color: #4a5568;
}

.btn-outline {
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #4a5568;
}

.filters-section {
  margin: 20px 0;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  align-items: end;
}

.filter-input {
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
}

.table-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.table-header h3 {
  margin: 0;
  color: #2d3748;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f7fafc;
}

.data-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #4a5568;
}

.amount {
  text-align: right;
  font-weight: 500;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.posted {
  background: #c6f6d5;
  color: #22543d;
}

.status-badge.draft {
  background: #fed7d7;
  color: #742a2a;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.btn-icon:hover {
  background: #f7fafc;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.entry-form {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #4a5568;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
}

.journal-lines {
  margin: 30px 0;
}

.journal-lines h4 {
  margin-bottom: 15px;
  color: #2d3748;
}

.journal-line {
  margin-bottom: 15px;
}

.line-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto;
  gap: 10px;
  align-items: center;
}

.btn-remove {
  background: #fed7d7;
  color: #742a2a;
  border: none;
  border-radius: 4px;
  width: 30px;
  height: 30px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 30px;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .line-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}
</style>