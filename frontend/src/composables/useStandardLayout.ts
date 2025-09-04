export const useStandardLayout = () => {
  const getPageHeaderClass = () => 'flex justify-content-between align-items-center mb-4'
  
  const getStatsGridClass = () => 'grid'
  
  const getStatCardClass = () => 'col-12 md:col-6 lg:col-3'
  
  const getMainContentClass = () => 'grid'
  
  const getContentCardClass = () => 'col-12'
  
  const getSidebarCardClass = () => 'col-12 lg:col-4'
  
  const getMainCardClass = () => 'col-12 lg:col-8'
  
  const getFormGridClass = () => 'grid'
  
  const getFormFieldClass = () => 'col-12 md:col-6'
  
  const getFullWidthFieldClass = () => 'col-12'
  
  const getActionButtonsClass = () => 'flex gap-2 justify-content-end mt-3'
  
  const getTableActionsClass = () => 'flex gap-2'
  
  return {
    getPageHeaderClass,
    getStatsGridClass,
    getStatCardClass,
    getMainContentClass,
    getContentCardClass,
    getSidebarCardClass,
    getMainCardClass,
    getFormGridClass,
    getFormFieldClass,
    getFullWidthFieldClass,
    getActionButtonsClass,
    getTableActionsClass
  }
}