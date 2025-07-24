import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useDisplay } from 'vuetify'

export function useResponsive() {
  const display = useDisplay()
  
  const breakpoints = computed(() => ({
    xs: display.xs.value,
    sm: display.sm.value,
    md: display.md.value,
    lg: display.lg.value,
    xl: display.xl.value,
    xxl: display.xxl.value
  }))

  const isMobile = computed(() => display.mobile.value)
  const isTablet = computed(() => display.tablet.value)
  const isDesktop = computed(() => display.desktop.value)

  const getResponsiveCols = (mobile = 12, tablet = 6, desktop = 4) => {
    if (isMobile.value) return mobile
    if (isTablet.value) return tablet
    return desktop
  }

  const getResponsiveClass = (mobileClass: string, tabletClass?: string, desktopClass?: string) => {
    if (isMobile.value) return mobileClass
    if (isTablet.value && tabletClass) return tabletClass
    if (desktopClass) return desktopClass
    return mobileClass
  }

  return {
    breakpoints,
    isMobile,
    isTablet,
    isDesktop,
    getResponsiveCols,
    getResponsiveClass
  }
}