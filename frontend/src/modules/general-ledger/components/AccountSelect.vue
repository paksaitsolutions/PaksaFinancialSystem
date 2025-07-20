<template>
  <div>
    <Combobox v-model="selectedAccount" @update:modelValue="handleSelect">
      <div class="relative">
        <div class="relative w-full cursor-default overflow-hidden rounded-md bg-white text-left shadow-sm border border-gray-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-white/75 focus-visible:ring-offset-2 focus-visible:ring-offset-indigo-300 sm:text-sm">
          <ComboboxInput
            class="w-full border-none py-2 pl-3 pr-10 text-sm leading-5 text-gray-900 focus:ring-0"
            :display-value="(account) => account ? `${account.code} - ${account.name}` : ''"
            @change="query = $event.target.value"
            placeholder="Select an account..."
            :disabled="disabled"
          />
          <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-2">
            <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
          </ComboboxButton>
        </div>
        <TransitionRoot
          leave="transition ease-in duration-100"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
          @after-leave="query = ''"
        >
          <ComboboxOptions class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black/5 focus:outline-none sm:text-sm">
            <div v-if="filteredAccounts.length === 0 && query !== ''" class="relative cursor-default select-none px-4 py-2 text-gray-700">
              No accounts found.
            </div>

            <ComboboxOption
              v-for="account in filteredAccounts"
              as="template"
              :key="account.id"
              :value="account"
              v-slot="{ selected, active }"
            >
              <li
                class="relative cursor-default select-none py-2 pl-10 pr-4"
                :class="{
                  'bg-indigo-600 text-white': active,
                  'text-gray-900': !active,
                }"
              >
                <span class="block truncate font-medium" :class="{ 'font-semibold': selected, 'font-normal': !selected }">
                  {{ account.code }} - {{ account.name }}
                </span>
                <span
                  v-if="selected"
                  class="absolute inset-y-0 left-0 flex items-center pl-3"
                  :class="{ 'text-white': active, 'text-indigo-600': !active }"
                >
                  <CheckIcon class="h-5 w-5" aria-hidden="true" />
                </span>
              </li>
            </ComboboxOption>
          </ComboboxOptions>
        </TransitionRoot>
      </div>
    </Combobox>
    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
  </div>
</template>

<script lang="ts">
import { ref, computed, watch, onMounted, defineComponent } from 'vue';
import {
  Combobox,
  ComboboxInput,
  ComboboxButton,
  ComboboxOptions,
  ComboboxOption,
  TransitionRoot,
} from '@headlessui/vue';
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/vue/20/solid';
import accountService from '@/services/accounting/accountService';

interface Account {
  id: string;
  code: string;
  name: string;
  category: string;
  is_active: boolean;
}

export default defineComponent({
  name: 'AccountSelect',
  components: {
    Combobox,
    ComboboxInput,
    ComboboxButton,
    ComboboxOptions,
    ComboboxOption,
    TransitionRoot,
    CheckIcon,
    ChevronUpDownIcon,
  },
  props: {
    modelValue: {
      type: String,
      default: '',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    error: {
      type: String,
      default: '',
    },
  },
  emits: ['update:modelValue', 'select'],
  setup(props, { emit }) {
    const accounts = ref<Account[]>([]);
    const selectedAccount = ref<Account | null>(null);
    const query = ref('');
    const isLoading = ref(false);

    // Filter accounts based on search query
    const filteredAccounts = computed(() => {
      if (query.value === '') {
        return accounts.value;
      }
      
      const searchTerm = query.value.toLowerCase();
      return accounts.value.filter(
        (account) =>
          account.code.toLowerCase().includes(searchTerm) ||
          account.name.toLowerCase().includes(searchTerm) ||
          account.category.toLowerCase().includes(searchTerm)
      );
    });

    // Load accounts from API
    const loadAccounts = async () => {
      try {
        isLoading.value = true;
        const data = await accountService.fetchAccounts({
          is_active: true,
          limit: 1000, // Adjust based on your needs
        });
        accounts.value = data.data || [];
        
        // If we have a value, find the corresponding account
        if (props.modelValue) {
          const account = accounts.value.find(a => a.id === props.modelValue);
          if (account) {
            selectedAccount.value = account;
          }
        }
      } catch (error) {
        console.error('Error loading accounts:', error);
      } finally {
        isLoading.value = false;
      }
    };

    // Handle account selection
    const handleSelect = (account: Account) => {
      selectedAccount.value = account;
      emit('update:modelValue', account.id);
      emit('select', account);
    };

    // Watch for changes to the modelValue prop
    watch(() => props.modelValue, (newValue) => {
      if (newValue && accounts.value.length > 0) {
        const account = accounts.value.find(a => a.id === newValue);
        if (account) {
          selectedAccount.value = account;
        }
      } else if (!newValue) {
        selectedAccount.value = null;
      }
    });

    // Load accounts when component is mounted
    onMounted(() => {
      loadAccounts();
    });

    return {
      accounts,
      selectedAccount,
      query,
      isLoading,
      filteredAccounts,
      handleSelect,
    };
  },
});
</script>
