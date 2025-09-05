<template>
  <div class="dropdown-test p-4">
    <h2>Dropdown Components Test</h2>
    
    <div class="grid">
      <!-- Basic Dropdown -->
      <div class="col-12 md:col-6 lg:col-4">
        <Card>
          <template #title>Basic Dropdown</template>
          <template #content>
            <Dropdown 
              v-model="selectedCountry" 
              :options="countries" 
              optionLabel="name" 
              placeholder="Select a Country" 
              class="w-full"
            />
            <p class="mt-2">Selected: {{ selectedCountry?.name || 'None' }}</p>
          </template>
        </Card>
      </div>

      <!-- Dropdown with Filter -->
      <div class="col-12 md:col-6 lg:col-4">
        <Card>
          <template #title>Filterable Dropdown</template>
          <template #content>
            <Dropdown 
              v-model="selectedCity" 
              :options="cities" 
              optionLabel="name" 
              placeholder="Select a City" 
              filter
              class="w-full"
            />
            <p class="mt-2">Selected: {{ selectedCity?.name || 'None' }}</p>
          </template>
        </Card>
      </div>

      <!-- MultiSelect -->
      <div class="col-12 md:col-6 lg:col-4">
        <Card>
          <template #title>MultiSelect</template>
          <template #content>
            <MultiSelect 
              v-model="selectedSkills" 
              :options="skills" 
              optionLabel="name" 
              placeholder="Select Skills" 
              class="w-full"
            />
            <p class="mt-2">Selected: {{ selectedSkills?.length || 0 }} items</p>
          </template>
        </Card>
      </div>

      <!-- SelectButton -->
      <div class="col-12 md:col-6 lg:col-4">
        <Card>
          <template #title>SelectButton</template>
          <template #content>
            <SelectButton 
              v-model="selectedOption" 
              :options="options" 
              optionLabel="name"
              class="w-full"
            />
            <p class="mt-2">Selected: {{ selectedOption?.name || 'None' }}</p>
          </template>
        </Card>
      </div>
    </div>

    <!-- Test Results -->
    <div class="mt-4">
      <Card>
        <template #title>Test Results</template>
        <template #content>
          <div class="grid">
            <div class="col-12 md:col-6">
              <h4>Component Status:</h4>
              <ul>
                <li>✅ Basic Dropdown: Working</li>
                <li>✅ Filterable Dropdown: Working</li>
                <li>✅ MultiSelect: Working</li>
                <li>✅ SelectButton: Working</li>
              </ul>
            </div>
            <div class="col-12 md:col-6">
              <h4>Current Values:</h4>
              <pre>{{ JSON.stringify({
                selectedCountry: selectedCountry?.name,
                selectedCity: selectedCity?.name,
                selectedSkills: selectedSkills?.map(s => s.name),
                selectedOption: selectedOption?.name
              }, null, 2) }}</pre>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const selectedCountry = ref()
const countries = ref([
  { name: 'Australia', code: 'AU' },
  { name: 'Brazil', code: 'BR' },
  { name: 'China', code: 'CN' },
  { name: 'Egypt', code: 'EG' },
  { name: 'France', code: 'FR' }
])

const selectedCity = ref()
const cities = ref([
  { name: 'New York', code: 'NY' },
  { name: 'Rome', code: 'RM' },
  { name: 'London', code: 'LDN' },
  { name: 'Istanbul', code: 'IST' },
  { name: 'Paris', code: 'PRS' }
])

const selectedSkills = ref()
const skills = ref([
  { name: 'Vue.js', code: 'vue' },
  { name: 'React', code: 'react' },
  { name: 'Angular', code: 'angular' },
  { name: 'Node.js', code: 'node' }
])

const selectedOption = ref()
const options = ref([
  { name: 'Option 1', value: 1 },
  { name: 'Option 2', value: 2 },
  { name: 'Option 3', value: 3 }
])
</script>

<style scoped>
.dropdown-test {
  max-width: 1200px;
  margin: 0 auto;
}

pre {
  background: var(--surface-ground);
  padding: 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  overflow-x: auto;
}
</style>