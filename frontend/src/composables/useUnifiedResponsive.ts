import { ref, onMounted, onUnmounted, computed } from 'vue'

const breakpoints = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536
}

const windowWidth = ref(0)

export function useUnifiedResponsive() {
  const updateWidth = () => {
    windowWidth.value = window.innerWidth
  }

  onMounted(() => {
    updateWidth()
    window.addEventListener('resize', updateWidth)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', updateWidth)
  })

  const isMobile = computed(() => windowWidth.value < breakpoints.md)
  const isTablet = computed(() => windowWidth.value >= breakpoints.md && windowWidth.value < breakpoints.lg)
  const isDesktop = computed(() => windowWidth.value >= breakpoints.lg)
  
  const isSmallScreen = computed(() => windowWidth.value < breakpoints.sm)
  const isMediumScreen = computed(() => windowWidth.value >= breakpoints.sm && windowWidth.value < breakpoints.md)
  const isLargeScreen = computed(() => windowWidth.value >= breakpoints.md && windowWidth.value < breakpoints.lg)
  const isExtraLargeScreen = computed(() => windowWidth.value >= breakpoints.lg && windowWidth.value < breakpoints.xl)
  const is2ExtraLargeScreen = computed(() => windowWidth.value >= breakpoints.xl)

  const screenSize = computed(() => {
    if (windowWidth.value < breakpoints.sm) return 'xs'
    if (windowWidth.value < breakpoints.md) return 'sm'
    if (windowWidth.value < breakpoints.lg) return 'md'
    if (windowWidth.value < breakpoints.xl) return 'lg'
    if (windowWidth.value < breakpoints['2xl']) return 'xl'
    return '2xl'
  })

  const getColumnsForScreen = (columns: { xs?: number, sm?: number, md?: number, lg?: number, xl?: number, '2xl'?: number }) => {
    const size = screenSize.value
    return columns[size as keyof typeof columns] || columns.md || 1
  }

  return {
    windowWidth,
    isMobile,
    isTablet,
    isDesktop,
    isSmallScreen,
    isMediumScreen,
    isLargeScreen,
    isExtraLargeScreen,
    is2ExtraLargeScreen,
    screenSize,
    getColumnsForScreen,
    breakpoints
  }
}