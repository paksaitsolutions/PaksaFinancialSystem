<template>
  <div class="financial-statement-templates">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2>Financial Statement Templates</h2>
      <div>
        <Button 
          label="New Template" 
          icon="pi pi-plus" 
          @click="showTemplateDialog = true"
          class="p-button-success"
        />
      </div>
    </div>

    <!-- Template List -->
    <DataTable 
      :value="templates" 
      :loading="loading"
      :paginator="true" 
      :rows="10"
      :rowsPerPageOptions="[10, 20, 50]"
      :totalRecords="totalRecords"
      :lazy="true"
      @page="onPage"
      @sort="onSort"
      sortMode="multiple"
      :sortField="sortField"
      :sortOrder="sortOrder"
      :filters="filters"
      filterDisplay="menu"
      :globalFilterFields="['name', 'statement_type', 'is_default']"
    >
      <Column field="name" header="Name" :sortable="true" filter>
        <template #body="{ data }">
          <span class="font-medium">{{ data.name }}</span>
          <span v-if="data.is_default" class="ml-2 p-tag p-tag-rounded p-tag-success">
            Default
          </span>
        </template>
      </Column>
      
      <Column field="statement_type" header="Type" :sortable="true" filter>
        <template #body="{ data }">
          {{ formatStatementType(data.statement_type) }}
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <Dropdown 
            v-model="filterModel.value" 
            :options="statementTypeOptions" 
            optionLabel="label"
            optionValue="value"
            placeholder="Select Type"
            @change="filterCallback()"
            class="p-column-filter"
            :showClear="true"
          />
        </template>
      </Column>
      
      <Column field="description" header="Description" />
      
      <Column field="updated_at" header="Last Updated" :sortable="true">
        <template #body="{ data }">
          {{ formatDate(data.updated_at) }}
        </template>
      </Column>
      
      <Column header="Actions" :exportable="false" style="min-width: 12rem">
        <template #body="{ data }">
          <div class="flex gap-2">
            <Button 
              icon="pi pi-eye" 
              class="p-button-rounded p-button-text p-button-sm"
              @click="previewTemplate(data)"
              v-tooltip.top="'Preview'"
            />
            <Button 
              icon="pi pi-pencil" 
              class="p-button-rounded p-button-text p-button-sm"
              @click="editTemplate(data)"
              v-tooltip.top="'Edit'"
            />
            <Button 
              icon="pi pi-clone" 
              class="p-button-rounded p-button-text p-button-sm p-button-warning"
              @click="cloneTemplate(data)"
              v-tooltip.top="'Clone'"
            />
            <Button 
              icon="pi pi-trash" 
              class="p-button-rounded p-button-text p-button-sm p-button-danger"
              @click="confirmDeleteTemplate(data)"
              v-tooltip.top="'Delete'"
            />
          </div>
        </template>
      </Column>
      
      <template #empty>
        <div class="p-4 text-center">
          <i class="pi pi-inbox text-5xl text-400 mb-3" />
          <p class="text-600">No templates found</p>
          <Button 
            label="Create New Template" 
            icon="pi pi-plus" 
            @click="showTemplateDialog = true"
            class="mt-3"
          />
        </div>
      </template>
      
      <template #loading>
        <div class="p-4 text-center">
          <i class="pi pi-spin pi-spinner text-2xl"></i>
          <p class="mt-2">Loading templates...</p>
        </div>
      </template>
    </DataTable>
    
    <!-- Template Dialog -->
    <Dialog 
      v-model:visible="showTemplateDialog" 
      :header="editingTemplate ? 'Edit Template' : 'New Template'"
      :modal="true"
      :style="{ width: '70vw' }"
      :maximizable="true"
      :closable="true"
    >
      <div v-if="templateForm">
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="name">Template Name <span class="text-red-500">*</span></label>
              <InputText 
                id="name" 
                v-model="templateForm.name" 
                class="w-full" 
                :class="{ 'p-invalid': submitted && !templateForm.name }"
              />
              <small v-if="submitted && !templateForm.name" class="p-error">
                Template name is required
              </small>
            </div>
            
            <div class="field">
              <label for="description">Description</label>
              <Textarea 
                id="description" 
                v-model="templateForm.description" 
                rows="2" 
                class="w-full" 
                autoResize
              />
            </div>
            
            <div class="field">
              <label for="statement_type">Statement Type <span class="text-red-500">*</span></label>
              <Dropdown 
                id="statement_type"
                v-model="templateForm.statement_type" 
                :options="statementTypeOptions" 
                optionLabel="label"
                optionValue="value"
                placeholder="Select Type"
                class="w-full"
                :class="{ 'p-invalid': submitted && !templateForm.statement_type }"
                :disabled="!!editingTemplate"
              />
              <small v-if="submitted && !templateForm.statement_type" class="p-error">
                Statement type is required
              </small>
            </div>
            
            <div class="field-checkbox">
              <Checkbox 
                id="is_default" 
                v-model="templateForm.is_default" 
                :binary="true"
              />
              <label for="is_default" class="ml-2">Set as default template for this statement type</label>
            </div>
          </div>
          
          <div class="col-12">
            <div class="flex justify-content-between align-items-center mb-3">
              <h4>Template Structure</h4>
              <div>
                <Button 
                  label="Add Header" 
                  icon="pi pi-plus" 
                  class="p-button-text p-button-sm"
                  @click="addLine('header')"
                />
                <Button 
                  label="Add Account" 
                  icon="pi pi-plus" 
                  class="p-button-text p-button-sm"
                  @click="addLine('account')"
                />
                <Button 
                  label="Add Calculation" 
                  icon="pi pi-plus" 
                  class="p-button-text p-button-sm"
                  @click="addLine('calculation')"
                />
                <Button 
                  label="Add Total" 
                  icon="pi pi-plus" 
                  class="p-button-text p-button-sm"
                  @click="addLine('total')"
                />
              </div>
            </div>
            
            <TreeTable 
              :value="templateForm.structure" 
              :expandedKeys="expandedKeys"
              @nodeExpand="onNodeExpand"
              @nodeCollapse="onNodeCollapse"
              class="p-treetable-sm"
              scrollable
              scrollHeight="400px"
            >
              <Column field="name" header="Name" :expander="true">
                <template #body="{ node }">
                  <span :class="getLineStyle(node)">
                    {{ node.data.name }}
                  </span>
                </template>
              </Column>
              
              <Column field="code" header="Code">
                <template #body="{ node }">
                  <InputText 
                    v-model="node.data.code" 
                    class="w-full" 
                    :disabled="node.data.line_type === 'header'"
                  />
                </template>
              </Column>
              
              <Column field="account_number" header="Account" v-if="showAccountNumberColumn">
                <template #body="{ node }">
                  <AutoComplete 
                    v-if="node.data.line_type === 'account'"
                    v-model="node.data.account_number"
                    :suggestions="filteredAccounts"
                    @complete="searchAccounts($event)"
                    field="number"
                    :dropdown="true"
                    forceSelection
                    class="w-full"
                    placeholder="Select Account"
                  >
                    <template #item="slotProps">
                      <div class="flex align-items-center">
                        <div>
                          <div class="font-medium">{{ slotProps.item.number }}</div>
                          <div class="text-sm text-500">{{ slotProps.item.name }}</div>
                        </div>
                      </div>
                    </template>
                  </AutoComplete>
                  <span v-else class="text-400">-</span>
                </template>
              </Column>
              
              <Column field="calculation_formula" header="Formula" v-if="showFormulaColumn">
                <template #body="{ node }">
                  <InputText 
                    v-if="node.data.line_type === 'calculation'"
                    v-model="node.data.calculation_formula" 
                    class="w-full" 
                    placeholder="E.g., A1 + A2 - A3"
                  />
                  <span v-else class="text-400">-</span>
                </template>
              </Column>
              
              <Column field="actions" header="Actions" style="width: 120px">
                <template #body="{ node }">
                  <div class="flex gap-1">
                    <Button 
                      icon="pi pi-plus" 
                      class="p-button-rounded p-button-text p-button-sm"
                      @click="addChildLine(node)"
                      v-tooltip.top="'Add Child'"
                    />
                    <Button 
                      icon="pi pi-trash" 
                      class="p-button-rounded p-button-text p-button-sm p-button-danger"
                      @click="removeLine(node)"
                      v-tooltip.top="'Remove'"
                    />
                    <Button 
                      icon="pi pi-arrow-up" 
                      class="p-button-rounded p-button-text p-button-sm"
                      @click="moveLineUp(node)"
                      :disabled="isFirstSibling(node)"
                      v-tooltip.top="'Move Up'"
                    />
                    <Button 
                      icon="pi pi-arrow-down" 
                      class="p-button-rounded p-button-text p-button-sm"
                      @click="moveLineDown(node)"
                      :disabled="isLastSibling(node)"
                      v-tooltip.top="'Move Down'"
                    />
                  </div>
                </template>
              </Column>
            </TreeTable>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          @click="closeTemplateDialog" 
          class="p-button-text"
        />
        <Button 
          label="Save" 
          icon="pi pi-check" 
          @click="saveTemplate" 
          class="p-button-success"
          :loading="saving"
        />
      </template>
    </Dialog>
    
    <!-- Delete Confirmation -->
    <Dialog 
      v-model:visible="deleteDialog.visible" 
      header="Confirm Delete" 
      :modal="true"
      :style="{ width: '450px' }"
    >
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="deleteDialog.template">
          Are you sure you want to delete <b>{{ deleteDialog.template.name }}</b>?
        </span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          @click="deleteDialog.visible = false" 
          class="p-button-text"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          @click="deleteTemplate" 
          class="p-button-danger"
          :loading="deleting"
        />
      </template>
    </Dialog>
    
    <!-- Template Preview Dialog -->
    <Dialog 
      v-model:visible="previewDialog.visible" 
      :header="'Preview: ' + (previewDialog.template?.name || '')" 
      :modal="true"
      :style="{ width: '80vw' }"
      :maximizable="true"
    >
      <div v-if="previewDialog.template">
        <div class="mb-4 p-4 border-round border-1 surface-border">
          <div class="grid">
            <div class="col-12 md:col-6">
              <div class="text-500 font-medium mb-1">Name</div>
              <div class="font-medium">{{ previewDialog.template.name }}</div>
            </div>
            <div class="col-12 md:col-6">
              <div class="text-500 font-medium mb-1">Type</div>
              <div>{{ formatStatementType(previewDialog.template.statement_type) }}</div>
            </div>
            <div class="col-12 md:col-6">
              <div class="text-500 font-medium mb-1">Default</div>
              <div>
                <i 
                  :class="previewDialog.template.is_default ? 'pi pi-check-circle text-green-500' : 'pi pi-times-circle text-red-500'"
                ></i>
                {{ previewDialog.template.is_default ? 'Yes' : 'No' }}
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="text-500 font-medium mb-1">Last Updated</div>
              <div>{{ formatDate(previewDialog.template.updated_at) }}</div>
            </div>
            <div class="col-12" v-if="previewDialog.template.description">
              <div class="text-500 font-medium mb-1">Description</div>
              <div>{{ previewDialog.template.description }}</div>
            </div>
          </div>
        </div>
        
        <h4>Template Structure</h4>
        <TreeTable 
          :value="buildTemplateTree(previewDialog.template.structure)" 
          class="p-treetable-sm"
          scrollable
          scrollHeight="400px"
        >
          <Column field="name" header="Name" expander>
            <template #body="{ node }">
              <span :class="getLineStyle(node)">
                {{ node.data.name }}
              </span>
            </template>
          </Column>
          
          <Column field="code" header="Code">
            <template #body="{ node }">
              <span>{{ node.data.code || '-' }}</span>
            </template>
          </Column>
          
          <Column field="account_number" header="Account" v-if="previewDialog.template.structure.some(l => l.line_type === 'account')">
            <template #body="{ node }">
              <span v-if="node.data.line_type === 'account' && node.data.account_number">
                {{ node.data.account_number }}
              </span>
              <span v-else class="text-400">-</span>
            </template>
          </Column>
          
          <Column field="calculation_formula" header="Formula" v-if="previewDialog.template.structure.some(l => l.line_type === 'calculation')">
            <template #body="{ node }">
              <code v-if="node.data.line_type === 'calculation' && node.data.calculation_formula">
                {{ node.data.calculation_formula }}
              </code>
              <span v-else class="text-400">-</span>
            </template>
          </Column>
        </TreeTable>
      </div>
      
      <template #footer>
        <Button 
          label="Close" 
          @click="previewDialog.visible = false" 
          class="p-button-text"
        />
        <Button 
          label="Edit Template" 
          icon="pi pi-pencil" 
          @click="editTemplate(previewDialog.template)"
          class="p-button-primary"
        />
      </template>
    </Dialog>
  </div>
</template>
