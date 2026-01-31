
export function useFormatting() {
  const formatCurrency = (value: number | string): string => {
    if (value === null || value === undefined) return '';
    
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(numValue)) return '';
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(numValue);
  };

  const formatDate = (date: Date | string | null | undefined): string => {
    if (!date) return '';
    
    const dateObj = date instanceof Date ? date : new Date(date);
    if (isNaN(dateObj.getTime())) return '';
    
    return dateObj.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatPercentage = (value: number | string, decimals: number = 2): string => {
    if (value === null || value === undefined) return '';
    
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(numValue)) return '';
    
    return `${numValue.toFixed(decimals)}%`;
  };

  const formatNumber = (value: number | string, decimals: number = 2): string => {
    if (value === null || value === undefined) return '';
    
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(numValue)) return '';
    
    return numValue.toLocaleString('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: decimals,
    });
  };

  const getStatusVariant = (status: string) => {
    const statusMap: Record<string, string> = {
      'active': 'success',
      'inactive': 'danger',
      'pending': 'warning',
      'approved': 'success',
      'rejected': 'danger',
      'draft': 'info',
      'paid': 'success',
      'unpaid': 'danger',
      'overdue': 'danger',
      'partially_paid': 'warning',
    };
    
    return statusMap[status.toLowerCase()] || 'secondary';
  };

  return {
    formatCurrency,
    formatDate,
    formatPercentage,
    formatNumber,
    getStatusVariant,
  };
}

export default useFormatting;
