export const useReportExport = () => {
  const downloadFile = (content: string, filename: string, type: string) => {
    const element = document.createElement('a')
    const file = new Blob([content], { type })
    element.href = URL.createObjectURL(file)
    element.download = filename
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const exportToCSV = (data: any[], filename: string) => {
    const headers = Object.keys(data[0]).join(',')
    const rows = data.map(row => Object.values(row).join(','))
    const csv = [headers, ...rows].join('\n')
    downloadFile(csv, `${filename}.csv`, 'text/csv')
  }

  const exportToPDF = (title: string, data: any[], filename: string) => {
    // Create HTML content for PDF
    const headers = Object.keys(data[0])
    const htmlContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <title>${title}</title>
          <style>
            body { 
              font-family: Arial, sans-serif; 
              margin: 20px; 
              font-size: 12px;
            }
            .header {
              text-align: center;
              margin-bottom: 30px;
              border-bottom: 2px solid #333;
              padding-bottom: 10px;
            }
            .company-name {
              font-size: 18px;
              font-weight: bold;
              margin-bottom: 5px;
            }
            .report-title {
              font-size: 16px;
              font-weight: bold;
              margin-bottom: 5px;
            }
            .report-date {
              font-size: 12px;
              color: #666;
            }
            table { 
              width: 100%; 
              border-collapse: collapse; 
              margin-top: 20px;
            }
            th, td { 
              border: 1px solid #ddd; 
              padding: 8px; 
              text-align: left;
            }
            th { 
              background-color: #f8f9fa; 
              font-weight: bold;
            }
            .section-header {
              background-color: #e9ecef;
              font-weight: bold;
            }
            .amount {
              text-align: right;
            }
            .total-row {
              font-weight: bold;
              border-top: 2px solid #333;
            }
            @media print {
              body { margin: 0; }
              .no-print { display: none; }
            }
          </style>
        </head>
        <body>
          <div class="header">
            <div class="company-name">Paksa Financial System</div>
            <div class="report-title">${title}</div>
            <div class="report-date">Generated on: ${new Date().toLocaleDateString()}</div>
          </div>
          <table>
            <thead>
              <tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>
            </thead>
            <tbody>
              ${data.map(row => {
                const isTotal = row.Account && (row.Account.includes('TOTAL') || row.Account.includes('Total'));
                const isSection = row.Section && !row.Account;
                const cssClass = isTotal ? 'total-row' : (isSection ? 'section-header' : '');
                return `<tr class="${cssClass}">${Object.values(row).map((v, i) => {
                  const isAmountColumn = headers[i] === 'Amount';
                  return `<td class="${isAmountColumn ? 'amount' : ''}">${v || ''}</td>`;
                }).join('')}</tr>`;
              }).join('')}
            </tbody>
          </table>
        </body>
      </html>
    `
    
    // Open in new window for printing to PDF
    const printWindow = window.open('', '_blank')
    if (printWindow) {
      printWindow.document.write(htmlContent)
      printWindow.document.close()
      
      // Wait for content to load then trigger print dialog
      printWindow.onload = () => {
        setTimeout(() => {
          printWindow.print()
        }, 500)
      }
    }
  }

  const printReport = (title: string, data: any[]) => {
    const headers = Object.keys(data[0])
    const content = `
      <html>
        <head>
          <title>${title}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
          </style>
        </head>
        <body>
          <h1>${title}</h1>
          <p>Generated on: ${new Date().toLocaleDateString()}</p>
          <table>
            <thead>
              <tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>
            </thead>
            <tbody>
              ${data.map(row => `<tr>${Object.values(row).map(v => `<td>${v}</td>`).join('')}</tr>`).join('')}
            </tbody>
          </table>
        </body>
      </html>
    `
    
    const printWindow = window.open('', '_blank')
    if (printWindow) {
      printWindow.document.write(content)
      printWindow.document.close()
      printWindow.print()
    }
  }

  const getExportOptions = (title: string, data: any[], filename: string) => [
    {
      label: 'Print to PDF',
      icon: 'pi pi-file-pdf',
      command: () => exportToPDF(title, data, filename)
    },
    {
      label: 'Export to Excel',
      icon: 'pi pi-file-excel',
      command: () => exportToCSV(data, filename)
    }
  ]

  return {
    exportToCSV,
    exportToPDF,
    printReport,
    getExportOptions
  }
}