import { ref, onMounted, watch } from 'vue';

// Constants
const THEME_STORAGE_KEY = 'paksa_theme_preference';
const THEME_DARK = 'dark';
const THEME_LIGHT = 'light';

// State
const isDark = ref<boolean>(false);

// Check system preference for dark mode
const getSystemPreference = (): boolean => {
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
};

// Apply theme class to document element
const applyTheme = (dark: boolean): void => {
  if (dark) {
    document.documentElement.classList.add('dark-theme');
    document.documentElement.setAttribute('data-theme', THEME_DARK);
  } else {
    document.documentElement.classList.remove('dark-theme');
    document.documentElement.setAttribute('data-theme', THEME_LIGHT);
  }
};

// Save theme preference to localStorage
const savePreference = (dark: boolean): void => {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, dark ? THEME_DARK : THEME_LIGHT);
  } catch (e) {
    console.warn('Failed to save theme preference to localStorage', e);
  }
};

export function useTheme() {
  // Initialize theme from localStorage or system preference
  const initTheme = (): void => {
    // Check for saved preference first
    const savedPreference = localStorage.getItem(THEME_STORAGE_KEY);
    
    if (savedPreference) {
      isDark.value = savedPreference === THEME_DARK;
    } else {
      // No saved preference, use system preference
      isDark.value = getSystemPreference();
    }
    
    // Apply the theme
    applyTheme(isDark.value);
  };
  
  // Toggle between light and dark theme
  const toggleTheme = (): void => {
    isDark.value = !isDark.value;
    savePreference(isDark.value);
    applyTheme(isDark.value);
  };
  
  // Set theme explicitly
  const setTheme = (dark: boolean): void => {
    isDark.value = dark;
    savePreference(dark);
    applyTheme(dark);
  };
  
  // Watch for system preference changes (only if no explicit preference is set)
  const watchSystemPreference = (): (() => void) => {
    if (localStorage.getItem(THEME_STORAGE_KEY)) {
      // User has set a preference, don't respond to system changes
      return () => {};
    }
    
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      setTheme(e.matches);
    };
    
    // Add event listener for future changes
    mediaQuery.addEventListener('change', handleChange);
    
    // Return cleanup function
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  };
  
  // Initialize theme when component mounts
  onMounted(() => {
    initTheme();
    const cleanup = watchSystemPreference();
    
    // Clean up event listener when component unmounts
    return () => {
      cleanup();
    };
  });
  
  // Watch for changes to isDark and apply theme
  watch(isDark, (newVal) => {
    applyTheme(newVal);
  });

  return {
    isDarkMode: isDark,
    toggleTheme,
    setTheme,
    currentTheme: () => isDark.value ? THEME_DARK : THEME_LIGHT
  };
}