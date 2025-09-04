// Standard PrimeFlex classes for consistent layout across all views
export const STANDARD_CLASSES = {
  // Page layout
  PAGE_CONTAINER: 'p-4',
  PAGE_HEADER: 'flex justify-content-between align-items-center mb-4',
  PAGE_TITLE: 'text-3xl font-bold m-0',
  PAGE_SUBTITLE: 'text-color-secondary m-0 mt-2',
  
  // Grid layouts
  STATS_GRID: 'grid mb-4',
  STAT_CARD: 'col-12 md:col-6 lg:col-3',
  MAIN_GRID: 'grid',
  MAIN_CONTENT: 'col-12 lg:col-8',
  SIDEBAR_CONTENT: 'col-12 lg:col-4',
  FULL_WIDTH: 'col-12',
  
  // Form layouts
  FORM_GRID: 'grid',
  FORM_FIELD: 'col-12 md:col-6',
  FORM_FIELD_FULL: 'col-12',
  
  // Actions
  ACTION_BUTTONS: 'flex gap-2 justify-content-end mt-3',
  TABLE_ACTIONS: 'flex gap-2',
  HEADER_ACTIONS: 'flex gap-2',
  
  // Cards
  CARD_TITLE: 'flex align-items-center gap-2',
  CARD_TITLE_WITH_ACTION: 'flex justify-content-between align-items-center w-full',
  
  // Quick actions
  QUICK_ACTIONS_GRID: 'grid mb-4',
  QUICK_ACTION_ITEM: 'col-12 md:col-6 lg:col-2',
  
  // Responsive utilities
  RESPONSIVE_HIDE_MOBILE: 'hidden lg:block',
  RESPONSIVE_SHOW_MOBILE: 'block lg:hidden'
}

// Standard component templates
export const STANDARD_TEMPLATES = {
  PAGE_HEADER: (title, subtitle, actions = '') => `
    <div class="${STANDARD_CLASSES.PAGE_HEADER}">
      <div>
        <h1 class="${STANDARD_CLASSES.PAGE_TITLE}">${title}</h1>
        ${subtitle ? `<p class="${STANDARD_CLASSES.PAGE_SUBTITLE}">${subtitle}</p>` : ''}
      </div>
      ${actions ? `<div class="${STANDARD_CLASSES.HEADER_ACTIONS}">${actions}</div>` : ''}
    </div>
  `,
  
  STAT_CARD: (icon, title, value, color = 'blue') => `
    <div class="${STANDARD_CLASSES.STAT_CARD}">
      <Card>
        <template #content>
          <div class="flex justify-content-between align-items-center">
            <div>
              <div class="text-2xl font-bold text-${color}-500">${value}</div>
              <div class="text-color-secondary text-sm">${title}</div>
            </div>
            <i class="${icon} text-3xl text-${color}-500"></i>
          </div>
        </template>
      </Card>
    </div>
  `
}