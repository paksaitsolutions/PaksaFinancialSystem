import { useVendorsStore } from './vendors';
import { useInvoicesStore } from './invoices';
import { usePaymentsStore } from './payments';

export const useAPStore = () => {
  const vendors = useVendorsStore();
  const invoices = useInvoicesStore();
  const payments = usePaymentsStore();

  // Initialize all stores
  const initialize = async () => {
    await Promise.all([
      vendors.initialize(),
      invoices.initialize(),
      payments.initialize(),
    ]);
  };

  // Reset all stores
  const reset = () => {
    vendors.$reset();
    invoices.$reset();
    payments.$reset();
  };

  return {
    vendors,
    invoices,
    payments,
    initialize,
    reset,
  };
};

export type APStore = ReturnType<typeof useAPStore>;
