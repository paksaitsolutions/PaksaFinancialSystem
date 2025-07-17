<template>
  <div class="currency-selector">
    <div class="flex items-center">
      <span class="mr-2 text-sm font-medium text-gray-700">{{ label }}</span>
      <div class="relative">
        <button
          type="button"
          class="relative w-full bg-white border border-gray-300 rounded-md shadow-sm pl-3 pr-10 py-2 text-left cursor-default focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          @click="isOpen = !isOpen"
          @blur="handleBlur"
          :aria-expanded="isOpen"
          aria-haspopup="listbox"
        >
          <span class="flex items-center">
            <span class="fi" :class="selectedCurrency.flag" :title="selectedCurrency.name"></span>
            <span class="ml-2 block truncate">
              {{ selectedCurrency.code }} - {{ selectedCurrency.symbol }}
            </span>
          </span>
          <span class="ml-3 absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M10 3a1 1 0 01.707.293l3 3a1 1 0 01-1.414 1.414L10 5.414 7.707 7.707a1 1 0 01-1.414-1.414l3-3A1 1 0 0110 3zm-3.707 9.293a1 1 0 011.414 0L10 14.586l2.293-2.293a1 1 0 011.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </span>
        </button>

        <transition
          enter-active-class="transition ease-out duration-100"
          enter-class="transform opacity-0 scale-95"
          enter-to-class="transform opacity-100 scale-100"
          leave-active-class="transition ease-in duration-75"
          leave-class="transform opacity-100 scale-100"
          leave-to-class="transform opacity-0 scale-95"
        >
          <ul
            v-show="isOpen"
            class="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-56 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm"
            tabindex="-1"
            role="listbox"
            aria-labelledby="listbox-label"
            aria-activedescendant="listbox-option-0"
          >
            <li
              v-for="(currency, index) in currencies"
              :key="currency.code"
              :id="`listbox-option-${index}`"
              class="text-gray-900 cursor-default select-none relative py-2 pl-3 pr-9 hover:bg-gray-50"
              role="option"
              @mousedown="selectCurrency(currency)"
            >
              <div class="flex items-center">
                <span class="fi" :class="currency.flag" :title="currency.name"></span>
                <span class="font-normal ml-3 block truncate">
                  {{ currency.name }} ({{ currency.code }})
                </span>
                <span class="text-gray-500 ml-2">{{ currency.symbol }}</span>
              </div>
              <span
                v-if="currency.code === modelValue"
                class="text-primary-600 absolute inset-y-0 right-0 flex items-center pr-4"
              >
                <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
            </li>
          </ul>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';

interface Currency {
  code: string;
  name: string;
  symbol: string;
  flag: string;
  decimalDigits: number;
  decimalSeparator: string;
  thousandsSeparator: string;
  symbolOnLeft: boolean;
  spaceBetweenAmountAndSymbol: boolean;
}

const props = defineProps({
  modelValue: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: 'Currency'
  },
  showSymbol: {
    type: Boolean,
    default: true
  },
  showFlag: {
    type: Boolean,
    default: true
  },
  showCode: {
    type: Boolean,
    default: true
  },
  showName: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  currencies: {
    type: Array as () => Currency[],
    default: () => [
      {
        code: 'USD',
        name: 'US Dollar',
        symbol: '$',
        flag: 'fi-us',
        decimalDigits: 2,
        decimalSeparator: '.',
        thousandsSeparator: ',',
        symbolOnLeft: true,
        spaceBetweenAmountAndSymbol: false
      },
      {
        code: 'EUR',
        name: 'Euro',
        symbol: '€',
        flag: 'fi-eu',
        decimalDigits: 2,
        decimalSeparator: ',',
        thousandsSeparator: '.',
        symbolOnLeft: false,
        spaceBetweenAmountAndSymbol: true
      },
      {
        code: 'GBP',
        name: 'British Pound',
        symbol: '£',
        flag: 'fi-gb',
        decimalDigits: 2,
        decimalSeparator: '.',
        thousandsSeparator: ',',
        symbolOnLeft: true,
        spaceBetweenAmountAndSymbol: false
      },
      {
        code: 'PKR',
        name: 'Pakistani Rupee',
        symbol: '₨',
        flag: 'fi-pk',
        decimalDigits: 0,
        decimalSeparator: '.',
        thousandsSeparator: ',',
        symbolOnLeft: true,
        spaceBetweenAmountAndSymbol: false
      },
      {
        code: 'SAR',
        name: 'Saudi Riyal',
        symbol: '﷼',
        flag: 'fi-sa',
        decimalDigits: 2,
        decimalSeparator: '.',
        thousandsSeparator: ',',
        symbolOnLeft: true,
        spaceBetweenAmountAndSymbol: true
      },
      {
        code: 'AED',
        name: 'UAE Dirham',
        symbol: 'د.إ',
        flag: 'fi-ae',
        decimalDigits: 2,
        decimalSeparator: '.',
        thousandsSeparator: ',',
        symbolOnLeft: true,
        spaceBetweenAmountAndSymbol: true
      }
    ]
  }
});

const emit = defineEmits(['update:modelValue', 'change']);

const isOpen = ref(false);

const selectedCurrency = computed(() => {
  return props.currencies.find(c => c.code === props.modelValue) || props.currencies[0];
});

const selectCurrency = (currency: Currency) => {
  emit('update:modelValue', currency.code);
  emit('change', currency);
  isOpen.value = false;
};

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  if (!target.closest('.currency-selector')) {
    isOpen.value = false;
  }
};

const handleBlur = () => {
  // Use setTimeout to allow click events to fire on options
  setTimeout(() => {
    isOpen.value = false;
  }, 200);
};

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside);
});
</script>

<style scoped>
/* Flag Icons CSS */
.fi {
  display: inline-block;
  width: 1.33333333em;
  height: 1em;
  background-size: contain;
  background-position: 50%;
  background-repeat: no-repeat;
  position: relative;
  top: 0.1em;
  line-height: 1em;
  border-radius: 2px;
  box-shadow: 0 0 1px rgba(0, 0, 0, 0.5);
}

.fi-us { background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMjAwIDYwMCI+PHBhdGggZmlsbD0iMDAyMTQ4IiBkPSJNODAwIDBINDB2NjAwaDc2MHYtNjB6Ii8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTAgMGgxMjAwdjYwSDB6Ii8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTAgMTIwaDEyMDB2NjBIMHoiLz48cGF0aCBmaWxsPSIjZmZmIiBkPSJNMCAyNDBoMTIwMHY2MEgweiIvPjxwYXRoIGZpbGw9IiNmZmYiIGQ9Ik0wIDM2MGgxMjAwdjYwSDB6Ii8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTAgNDgwaDEyMDB2NjBIMHoiLz48cGF0aCBmaWxsPSIjZTUwMDAwIiBkPSJNMCA2MGgxMjAwdjYwSDB6Ii8+PHBhdGggZmlsbD0iI2U1MDAwMCIgZD0iTTAgMTgwaDEyMDB2NjBIMHoiLz48cGF0aCBmaWxsPSIjZTUwMDAwIiBkPSJNMCAzMDBoMTIwMHY2MEgweiIvPjxwYXRoIGZpbGw9IiNlNTAwMDAiIGQ9Ik0wIDQyMGgxMjAwdjYwSDB6Ii8+PHBhdGggZmlsbD0iIzAwMUg5OSIgZD0iTTAgMGg0ODB2MzYwSDB6Ii8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTE4MCAwYy0xOS44ODIgMzUuNzctMzIgNzcuNDI1LTMyIDEyMiAwIDQ0LjU3NSAxMi4xMTggODYuMjMgMzIgMTIybDYwLTYwYy0xOS43NjQtMjMuNTMtMzAtNTIuNDUtMzAtNjIgMC05LjU1IDEwLjIzNi0zOC40NyAzMC02MnoiLz48cGF0aCBmaWxsPSIjMDAxSDk5IiBkPSJNMTgwIDB2NjBoMzAwVjB6Ii8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTI0MCAwYy0xOS44ODIgMzUuNzctMzIgNzcuNDI1LTMyIDEyMiAwIDQ0LjU3NSAxMi4xMTggODYuMjMgMzIgMTIybDYwLTYwYy0xOS43NjQtMjMuNTMtMzAtNTIuNDUtMzAtNjIgMC05LjU1IDEwLjIzNi0zOC40NyAzMC02MnoiLz48cGF0aCBmaWxsPSIjMDAxSDk5IiBkPSJNMjQwIDB2NjBoMzAwVjB6Ii8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTEyMCA2MGMtMTkuODgyIDM1Ljc3LTMyIDc3LjQyNS0zMiAxMjIgMCA0NC41NzUgMTIuMTE4IDg2LjIzIDMyIDEyMmw2MC02MGMtMTkuNzY0LTIzLjUzLTMwLTUyLjQ1LTMwLTYyIDAtOS41NSAxMC4yMzYtMzguNDcgMzAtNjJ6Ii8+PHBhdGggZmlsbD0iIzAwMUg5OSIgZD0iTTEyMCA2MHY2MGgzMDBWNjB6Ii8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTQ4MCAwYy0xOS44ODIgMzUuNzctMzIgNzcuNDI1LTMyIDEyMiAwIDQ0LjU3NSAxMi4xMTggODYuMjMgMzIgMTIybDYwLTYwYy0xOS43NjQtMjMuNTMtMzAtNTIuNDUtMzAtNjIgMC05LjU1IDEwLjIzNi0zOC40NyAzMC02MnoiLz48cGF0aCBmaWxsPSIjMDAxSDk5IiBkPSJNNDgwIDB2NjBoMzAwVjB6Ii8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTMwMCAwYy0xOS44ODIgMzUuNzctMzIgNzcuNDI1LTMyIDEyMiAwIDQ0LjU3NSAxMi4xMTggODYuMjMgMzIgMTIybDYwLTYwYy0xOS43NjQtMjMuNTMtMzAtNTIuNDUtMzAtNjIgMC05LjU1IDEwLjIzNi0zOC40NyAzMC02MnoiLz48cGF0aCBmaWxsPSIjMDAxSDk5IiBkPSJNMzAwIDB2NjBoMzAwVjB6Ii8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTM2MCA2MGMtMTkuODgyIDM1Ljc3LTMyIDc3LjQyNS0zMiAxMjIgMCA0NC41NzUgMTIuMTE4IDg2LjIzIDMyIDEyMmw2MC02MGMtMTkuNzY0LTIzLjUzLTMwLTUyLjQ1LTMwLTYyIDAtOS41NSAxMC4yMzYtMzguNDcgMzAtNjJ6Ii8+PHBhdGggZmlsbD0iIzAwMUg5OSIgZD0iTTM2MCA2MHY2MGgzMDBWNjB6Ii8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTQyMCA2MGMtMTkuODgyIDM1Ljc3LTMyIDc3LjQyNS0zMiAxMjIgMCA0NC41NzUgMTIuMTE4IDg2LjIzIDMyIDEyMmw2MC02MGMtMTkuNzY0LTIzLjUzLTMwLTUyLjQ1LTMwLTYyIDAtOS41NSAxMC4yMzYtMzguNDcgMzAtNjJ6Ii8+PHBhdGggZmlsbD0iIzAwMUg5OSIgZD0iTTQyMCA2MHY2MGgzMDBWNjB6Ii8+PC9zdmc+'); }
.fi-eu { background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA1MTIgNTEyIj48cGF0aCBmaWxsPSIjMDAzM2E5IiBkPSJNMjU2IDBDMTE0LjYgMCAwIDExNC42IDAgMjU2czExNC42IDI1NiAyNTYgMjU2IDI1Ni0xMTQuNiAyNTYtMjU2UzM5Ny40IDAgMjU2IDB6Ii8+PHBhdGggZmlsbD0iI2ZmZGRjYyIgZD0iTTI1NiA0NS4zYzExNi4zIDAgMjEwLjcgOTQuNCAyMTAuNyAyMTAuN1MzNzIuMyA0NjYuNyAyNTYgNDY2LjdTNDUuMyAzNzIuMyA0NS4zIDI1NiAxMzkuNyA0NS4zIDI1NiA0NS4zeiIvPjxwYXRoIGZpbGw9IiNGRjAwMDAiIGQ9Ik0yNTYgNjRjLTEwNi4xIDAtMTkyIDg1LjktMTkyIDE5MnM4NS45IDE5MiAxOTIgMTkyYzAgMTA2LjEgODUuOSAxOTIgMTkyIDE5MnMxOTItODUuOSAxOTItMTkyYzAtMTA2LjEtODUuOS0xOTItMTkyLTE5MnoiLz48cGF0aCBmaWxsPSIjRkZGRkZGIiBkPSJNMjU2IDk2Yy04OC40IDAtMTYwIDcxLjYtMTYwIDE2MHM3MS42IDE2MCAxNjAgMTYwYzAgODguNC03MS42IDE2MC0xNjAgMTYwUzk2IDMwNC40IDk2IDIxNnM3MS42LTE2MCAxNjAtMTYweiIvPjxwYXRoIGZpbGw9IiNGRjAwMDAiIGQ9Ik0yNTYgMTI4Yy00OC41IDAtODggMzkuNS04OCA4OHMzOS41IDg4IDg4IDg4YzAgNDguNS0zOS41IDg4LTg4IDg4cy04OC0zOS41LTg4LTg4czM5LjUtODggODgtODh6Ii8+PHBhdGggZmlsbD0iI0ZGQ0MwMCIgZD0iTTI1NiAxNjBjLTMwLjkgMC01NiAyNS4xLTU2IDU2czI1LjEgNTYgNTYgNTZzNTYtMjUuMSA1Ni01NnMtMjUuMS01Ni01Ni01NnoiLz48L3N2Zz4='); }
.fi-gb { background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA2MDAgMzAwIj48cGF0aCBmaWxsPSIjMDAyNDdCIiBkPSJNNTk5LjkgMEgwdjMwMGg2MDBWMEg1OTkuOXoiLz48cGF0aCBmaWxsPSIjRkZGIiBkPSJNNTk5LjkgMEgwdjMzLjN2NjYuN3Y2Ni43djY2Ljd2NjYuNmg2MDB2LTY2LjZ2LTY2Ljd2LTY2LjdWMzMuM1YwSDU5OS45eiIvPjxwYXRoIGZpbGw9IiNDRDAwMDAiIGQ9Ik0wIDIwMGg2MDB2LTY2LjdIMHY2Ni43em0wLTEzMy4zaDYwMFYwaC02MDB2NjYuN3oiLz48cGF0aCBmaWxsPSIjRkZGIiBkPSJNMTY2LjcgNjYuN2g2Ni43djY2LjdoLTY2LjdWNjYuN3ptLTY2LjcgMGg2Ni43djY2LjdoLTY2LjdWNjYuN3ptMTMzLjMgMGg2Ni43djY2LjdoLTY2LjdWNjYuN3ptNjYuNy02Ni43aDY2Ljd2NjYuN2gtNjYuN1Ywem0xMzMuMyAwaDY2Ljd2NjYuN2gtNjYuN1Ywem0xMzMuMyAwaDY2Ljd2NjYuN2gtNjYuN1Ywem00MDAgNjYuN2g2Ni43djY2LjdoLTY2LjdWNjYuN3ptMCAxMzMuM2g2Ni43djY2LjdoLTY2Ljd2LTY2LjdNNTk5LjkgNjYuN2g2Ni43djY2LjdoLTY2LjdWNjYuN3oiLz48L3N2Zz4='); }
.fi-pk { background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5MDAgNjAwIj48cGF0aCBmaWxsPSIjMDE0NzExIiBkPSJNNjAgMGg4NDB2NjBINjB6Ii8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTYwIDYwaDg0MHY0ODBINjB6Ii8+PHBhdGggZmlsbD0iIzAwNDAxMCIgZD0iTTYwIDU0MGg4NDB2NjBINjB6Ii8+PHBhdGggZmlsbD0iIzAwNDAxMCIgZD0iTTQyMCAzMDBhNjAgNjAgMCAxIDAgMTIwIDAgNjAgNjAgMCAxIDAtMTIwIDB6Ii8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTQ4MCAzMDBhNjAgNjAgMCAxIDAtMTIwIDAgNjAgNjAgMCAwIDAgMTIwIDB6Ii8+PHBhdGggZmlsbD0iIzAwNDAxMCIgZD0iTTQzOCAzMDBhMzggMzggMCAxIDAgNzYgMCAzOCAzOCAwIDEgMC03NiAwIi8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTQ0OCAzMDBhMjggMjggMCAxIDAtNTYgMCAyOCAyOCAwIDEgMCA1NiAwIi8+PHBhdGggZmlsbD0iIzAwNDAxMCIgZD0iTTQ1OCAzMDBhMTggMTggMCAxIDAtMzYgMCAxOCAxOCAwIDEgMCAzNiAwIi8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTQ2OCAzMDBhOCA4IDAgMSAwLTE2IDAgOCA4IDAgMSAwIDE2IDAiLz48cGF0aCBmaWxsPSIjMDA0MDEwIiBkPSJNNDAwIDI0MGg0MHYxMjBoLTQweiIvPjxwYXRoIGZpbGw9IiMwMDQwMTAiIGQ9Ik00MjAgMjYwbDIwIDQwLTIwIDQwLTIwLTQweiIvPjwvc3ZnPg=='); }
.fi-sa { background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5MDAgNjAwIj48cGF0aCBmaWxsPSIjMDA2NjAwIiBkPSJNMC0wLjF2NjAwaDkwMFYtMC4xSDB6Ii8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTAg0Jg0JjAgNjYuMyA1My43IDEyMCAxMjAgMTIwczEyMC01My43IDEyMC0xMjBTMTg2LjMgMCAxMjAgMCAwIDUzLjcgMCAxMjB6Ii8+PHBhdGggZD0iTTE1MCAxMjBjMCAxNi41IDEzLjUgMzAgMzAgMzBzMzAtMTMuNSAzMC0zMC0xMy41LTMwLTMwLTMwLTMwIDEzLjUtMzAgMzB6Ii8+PHBhdGggZmlsbD0iIzAwNjYwMCIgZD0iTTE4MCAxMjBjMCAxNi41LTEzLjUgMzAtMzAgMzBzLTMwLTEzLjUtMzAtMzAgMTMuNS0zMCAzMC0zMCAzMCAxMy41IDMwIDN6Ii8+PC9zdmc+'); }
.fi-ae { background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5MDAgNjAwIj48cGF0aCBmaWxsPSIjMDA3MkM0IiBkPSJNMC0wLjF2NjAwaDkwMFYtMC4xSDB6Ii8+PHBhdGggZmlsbD0iI0ZGRiIgZD0iTTAgMjAwaDkwMHYyMDBIMHoiLz48cGF0aCBmaWxsPSIjMDA5NjM5IiBkPSJNMC0wLjFoMzAwdjYwMEgweiIvPjxwYXRoIGZpbGw9IiNGRkYiIGQ9Ik0yMDAgMTYwYzAgMjIuMS0xNy45IDQwLTQwIDQwcy00MC0xNy45LTQwLTQwIDE3LjktNDAgNDAtNDAgNDAgMTcuOSA0MCA0MHoiLz48L3N2Zz4='); }
</style>
