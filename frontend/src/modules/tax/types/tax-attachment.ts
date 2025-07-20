export interface TaxAttachment {
  id: string;
  tax_return_id: string;
  filename: string;
  description: string;
  document_type: string;
  file_size: number;
  mime_type: string;
  created_at: string;
  updated_at: string;
  download_url?: string;
}

export interface CreateTaxAttachmentDto {
  file: File;
  description: string;
  document_type: string;
}

export interface UpdateTaxAttachmentDto {
  description?: string;
  document_type?: string;
}

export interface TaxAttachmentFilter {
  tax_return_id?: string;
  document_type?: string;
  start_date?: string;
  end_date?: string;
  search?: string;
}

export interface TaxAttachmentStats {
  total_size: number;
  total_files: number;
  by_type: Record<string, number>;
}

export interface DocumentTypeOption {
  label: string;
  value: string;
  icon: string;
  color: string;
}

export const DOCUMENT_TYPES: DocumentTypeOption[] = [
  { 
    label: 'Tax Return', 
    value: 'tax_return',
    icon: 'pi pi-file-pdf',
    color: 'var(--primary-color)'
  },
  { 
    label: 'Receipt', 
    value: 'receipt',
    icon: 'pi pi-receipt',
    color: 'var(--green-500)'
  },
  { 
    label: 'Invoice', 
    value: 'invoice',
    icon: 'pi pi-file-invoice',
    color: 'var(--blue-500)'
  },
  { 
    label: 'Statement', 
    value: 'statement',
    icon: 'pi pi-file-alt',
    color: 'var(--yellow-500)'
  },
  { 
    label: 'Correspondence', 
    value: 'correspondence',
    icon: 'pi pi-envelope',
    color: 'var(--purple-500)'
  },
  { 
    label: 'Other', 
    value: 'other',
    icon: 'pi pi-file',
    color: 'var(--gray-500)'
  }
];

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
export const ALLOWED_FILE_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'image/jpeg',
  'image/png',
  'image/gif'
];

export const ALLOWED_FILE_EXTENSIONS = [
  '.pdf',
  '.doc',
  '.docx',
  '.xls',
  '.xlsx',
  '.jpg',
  '.jpeg',
  '.png',
  '.gif'
];

export const FILE_TYPE_MAP: Record<string, { icon: string; color: string }> = {
  // PDF
  'application/pdf': { 
    icon: 'pi pi-file-pdf', 
    color: 'var(--red-500)' 
  },
  
  // Word
  'application/msword': { 
    icon: 'pi pi-file-word', 
    color: 'var(--blue-500)' 
  },
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': { 
    icon: 'pi pi-file-word', 
    color: 'var(--blue-500)' 
  },
  
  // Excel
  'application/vnd.ms-excel': { 
    icon: 'pi pi-file-excel', 
    color: 'var(--green-600)' 
  },
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': { 
    icon: 'pi pi-file-excel', 
    color: 'var(--green-600)' 
  },
  
  // Images
  'image/jpeg': { 
    icon: 'pi pi-image', 
    color: 'var(--purple-500)' 
  },
  'image/png': { 
    icon: 'pi pi-image', 
    color: 'var(--purple-500)' 
  },
  'image/gif': { 
    icon: 'pi pi-image', 
    color: 'var(--purple-500)' 
  },
  
  // Default
  'default': { 
    icon: 'pi pi-file', 
    color: 'var(--gray-500)' 
  }
};

export function getFileTypeInfo(mimeType: string) {
  return FILE_TYPE_MAP[mimeType] || FILE_TYPE_MAP['default'];
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function getFileExtension(filename: string): string {
  return filename.split('.').pop()?.toLowerCase() || '';
}

export function isFileTypeAllowed(filename: string): boolean {
  const ext = getFileExtension(filename);
  return ALLOWED_FILE_EXTENSIONS.includes('.' + ext);
}
