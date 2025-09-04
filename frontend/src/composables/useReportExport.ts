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
    const content = `${title}\nGenerated on: ${new Date().toLocaleDateString()}\n\n${JSON.stringify(data, null, 2)}`
    downloadFile(content, `${filename}.pdf`, 'text/plain')
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
      label: 'Export to PDF',
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