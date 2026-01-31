<template>
  <div class="language-switcher">
    <Dropdown
      v-model="currentLanguage"
      :options="availableLanguages"
      option-label="name"
      option-value="code"
      :pt="{
        root: { class: 'language-dropdown' },
        input: { class: 'language-input' },
        item: { class: 'language-item' },
        panel: { class: 'language-panel' }
      }"
      @change="onLanguageChange"
    >
      <template #value="slotProps: { value: string }">
        <div v-if="slotProps.value" class="flex align-items-center gap-2">
          <span :class="`fi fi-${getFlagCode(slotProps.value)}`" style="font-size: 1.2rem"></span>
          <span class="language-code">{{ slotProps.value.toUpperCase() }}</span>
        </div>
      </template>
      <template #option="slotProps: { option: { code: string; name: string } }">
        <div class="flex align-items-center gap-2">
          <span :class="`fi fi-${getFlagCode(slotProps.option.code)}`" style="font-size: 1.2rem"></span>
          <span>{{ slotProps.option.name }}</span>
        </div>
      </template>
    </Dropdown>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAppStore } from '@/store/app';

interface LanguageOption {
  code: string;
  name: string;
}

const { locale } = useI18n();
const appStore = useAppStore();

const currentLanguage = ref<string>(locale.value);
const availableLanguages = ref<LanguageOption[]>([
  { code: 'en', name: 'English' },
  { code: 'ar', name: 'العربية' },
  { code: 'ur', name: 'اردو' }
]);

// Map language codes to country codes for flag display
const getFlagCode = (langCode: string): string => {
  const flagMap: Record<string, string> = {
    en: 'us',
    ar: 'sa',
    ur: 'pk'
  };
  return flagMap[langCode] || langCode;
};

const onLanguageChange = (event: { value: string }): void => {
  if (event && event.value) {
    locale.value = event.value;
    appStore.setLocale(event.value);
    document.documentElement.lang = event.value;
    // You might want to reload the page or update the app's language here
  }
};

// Initialize from app store
onMounted((): void => {
  if (appStore.currentLocale) {
    currentLanguage.value = appStore.currentLocale;
  }
});
</script>

<style scoped>
.language-switcher {
  min-width: 120px;
}

:deep(.language-dropdown) {
  border: none;
  background: transparent;
  box-shadow: none;
}

:deep(.language-input) {
  padding: 0.5rem;
  background: transparent;
  border: none;
  color: var(--text-color);
}

:deep(.language-panel) {
  min-width: 140px;
}

:deep(.language-item) {
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.language-code {
  font-weight: 600;
}
</style>
