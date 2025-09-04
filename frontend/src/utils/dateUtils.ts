// Utility functions for date handling

export const formatDateForDisplay = (date: string | Date | null | undefined): string => {
  if (!date) return '';
  try {
    const d = new Date(date);
    return isNaN(d.getTime()) ? '' : d.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  } catch (e) {
    console.error('Error formatting date:', e);
    return '';
  }
};
