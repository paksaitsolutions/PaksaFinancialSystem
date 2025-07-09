<template>
  <AppLayout>
    <template #header>
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <h1 class="text-2xl font-semibold text-gray-900">
            {{ isEditMode ? 'Edit Journal Entry' : 'New Journal Entry' }}
          </h1>
          <span v-if="entry.status" :class="statusBadgeClass">
            {{ entry.status.toUpperCase() }}
          </span>
        </div>
        <div class="flex space-x-2">
          <!-- Action Menu -->
          <Menu as="div" class="relative inline-block text-left">
            <div>
              <MenuButton class="inline-flex justify-center w-full px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                Actions
                <ChevronDownIcon class="w-5 h-5 ml-2 -mr-1" aria-hidden="true" />
              </MenuButton>
            </div>

            <transition enter-active-class="transition duration-100 ease-out" enter-from-class="transform scale-95 opacity-0" enter-to-class="transform scale-100 opacity-100" leave-active-class="transition duration-75 ease-in" leave-from-class="transform scale-100 opacity-100" leave-to-class="transform scale-95 opacity-0">
              <MenuItems class="absolute right-0 z-10 w-56 mt-2 origin-top-right bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                <div class="py-1">
                  <!-- Save as Draft -->
                  <MenuItem v-slot="{ active }" v-if="isEditable">
                    <button
                      :class="[active ? 'bg-gray-100 text-gray-900' : 'text-gray-700', 'w-full text-left px-4 py-2 text-sm']"
                      @click="saveEntry('draft')"
                      :disabled="isSaving"
                    >
                      Save as Draft
                    </button>
                  </MenuItem>

                  <!-- Post Entry -->
                  <MenuItem v-slot="{ active }" v-if="isEditable">
                    <button
                      :class="[active ? 'bg-gray-100 text-gray-900' : 'text-gray-700', 'w-full text-left px-4 py-2 text-sm']"
                      @click="handleApproveEntry"
                      :disabled="isSaving || entry.status === 'approved'"
                    >
                      Post Entry
                    </button>
                  </MenuItem>

                  <!-- Approve Entry -->
                  <MenuItem v-slot="{ active }" v-if="canApprove">
                    <button
                      :class="[active ? 'bg-gray-100 text-gray-900' : 'text-gray-700', 'w-full text-left px-4 py-2 text-sm']"
                      @click="approveEntry"
                      :disabled="isSaving"
                    >
                      Approve Entry
                    </button>
                  </MenuItem>

                  <!-- Reverse Entry -->
                  <MenuItem v-slot="{ active }" v-if="canReverse">
                    <button
                      :class="[active ? 'bg-gray-100 text-gray-900' : 'text-gray-700', 'w-full text-left px-4 py-2 text-sm']"
                      @click="showReverseDialog = true"
                      :disabled="isSaving"
                    >
                      Reverse Entry
                    </button>
                  </MenuItem>

                  <!-- Create Recurring -->
                  <MenuItem v-slot="{ active }" v-if="isEditMode && entry.status === 'posted'">
                    <button
                      :class="[active ? 'bg-gray-100 text-gray-900' : 'text-gray-700', 'w-full text-left px-4 py-2 text-sm']"
                      @click="showRecurringDialog = true"
                      :disabled="isSaving"
                    >
                      Create Recurring Entry
                    </button>
                  </MenuItem>

                  <!-- Delete Entry -->
                  <MenuItem v-slot="{ active }" v-if="canDelete">
                    <button
                      :class="[active ? 'bg-red-50 text-red-700' : 'text-red-600', 'w-full text-left px-4 py-2 text-sm font-medium']"
                      @click="confirmDelete"
                      :disabled="isSaving"
                    >
                      Delete Entry
                    </button>
                  </MenuItem>
                </div>
              </MenuItems>
            </div>
          </Menu>

          <!-- Main Save/Update Button -->
          <button
            type="button"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            @click="isEditMode ? saveEntry('posted') : postEntry()"
            :disabled="isSaving || !isFormValid"
          >
            <DocumentTextIcon class="h-5 w-5 mr-2" />
            {{ isEditMode ? 'Update' : 'Save' }}
          </button>

          <!-- Cancel Button -->
          <button
            type="button"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            @click="confirmCancel"
            :disabled="isSaving"
          >
            Cancel
          </button>
        </div>
      </div>
    </template>

    <div class="space-y-6">
      <!-- Status Alert -->
      <div v-if="entry.status && entry.status !== 'draft'" class="rounded-md bg-blue-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <InformationCircleIcon class="h-5 w-5 text-blue-400" aria-hidden="true" />
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-blue-800">
              This entry is {{ entry.status }} on {{ formatDate(entry.posted_at || entry.updated_at) }}
            </h3>
            <div v-if="entry.approved_by" class="mt-2 text-sm text-blue-700">
              <p>Approved by {{ entry.approved_by }} on {{ formatDate(entry.approved_at) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Form -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6 space-y-6">
          <!-- Header Fields -->
          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div class="sm:col-span-2">
              <label for="entry_date" class="block text-sm font-medium text-gray-700">
                Entry Date <span class="text-red-500">*</span>
              </label>
              <div class="mt-1">
                <input
                  id="entry_date"
                  v-model="entry.entry_date"
                  type="date"
                  :disabled="!isEditable"
                  class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  :class="{ 'bg-gray-100': !isEditable }"
                />
              </div>
            </div>

            <div class="sm:col-span-2">
              <label for="reference" class="block text-sm font-medium text-gray-700">
                Reference <span class="text-red-500">*</span>
              </label>
              <div class="mt-1">
                <input
                  id="reference"
                  v-model="entry.reference"
                  type="text"
                  :disabled="!isEditable"
                  class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  :class="{ 'bg-gray-100': !isEditable }"
                />
              </div>
            </div>

            <div class="sm:col-span-2">
              <label for="currency" class="block text-sm font-medium text-gray-700">
                Currency <span class="text-red-500">*</span>
              </label>
              <div class="mt-1">
                <select
                  id="currency"
                  v-model="entry.currency"
                  :disabled="!isEditable"
                  class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  :class="{ 'bg-gray-100': !isEditable }"
                >
                  <option value="PKR">PKR - Pakistani Rupee</option>
                  <option value="USD">USD - US Dollar</option>
                  <option value="EUR">EUR - Euro</option>
                  <option value="GBP">GBP - British Pound</option>
                  <option value="AED">AED - UAE Dirham</option>
                  <option value="SAR">SAR - Saudi Riyal</option>
                </select>
              </div>
            </div>

            <div class="sm:col-span-6">
              <label for="description" class="block text-sm font-medium text-gray-700">
                Description
              </label>
              <div class="mt-1">
                <input
                  id="description"
                  v-model="line.description"
                  type="text"
                  @input="updateLineDescription(index, ($event.target as HTMLInputElement).value)"
                  class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  :disabled="!isEditable"
                />
              </div>
            </div>
          </div>

          <!-- Line Items -->
          <div class="mt-8">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-medium text-gray-900">Line Items</h3>
              <button
                v-if="isEditable"
                type="button"
                class="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                @click="addLineItem"
              >
                <PlusIcon class="-ml-0.5 mr-1.5 h-4 w-4" />
                Add Line
              </button>
            </div>

            <div class="mt-4 overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Account
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Description
                    </th>
                    <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Debit
                    </th>
                    <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Credit
                    </th>
                    <th v-if="isEditable" scope="col" class="relative px-6 py-3">
                      <span class="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(line, index) in entry.line_items" :key="line.id || `new-${index}`">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <AccountSelect
                        v-model="line.account_id"
                        :disabled="!isEditable"
                        :error="lineErrors[index]?.account_id"
                        @update:modelValue="updateLineAccount(index, $event)"
                      />
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <input
                        type="text"
                        v-model="line.description"
                        @input="updateLineDescription(index, ($event.target as HTMLInputElement).value)"
                        class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                        :disabled="!isEditable"
                      />
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right">
                      <input
                        type="number"
                        min="0"
                        step="0.01"
                        :value="line.debit"
                        @input="updateLineAmount(index, 'debit', ($event.target as HTMLInputElement).value)"
                        class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                        :disabled="!isEditable"
                      />
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right">
                      <CurrencyInput
                        v-model="line.debit"
                        :disabled="!isEditable"
                        :currency="entry.currency"
                        class="text-right"
                        :class="{ 'bg-gray-100': !isEditable }"
                        @update:modelValue="updateLineAmount(index, 'debit', $event)"
                      />
                    </td>
                    <td v-if="isEditable" class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        type="button"
                        class="text-red-600 hover:text-red-900"
                        @click="removeLineItem(index)"
                      >
                        <TrashIcon class="h-5 w-5" />
                      </button>
                    </td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="border-t border-gray-200">
                    <th scope="row" colspan="2" class="px-6 py-3 text-right text-sm font-medium text-gray-500">
                      Totals:
                    </th>
                    <td class="px-6 py-3 text-right text-sm font-medium text-gray-900">
                      {{ formatCurrency(entry.total_debit || 0, entry.currency) }}
                    </td>
                    <td class="px-6 py-3 text-right text-sm font-medium text-gray-900">
                      {{ formatCurrency(entry.total_credit || 0, entry.currency) }}
                    </td>
                    <td v-if="isEditable" class="px-6 py-3"></td>
                  </tr>
                  <tr v-if="totalDifference !== 0" class="bg-red-50">
                    <th scope="row" colspan="2" class="px-6 py-3 text-right text-sm font-medium text-red-700">
                      Difference:
                    </th>
                    <td class="px-6 py-3 text-right text-sm font-medium text-red-700" colspan="2">
                      {{ formatCurrency(Math.abs(totalDifference), entry.currency) }}
                      ({{ totalDifference > 0 ? 'Debit' : 'Credit' }})
                    </td>
                    <td v-if="isEditable" class="px-6 py-3"></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <!-- Notes -->
          <div class="mt-8">
            <label for="notes" class="block text-sm font-medium text-gray-700">Notes</label>
            <div class="mt-1">
              <textarea
                id="notes"
                v-model="entry.notes"
                rows="3"
                :disabled="!isEditable"
                class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                :class="{ 'bg-gray-100': !isEditable }"
              />
            </div>
            <p class="mt-2 text-sm text-gray-500">
              Add any additional notes or details about this journal entry.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Reversal Confirmation Dialog -->
    <Dialog :open="showReverseDialog" @close="showReverseDialog = false">
      <div class="fixed inset-0 bg-black bg-opacity-30" aria-hidden="true" @click="showReverseDialog = false" />
      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <div class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
              <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                Reverse Journal Entry
              </DialogTitle>
              <div class="mt-2">
                <p class="text-sm text-gray-500">
                  Are you sure you want to reverse this journal entry? This will create a new reversing entry.
                </p>
                <div class="mt-4">
                  <label for="reversal-date" class="block text-sm font-medium text-gray-700">Reversal Date</label>
                  <input
                    type="date"
                    id="reversal-date"
                    v-model="reversalDate"
                    :min="new Date().toISOString().split('T')[0]"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                </div>
                <div class="mt-4">
                  <label for="reversal-description" class="block text-sm font-medium text-gray-700">Description</label>
                  <input
                    type="text"
                    id="reversal-description"
                    v-model="reversalDescription"
                    placeholder="Enter a description for the reversal"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                </div>
              </div>

              <div class="mt-4 flex justify-end space-x-3">
                <button
                  type="button"
                  class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  @click="showReverseDialog = false"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  class="inline-flex justify-center rounded-md border border-transparent bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                  @click="reverseEntry(reversalDate, reversalDescription)"
                >
                  Confirm Reversal
                </button>
              </div>
            </div>
          </TransitionChild>
        </div>
      </div>
    </Dialog>

    <!-- Recurring Entry Dialog -->
    <!-- Recurring Entry Dialog -->
    <Dialog :open="showRecurringDialog" @close="showRecurringDialog = false">
      <div class="fixed inset-0 bg-black bg-opacity-30" aria-hidden="true" @click="showRecurringDialog = false" />
      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <div class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
              <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                Create Recurring Journal Entry
              </DialogTitle>
              <div class="mt-2">
                <p class="text-sm text-gray-500">
                  Set up a recurring journal entry based on this template.
                </p>
                <div class="mt-4 space-y-4">
                  <div>
                    <label for="frequency" class="block text-sm font-medium text-gray-700">Frequency</label>
                    <select
                      id="frequency"
                      v-model="recurringData.frequency"
                      class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                    >
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly" selected>Monthly</option>
                      <option value="quarterly">Quarterly</option>
                      <option value="yearly">Yearly</option>
                    </select>
                  </div>
                  <div>
                    <label for="start-date" class="block text-sm font-medium text-gray-700">Start Date</label>
                    <input
                      type="date"
                      id="start-date"
                      v-model="recurringData.startDate"
                      :min="new Date().toISOString().split('T')[0]"
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label for="end-type" class="block text-sm font-medium text-gray-700">Ends</label>
                    <div class="mt-1 space-x-4">
                      <label class="inline-flex items-center">
                        <input
                          type="radio"
                          v-model="recurringData.endType"
                          value="never"
                          class="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                        />
                        <span class="ml-2 text-sm text-gray-700">Never</span>
                      </label>
                      <label class="inline-flex items-center">
                        <input
                          type="radio"
                          v-model="recurringData.endType"
                          value="on"
                          class="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                        />
                        <span class="ml-2 text-sm text-gray-700">On</span>
                        <input
                          type="date"
                          v-model="recurringData.endDate"
                          :disabled="recurringData.endType !== 'on'"
                          :min="recurringData.startDate"
                          class="ml-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        />
                      </label>
                      <label class="inline-flex items-center">
                        <input
                          type="radio"
                          v-model="recurringData.endType"
                          value="after"
                          class="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                        />
                        <span class="ml-2 text-sm text-gray-700">After</span>
                        <input
                          type="number"
                          v-model.number="recurringData.occurrences"
                          :disabled="recurringData.endType !== 'after'"
                          min="1"
                          class="ml-2 w-20 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        />
                        <span class="ml-2 text-sm text-gray-700">occurrences</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              <div class="mt-4 flex justify-end space-x-3">
                <button
                  type="button"
                  class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  @click="showRecurringDialog = false"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  class="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  @click="handleRecurringEntry"
                  :disabled="!canCreateRecurring"
                >
                  Create Recurring
                </button>
              </div>
            </div>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type { Ref } from 'vue';
import AppLayout from '@/layouts/AppLayout.vue';
import { 
  DocumentTextIcon,
  TrashIcon,
  InformationCircleIcon
} from '@heroicons/vue/24/outline';

// Toast notification type
type ToastType = 'success' | 'error' | 'warning' | 'info';

// Simple toast implementation as fallback
const useToast = () => {
  const show = (message: string, options: { type?: ToastType } = {}) => {
    const type = options.type || 'info';
    console[type](`[${type.toUpperCase()}] ${message}`);
  };

  return {
    success: (message: string) => show(message, { type: 'success' }),
    error: (message: string) => show(message, { type: 'error' }),
    warning: (message: string) => show(message, { type: 'warning' }),
    info: (message: string) => show(message, { type: 'info' }),
    show,
    updateDefaults: () => {},
    clear: () => {}
  };
};

// Initialize toast
const toast = useToast();

// Wrapper function for showing toast messages
const showToast = (message: string, type: ToastType = 'info'): void => {
  toast[type](message);
};

// Type definitions
type JournalEntryStatus = 'draft' | 'posted' | 'approved' | 'rejected' | 'reversed' | 'pending_approval';
type RecurringFrequency = 'daily' | 'weekly' | 'monthly' | 'yearly';
type RecurringEndType = 'never' | 'on' | 'after';

// Journal Entry Line interface
interface JournalEntryLine {
  id: string;
  account_id: string;
  account_name?: string;
  account_code?: string;
  description: string;
  debit: number;
  credit: number;
  tax_code?: string | null;
  cost_center?: string | null;
  cost_center_id?: string | null;
  tax_id?: string | null;
  project_id?: string | null;
  line_number: number;
  reference?: string;
  created_at?: string;
  updated_at?: string;
  [key: string]: unknown;
}

// Journal Entry interface
interface JournalEntry {
  id: string;
  entry_number: string;
  entry_date: string;
  reference: string;
  description: string;
  status: JournalEntryStatus;
  currency: string;
  lines: JournalEntryLine[];
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
  company_id: string;
  branch_id?: string;
  fiscal_year_id: string;
  period_id: string;
  source: string;
  source_id?: string | null;
  reference_type?: string;
  is_recurring?: boolean;
  recurring_id?: string | null;
  is_reversed?: boolean;
  reversed_entry_id?: string | null;
  reversal_id?: string | null;
  posted_at?: string;
  posted_by?: string;
  approved_at?: string;
  approved_by?: string;
  attachments?: unknown[];
  notes?: string;
  custom_fields?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  total_debit?: number;
  total_credit?: number;
  line_items?: unknown[];
  [key: string]: unknown;
}

// Recurring data interface
interface RecurringData {
  frequency: RecurringFrequency;
  interval: number;
  start_date: string;
  end_date: string;
  max_occurrences: number;
  week_day: number;
  month_day: number;
  is_active: boolean;
  endType: RecurringEndType;
  endDate: string;
  occurrences: number;
  startDate?: string;
}

// Consolidated Journal Entry Line interface
interface JournalEntryLine {
  id: string;
  account_id: string;
  account_name?: string;
  account_code?: string;
  description: string;
  debit: number;
  credit: number;
  tax_code?: string | null;
  cost_center?: string | null;
  cost_center_id?: string | null;
  tax_id?: string | null;
  project_id: string | null;
  line_number: number;
  reference?: string;
  created_at?: string;
  updated_at?: string;
  [key: string]: unknown;
}

// Consolidated Journal Entry interface
interface JournalEntry {
  id: string;
  entry_number: string;
  entry_date: string;
  reference: string;
  description: string;
  status: JournalEntryStatus;
  currency: string;
  lines: JournalEntryLine[];
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
  company_id: string;
  branch_id?: string;
  fiscal_year_id: string;
  period_id: string;
  source: string;
  source_id?: string | null;
  reference_type?: string;
  is_recurring?: boolean;
  recurring_id?: string | null;
  is_reversed?: boolean;
  reversed_entry_id?: string | null;
  reversal_id?: string | null;
  posted_at?: string;
  posted_by?: string;
  approved_at?: string;
  approved_by?: string;
  attachments?: unknown[];
  notes?: string;
  custom_fields?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  total_debit?: number;
  total_credit?: number;
  line_items?: unknown[];
  [key: string]: unknown;
}

// Toast service type
type ToastService = {
  (content: string, options?: ToastOptions): void;
  clear(): void;
  updateDefaults(update: Partial<ToastOptions>): void;
  success(content: string, options?: ToastOptions): void;
  error(content: string, options?: ToastOptions): void;
  warning(content: string, options?: ToastOptions): void;
  info(content: string, options?: ToastOptions): void;
  show(content: string, options?: ToastOptions): void;
};

// Mock API functions - Replace these with actual implementations
const useJournalEntryApi = () => ({
  getJournalEntry: async (id: string): Promise<JournalEntry> => {
    // Mock implementation
    return {
      id,
      entry_number: `JE-${id.slice(0, 8)}`,
      entry_date: new Date().toISOString().split('T')[0],
      reference: '',
      description: '',
      status: 'draft',
      currency: 'USD',
      lines: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      created_by: '',
      updated_by: '',
      company_id: '',
      branch_id: '',
      reference_type: '',
      is_recurring: false,
      recurring_id: null,
      is_reversed: false,
      reversed_entry_id: null,
      reversal_id: null,
      attachments: [],
      notes: ''
    };
  },
  createJournalEntry: async (entry: Omit<JournalEntry, 'id'>): Promise<JournalEntry> => {
    // Mock implementation
    return {
      ...entry,
      id: `je_${Date.now()}`,
      entry_number: `JE-${Date.now().toString().slice(-6)}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      status: 'draft'
    } as JournalEntry;
  },
  updateJournalEntry: async (id: string, entry: Partial<JournalEntry>): Promise<JournalEntry> => {
    // Mock implementation
    return {
      id,
      ...entry,
      updated_at: new Date().toISOString()
    } as JournalEntry;
  },
  postJournalEntry: async (id: string): Promise<JournalEntry> => {
    // Mock implementation
    return {
      id,
      status: 'posted',
      updated_at: new Date().toISOString()
    } as JournalEntry;
  },
  reverseJournalEntry: async (id: string, data: any): Promise<JournalEntry> => {
    // Mock implementation
    return {
      id: `je_${Date.now()}`,
      status: 'reversed',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      ...data
    } as JournalEntry;
  },
  createRecurringJournalEntries: async (data: any): Promise<{ count: number }> => {
    // Mock implementation
    return { count: 1 };
  }
});

// Mock account store
interface AccountStore {
  currentUser: {
    permissions: string[];
  };
  accounts: any[];
}

const useAccountStore = (): AccountStore => ({
  currentUser: {
    permissions: [
      'view_journal_entries', 
      'create_journal_entries', 
      'edit_journal_entries',
      'post_journal_entries',
      'approve_journal_entries'
    ]
  },
  accounts: []
});

const {
  getJournalEntry: fetchJournalEntry,
  createJournalEntry,
  updateJournalEntry,
  postJournalEntry,
  reverseJournalEntry,
  createRecurringJournalEntries
} = useJournalEntryApi();

const accountStore = useAccountStore();
import CurrencyInput from '@/components/CurrencyInput.vue';
import DatePicker from '@/components/DatePicker.vue';
import AppLayout from '@/layouts/AppLayout.vue';

// Refs for dialogs
const showReverseDialog = ref<boolean>(false);
const showRecurringDialog = ref<boolean>(false);
const isSaving = ref<boolean>(false);
const isFormValid = ref<boolean>(false);
const route = useRoute();
const router = useRouter();

// Computed properties
const isEditMode = computed<boolean>(() => route.name === 'edit-journal-entry');
const isEditable = computed<boolean>(() => !isEditMode.value || entry.value.status === 'draft');

// Calculate totals
const total_debit = computed<number>(() => {
  return entry.value.lines.reduce((sum, line) => sum + (parseFloat(String(line.debit)) || 0), 0);
});

const total_credit = computed<number>(() => {
  return entry.value.lines.reduce((sum, line) => sum + (parseFloat(String(line.credit)) || 0), 0);
});

const totalDifference = computed<number>(() => {
  return Math.abs(total_debit.value - total_credit.value);
});

// Line errors
const lineErrors = computed<Record<number, string>>(() => {
  const errors: Record<number, string> = {};
  
  if (!entry.value?.lines?.length) {
    return errors;
      break;
    case 'error':
      toast.error(message, options);
      break;
    case 'warning':
      toast.warning(message, options);
      break;
    case 'info':
    default:
      toast.info(message, options);
      break;
  }
};

// ...

// Save entry
const saveEntry = async (): Promise<void> => {
  if (!entry.value) {
    showToast('Entry data is not initialized', 'error');
    return;
  }

  try {
    isSaving.value = true;
    
    // Validate form
    if (Object.keys(lineErrors.value).length > 0) {
      showToast('Please fix all validation errors before saving', 'error');
      return;
    }

    // Ensure lines exist and have required fields
    const lines: JournalEntryLine[] = (entry.value.lines || []).map((line, index) => ({
      id: line.id || `line-${Date.now()}-${index}`,
      account_id: line.account_id || '',
      description: line.description || '',
      debit: Number(line.debit) || 0,
      credit: Number(line.credit) || 0,
      line_number: line.line_number || index + 1,
      cost_center_id: line.cost_center_id || null,
      tax_id: line.tax_id || null,
      reference: line.reference || '',
      // Ensure all required fields from the interface are included
      account_name: line.account_name || '',
      account_code: line.account_code || '',
      tax_code: line.tax_code || null,
      cost_center: line.cost_center || null,
      project_id: line.project_id || null,
      created_at: line.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }));

    // Prepare the payload with proper typing
    const payload: JournalEntry = {
      ...entry.value,
      id: entry.value.id || `je-${Date.now()}`,
      entry_number: entry.value.entry_number || `JE-${new Date().getFullYear()}-${Math.floor(1000 + Math.random() * 9000)}`,
      entry_date: entry.value.entry_date || new Date().toISOString().split('T')[0],
      reference: entry.value.reference || '',
      description: entry.value.description || '',
      status: entry.value.status || 'draft',
      currency: entry.value.currency || 'PKR',
      lines,
      created_at: entry.value.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
      created_by: entry.value.created_by || 'system',
      updated_by: 'system',
      company_id: entry.value.company_id || 'default-company',
      branch_id: entry.value.branch_id || 'default-branch',
      fiscal_year_id: entry.value.fiscal_year_id || 'current-fiscal-year',
      period_id: entry.value.period_id || 'current-period',
      source: entry.value.source || 'manual',
      reference_type: entry.value.reference_type || 'manual',
      is_recurring: entry.value.is_recurring || false,
      recurring_id: entry.value.recurring_id || null,
      is_reversed: entry.value.is_reversed || false,
      reversed_entry_id: entry.value.reversed_entry_id || null,
      reversal_id: entry.value.reversal_id || null,
      attachments: entry.value.attachments || [],
      notes: entry.value.notes || '',
      custom_fields: entry.value.custom_fields || {},
      metadata: entry.value.metadata || {},
    };

    // Call your API here
    // const response = await journalEntryApi.saveJournalEntry(payload);
    
    // Update local state with the saved entry
    entry.value = payload;
    
    showToast('Journal entry saved successfully', 'success');
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Failed to save journal entry';
    showToast(errorMessage, 'error');
    console.error('Error saving journal entry:', error);
  } finally {
    isSaving.value = false;
  }
};

// Post entry (mark as posted)
const postEntry = async (): Promise<void> => {
  if (!entry.value?.id) {
    showToast('Cannot post an unsaved journal entry', 'error');
    return;
  }

  try {
    isSaving.value = true;
    
    // Call your API here to post the entry
    // const response = await journalEntryApi.postJournalEntry(entry.value.id);
    
    showToast('Journal entry posted successfully', 'success');
    
    // Refresh the entry data
    // await loadEntry(entry.value.id);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Failed to post journal entry';
    showToast(errorMessage, 'error');
    console.error('Error posting journal entry:', error);
  } finally {
    isSaving.value = false;
  }
};

    router.push('/accounting/journal-entries');
  }
};

const confirmDelete = (): void => {
  if (confirm('Are you sure you want to delete this journal entry? This action cannot be undone.')) {
    deleteEntry();
  }
};

// Delete entry
const deleteEntry = async (): Promise<void> => {
  if (!entry.value.id) {
    router.push('/accounting/journal-entries');
    return;
  }

  try {
    isSaving.value = true;
    const response = await fetch(`/api/journal-entries/${entry.value.id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete journal entry');
    }

    showSuccess('Journal entry deleted successfully');
    router.push('/accounting/journal-entries');
  } catch (error) {
    showError('Failed to delete journal entry');
    console.error('Error deleting journal entry:', error);
  } finally {
    isSaving.value = false;
  }
};

// Approve entry
const approveEntry = async (): Promise<void> => {
  if (!entry.value.id) {
    showError('Cannot approve an unsaved journal entry');
    return;
  }

  try {
    isSaving.value = true;
    const response = await fetch(`/api/journal-entries/${entry.value.id}/approve`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error('Failed to approve journal entry');
    }

    showSuccess('Journal entry approved successfully');
    await loadEntry(entry.value.id);
  } catch (error) {
    showError('Failed to approve journal entry');
    console.error('Error approving journal entry:', error);
  } finally {
    isSaving.value = false;
  }
};

// Handle reverse entry
const handleReverseEntry = async (): Promise<void> => {
  try {
    isSaving.value = true;
    const response = await fetch(`/api/journal-entries/${entry.value.id}/reverse`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        description: reversalDescription.value,
        reverse_date: new Date().toISOString().split('T')[0]
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to reverse journal entry');
    }

    const result = await response.json();
    showSuccess('Journal entry reversed successfully');
    showReverseDialog.value = false;
    router.push(`/accounting/journal-entries/${result.id}/edit`);
  } catch (error: any) {
    showError(error.message || 'Failed to reverse journal entry');
    console.error('Error reversing journal entry:', error);
  } finally {
    isSaving.value = false;
  }
};

// Handle recurring entry
const handleRecurringEntry = async (): Promise<void> => {
  try {
    isSaving.value = true;
    
    // Validate recurring data
    if (!recurringData.value.start_date) {
      throw new Error('Start date is required');
    }
    
    if (recurringData.value.endType === 'on' && !recurringData.value.endDate) {
      throw new Error('End date is required when end type is set to "on"');
    }
    
    if (recurringData.value.endType === 'after' && !recurringData.value.occurrences) {
      throw new Error('Number of occurrences is required when end type is set to "after"');
    }
    
    const response = await fetch(`/api/journal-entries/${entry.value.id}/recurring`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...recurringData.value,
        template_id: entry.value.id,
        end_type: recurringData.value.endType,
        end_date: recurringData.value.endDate,
        start_date: recurringData.value.start_date, // Use start_date consistently
        occurrences: recurringData.value.occurrences
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to create recurring journal entry');
    }

    const result = await response.json();
    showSuccess('Recurring journal entry created successfully');
    showRecurringDialog.value = false;
    
    // Reset recurring form
    recurringData.value = {
      frequency: 'monthly',
      interval: 1,
      start_date: new Date().toISOString().split('T')[0],
      end_date: '',
      max_occurrences: 0,
      week_day: 1,
      month_day: 1,
      is_active: true,
      endType: 'never',
      endDate: '',
      occurrences: 1
    };
    
    // Navigate to the new recurring entry if needed
    if (result.id) {
      router.push(`/accounting/recurring-journal-entries/${result.id}`);
    }
  } catch (error: any) {
    showError(error.message || 'Failed to create recurring journal entry');
    console.error('Error creating recurring journal entry:', error);
  } finally {
    isSaving.value = false;
  }
};
</script>

<style scoped>
/* Add any custom styles here */
</style>
