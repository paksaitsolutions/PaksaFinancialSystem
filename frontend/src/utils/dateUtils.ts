/**
 * Date formatting and manipulation utilities
 */

/**
 * Format a date string or Date object to YYYY-MM-DD format
 * @param dateInput The date to format (string or Date object)
 * @returns Formatted date string (YYYY-MM-DD)
 * @throws {Error} If the input date is invalid
 */
export const formatDate = (dateInput: string | Date): string => {
  const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput;
  if (isNaN(date.getTime())) {
    throw new Error('Invalid date input');
  }
  return date.toISOString().split('T')[0];
};

/**
 * Format a date to a human-readable string
 * @param date Date to format
 * @param locale Locale to use (default: en-US)
 * @param options Intl.DateTimeFormatOptions
 * @returns Formatted date string
 */
export const formatDateReadable = (
  date: Date | string,
  locale: string = 'en-US',
  options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }
): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  if (isNaN(dateObj.getTime())) {
    return 'Invalid date';
  }
  return new Intl.DateTimeFormat(locale, options).format(dateObj);
};

/**
 * Check if a date is valid
 * @param date Date to check
 * @returns boolean indicating if the date is valid
 */
export const isValidDate = (date: any): boolean => {
  return !isNaN(new Date(date).getTime());
};

/**
 * Get the difference in days between two dates
 * @param date1 First date
 * @param date2 Second date
 * @returns Number of days between the two dates
 */
export const getDaysDifference = (date1: Date, date2: Date): number => {
  const diffTime = Math.abs(date2.getTime() - date1.getTime());
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};

/**
 * Add days to a date
 * @param date Base date
 * @param days Number of days to add (can be negative)
 * @returns New Date object with the days added
 */
export const addDays = (date: Date, days: number): Date => {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
};
