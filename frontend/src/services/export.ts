import { ref } from 'vue';
import { useToast } from 'vue-toastification';
import { formatCurrency, formatDate } from '@/utils/formatters';

interface ExportOptions {
  filename: string;
  data: any;
  insights?: any;
  format?: 'excel' | 'pdf' | 'text';
}

export const useExportService = () => {
  const toast = useToast();
  const loading = ref(false);

  const exportText = async (filename: string, content: string) => {
    try {
      loading.value = true;
      const blob = new Blob([content], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.success('Insights exported successfully');
    } catch (error) {
      toast.error('Failed to export insights');
      console.error('Error exporting text:', error);
    } finally {
      loading.value = false;
    }
  };

  const exportExcel = async (filename: string, data: any) => {
    try {
      loading.value = true;
      const formattedData = formatDataForExcel(data);
      const worksheet = XLSX.utils.json_to_sheet(formattedData);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Tax Analytics');
      
      const excelBuffer = XLSX.write(workbook, {
        bookType: 'xlsx',
        type: 'array',
      });

      const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${filename}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.success('Excel export completed successfully');
    } catch (error) {
      toast.error('Failed to export Excel file');
      console.error('Error exporting Excel:', error);
    } finally {
      loading.value = false;
    }
  };

  const exportPdf = async (filename: string, data: any) => {
    try {
      loading.value = true;
      const doc = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      // Add title
      doc.setFontSize(20);
      doc.text('Tax Analytics Report', 105, 20, { align: 'center' });

      // Add date
      doc.setFontSize(12);
      const currentDate = formatDate(new Date());
      doc.text(`Generated on: ${currentDate}`, 105, 30, { align: 'center' });

      // Add data tables
      const formattedData = formatDataForPdf(data);
      doc.autoTable({
        head: Object.keys(formattedData[0]).map(key => key.charAt(0).toUpperCase() + key.slice(1)),
        body: formattedData,
        startY: 40
      });

      // Save PDF
      doc.save(`${filename}.pdf`);
      toast.success('PDF export completed successfully');
    } catch (error) {
      toast.error('Failed to export PDF file');
      console.error('Error exporting PDF:', error);
    } finally {
      loading.value = false;
    }
  };

  const downloadReport = async (filename: string, data: any, insights: any) => {
    try {
      loading.value = true;
      const formattedData = formatDataForReport(data, insights);
      const doc = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      // Add title
      doc.setFontSize(20);
      doc.text('Tax Analytics Comprehensive Report', 105, 20, { align: 'center' });

      // Add insights
      doc.setFontSize(12);
      doc.text('AI Insights & Recommendations:', 20, 40);
      let y = 45;
      Object.entries(insights).forEach(([key, value]) => {
        doc.text(`${key.charAt(0).toUpperCase() + key.slice(1)}:`, 20, y);
        doc.text(value, 40, y);
        y += 10;
      });

      // Add data tables
      doc.autoTable({
        head: Object.keys(formattedData[0]).map(key => key.charAt(0).toUpperCase() + key.slice(1)),
        body: formattedData,
        startY: y + 10
      });

      // Save PDF
      doc.save(`${filename}_report.pdf`);
      toast.success('Comprehensive report exported successfully');
    } catch (error) {
      toast.error('Failed to export comprehensive report');
      console.error('Error exporting report:', error);
    } finally {
      loading.value = false;
    }
  };

  const formatDataForExcel = (data: any) => {
    return Object.entries(data).map(([key, value]) => ({
      [key]: typeof value === 'number' ? formatCurrency(value) : value
    }));
  };

  const formatDataForPdf = (data: any) => {
    return Object.entries(data).map(([key, value]) => ({
      [key]: typeof value === 'number' ? formatCurrency(value) : value
    }));
  };

  const formatDataForReport = (data: any, insights: any) => {
    return [
      ...Object.entries(data).map(([key, value]) => ({
        [key]: typeof value === 'number' ? formatCurrency(value) : value
      })),
      ...Object.entries(insights).map(([key, value]) => ({
        [key]: value
      }))
    ];
  };

  return {
    exportText,
    exportExcel,
    exportPdf,
    downloadReport,
    loading
  };
};
