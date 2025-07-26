/**
 * Input sanitization utilities for XSS prevention
 */

// HTML sanitization
export const sanitizeHtml = (input: string): string => {
  const div = document.createElement('div')
  div.textContent = input
  return div.innerHTML
}

// Remove script tags and event handlers
export const stripScripts = (input: string): string => {
  return input
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/on\w+="[^"]*"/gi, '')
    .replace(/on\w+='[^']*'/gi, '')
    .replace(/javascript:/gi, '')
}

// Sanitize for SQL-like inputs (additional layer)
export const sanitizeForDatabase = (input: string): string => {
  return input
    .replace(/'/g, "''")
    .replace(/;/g, '')
    .replace(/--/g, '')
    .replace(/\/\*/g, '')
    .replace(/\*\//g, '')
}

// File upload validation
export const validateFileUpload = (file: File): { valid: boolean; error?: string } => {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/csv']
  const maxSize = 10 * 1024 * 1024 // 10MB
  
  if (!allowedTypes.includes(file.type)) {
    return { valid: false, error: 'File type not allowed' }
  }
  
  if (file.size > maxSize) {
    return { valid: false, error: 'File size too large' }
  }
  
  // Check for suspicious file names
  if (/[<>:"/\\|?*]/.test(file.name)) {
    return { valid: false, error: 'Invalid file name' }
  }
  
  return { valid: true }
}

// Input validation for forms
export const validateInput = (input: string, type: 'email' | 'phone' | 'text' | 'number'): boolean => {
  switch (type) {
    case 'email':
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input)
    case 'phone':
      return /^[+]?[1-9]?[0-9]{7,15}$/.test(input)
    case 'number':
      return /^[0-9]+(\.[0-9]+)?$/.test(input)
    case 'text':
      return input.length > 0 && input.length < 1000
    default:
      return true
  }
}