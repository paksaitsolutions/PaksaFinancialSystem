import { format, parseISO, isValid, parse, addDays, addMonths, addYears, differenceInDays, differenceInMonths, differenceInYears } from 'date-fns';

type DateInput = Date | string | number;

/**
 * Format a date to a string using the specified format
 * @param date - Date to format (Date, ISO string, or timestamp)
 * @param formatStr - Format string (default: 'yyyy-MM-dd')
 * @returns Formatted date string
 */
export const formatDate = (date: DateInput, formatStr = 'yyyy-MM-dd'): string => {
  if (!date) return '';
  
  let dateObj: Date;
  
  if (typeof date === 'string') {
    // Try to parse ISO string first
    dateObj = parseISO(date);
    
    // If not a valid date, try parsing with the provided format
    if (!isValid(dateObj) && formatStr) {
      dateObj = parse(date, formatStr, new Date());
    }
  } else if (typeof date === 'number') {
    dateObj = new Date(date);
  } else {
    dateObj = date;
  }
  
  return isValid(dateObj) ? format(dateObj, formatStr) : '';
};

/**
 * Format a date to a human-readable relative time string (e.g., "2 days ago")
 * @param date - Date to format
 * @returns Relative time string
 */
export const formatRelativeTime = (date: DateInput): string => {
  if (!date) return '';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  
  const diffInDays = differenceInDays(now, dateObj);
  
  if (diffInDays === 0) return 'Today';
  if (diffInDays === 1) return 'Yesterday';
  if (diffInDays < 7) return `${diffInDays} days ago`;
  
  const diffInWeeks = Math.floor(diffInDays / 7);
  if (diffInWeeks === 1) return '1 week ago';
  if (diffInWeeks < 4) return `${diffInWeeks} weeks ago`;
  
  const diffInMonths = differenceInMonths(now, dateObj);
  if (diffInMonths === 1) return '1 month ago';
  if (diffInMonths < 12) return `${diffInMonths} months ago`;
  
  const diffInYears = differenceInYears(now, dateObj);
  return diffInYears === 1 ? '1 year ago' : `${diffInYears} years ago`;
};

/**
 * Add days to a date
 * @param date - Base date
 * @param days - Number of days to add (can be negative)
 * @returns New Date object
 */
export const addDaysToDate = (date: DateInput, days: number): Date => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return addDays(dateObj, days);
};

/**
 * Add months to a date
 * @param date - Base date
 * @param months - Number of months to add (can be negative)
 * @returns New Date object
 */
export const addMonthsToDate = (date: DateInput, months: number): Date => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return addMonths(dateObj, months);
};

/**
 * Add years to a date
 * @param date - Base date
 * @param years - Number of years to add (can be negative)
 * @returns New Date object
 */
export const addYearsToDate = (date: DateInput, years: number): Date => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return addYears(dateObj, years);
};

/**
 * Check if a date is valid
 * @param date - Date to check
 * @returns True if the date is valid
 */
export const isValidDate = (date: unknown): boolean => {
  if (!date) return false;
  const dateObj = date instanceof Date ? date : new Date(date as string);
  return !isNaN(dateObj.getTime());
};

/**
 * Get the start of the day (00:00:00) for a given date
 * @param date - Input date
 * @returns Start of the day
 */
export const startOfDay = (date: DateInput): Date => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return new Date(dateObj.getFullYear(), dateObj.getMonth(), dateObj.getDate());
};

/**
 * Get the end of the day (23:59:59.999) for a given date
 * @param date - Input date
 * @returns End of the day
 */
export const endOfDay = (date: DateInput): Date => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return new Date(dateObj.getFullYear(), dateObj.getMonth(), dateObj.getDate(), 23, 59, 59, 999);
};

/**
 * Get the difference in days between two dates
 * @param dateLeft - First date
 * @param dateRight - Second date
 * @returns Difference in days
 */
export const getDaysDifference = (dateLeft: DateInput, dateRight: DateInput): number => {
  const left = typeof dateLeft === 'string' ? new Date(dateLeft) : dateLeft;
  const right = typeof dateRight === 'string' ? new Date(dateRight) : dateRight;
  return differenceInDays(left, right);
};

export default {
  formatDate,
  formatRelativeTime,
  addDays: addDaysToDate,
  addMonths: addMonthsToDate,
  addYears: addYearsToDate,
  isValidDate,
  startOfDay,
  endOfDay,
  getDaysDifference,
};
