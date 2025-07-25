import { computed } from 'vue'
import { useDisplay } from 'vuetify'

export function useResponsive() {
  const display = useDisplay()

  const isMobile = computed(() => display.mobile.value)
  const isTablet = computed(() => display.tablet.value)
  const isDesktop = computed(() => display.desktop.value)

  return {
    isMobile,
    isTablet,
    isDesktop
  }
}