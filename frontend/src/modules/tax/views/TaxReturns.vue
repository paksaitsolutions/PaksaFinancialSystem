<template>
  <div class="tax-returns">
    <router-view />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'TaxReturns',
  setup() {
    return {};
  }
});
</script>

<style scoped>
.tax-returns {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
