/**
 * Date and time manipulation and formatting utilities
 */

/**
 * Type for date input (string, Date, or timestamp)
 */
type DateInput = string | Date | number;

/**
 * Parse a date input into a Date object
 */
function parseDate(date: DateInput): Date {
  if (date instanceof Date) return date;
  if (typeof date === 'number') return new Date(date);
  if (typeof date === 'string') {
    // Handle ISO 8601 strings
    if (/^\d{4}-\d{2}-\d{2}/.test(date)) {
      return new Date(date);
    }
    // Handle other string formats
    const parsed = new Date(date);
    if (!isNaN(parsed.getTime())) return parsed;
  }
  throw new Error(`Invalid date input: ${date}`);
}

/**
 * Format a date as a localized date string
 * @param date - Date to format
 * @param locale - Locale to use (default: 'en-US')
 * @param options - Intl.DateTimeFormatOptions
 * @returns Formatted date string
 */
export function formatDate(
  date: DateInput,
  locale: string = 'en-US',
  options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }
): string {
  if (!date) return '';
  const dateObj = parseDate(date);
  return dateObj.toLocaleDateString(locale, options);
}

/**
 * Format a date and time as a localized string
 * @param date - Date to format
 * @param locale - Locale to use (default: 'en-US')
 * @param options - Intl.DateTimeFormatOptions
 * @returns Formatted date and time string
 */
export function formatDateTime(
  date: DateInput,
  locale: string = 'en-US',
  options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }
): string {
  if (!date) return '';
  const dateObj = parseDate(date);
  return dateObj.toLocaleString(locale, options);
}

/**
 * Format a date in a short format (e.g., 'MM/DD/YYYY')
 * @param date - Date to format
 * @param locale - Locale to use (default: 'en-US')
 * @returns Short formatted date string
 */
export function formatDateShort(
  date: DateInput,
  locale: string = 'en-US'
): string {
  if (!date) return '';
  const dateObj = parseDate(date);
  return dateObj.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Format a date in ISO 8601 format (YYYY-MM-DD)
 * @param date - Date to format
 * @returns ISO 8601 date string
 */
export function formatISODate(date: DateInput): string {
  if (!date) return '';
  const d = parseDate(date);
  return d.toISOString().split('T')[0];
}

/**
 * Format a date and time in ISO 8601 format (YYYY-MM-DDTHH:mm:ss.sssZ)
 * @param date - Date to format
 * @returns ISO 8601 date-time string
 */
export function formatISODateTime(date: DateInput): string {
  if (!date) return '';
  return parseDate(date).toISOString();
}

/**
 * Format a time as a localized string
 * @param date - Date containing the time to format
 * @param locale - Locale to use (default: 'en-US')
 * @param options - Intl.DateTimeFormatOptions
 * @returns Formatted time string
 */
export function formatTime(
  date: DateInput,
  locale: string = 'en-US',
  options: Intl.DateTimeFormatOptions = {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }
): string {
  if (!date) return '';
  const dateObj = parseDate(date);
  return dateObj.toLocaleTimeString(locale, options);
}

/**
 * Get the difference between two dates in the specified unit
 * @param date1 - First date
 * @param date2 - Second date (default: current date)
 * @param unit - Unit of time to return ('days', 'hours', 'minutes', 'seconds', 'milliseconds')
 * @returns Difference between dates in the specified unit
 */
export function dateDiff(
  date1: DateInput,
  date2: DateInput = new Date(),
  unit: 'days' | 'hours' | 'minutes' | 'seconds' | 'milliseconds' = 'milliseconds'
): number {
  const d1 = parseDate(date1);
  const d2 = parseDate(date2);
  const diff = d1.getTime() - d2.getTime();

  switch (unit) {
    case 'days':
      return Math.floor(diff / (1000 * 60 * 60 * 24));
    case 'hours':
      return Math.floor(diff / (1000 * 60 * 60));
    case 'minutes':
      return Math.floor(diff / (1000 * 60));
    case 'seconds':
      return Math.floor(diff / 1000);
    default:
      return diff;
  }
}

/**
 * Add a specified amount of time to a date
 * @param date - Base date
 * @param amount - Amount to add
 * @param unit - Unit of time to add ('years', 'months', 'days', 'hours', 'minutes', 'seconds', 'milliseconds')
 * @returns New date with the time added
 */
export function addToDate(
  date: DateInput,
  amount: number,
  unit: 'years' | 'months' | 'days' | 'hours' | 'minutes' | 'seconds' | 'milliseconds'
): Date {
  const d = parseDate(date);
  const result = new Date(d);

  switch (unit) {
    case 'years':
      result.setFullYear(result.getFullYear() + amount);
      break;
    case 'months':
      result.setMonth(result.getMonth() + amount);
      break;
    case 'days':
      result.setDate(result.getDate() + amount);
      break;
    case 'hours':
      result.setHours(result.getHours() + amount);
      break;
    case 'minutes':
      result.setMinutes(result.getMinutes() + amount);
      break;
    case 'seconds':
      result.setSeconds(result.getSeconds() + amount);
      break;
    case 'milliseconds':
      result.setMilliseconds(result.getMilliseconds() + amount);
      break;
  }

  return result;
}

/**
 * Check if a date is today
 * @param date - Date to check
 * @returns True if the date is today
 */
export function isToday(date: DateInput): boolean {
  if (!date) return false;
  const d = parseDate(date);
  const today = new Date();
  return (
    d.getDate() === today.getDate() &&
    d.getMonth() === today.getMonth() &&
    d.getFullYear() === today.getFullYear()
  );
}

/**
 * Check if a date is in the past
 * @param date - Date to check
 * @returns True if the date is in the past
 */
export function isPast(date: DateInput): boolean {
  if (!date) return false;
  return parseDate(date).getTime() < Date.now();
}

/**
 * Check if a date is in the future
 * @param date - Date to check
 * @returns True if the date is in the future
 */
export function isFuture(date: DateInput): boolean {
  if (!date) return false;
  return parseDate(date).getTime() > Date.now();
}

/**
 * Check if a date is a weekend
 * @param date - Date to check
 * @returns True if the date is a weekend day (Saturday or Sunday)
 */
export function isWeekend(date: DateInput): boolean {
  if (!date) return false;
  const day = parseDate(date).getDay();
  return day === 0 || day === 6;
}

/**
 * Get the start of the day for a given date
 * @param date - Date to get the start of
 * @returns New date set to the start of the day (00:00:00.000)
 */
export function startOfDay(date: DateInput): Date {
  const d = parseDate(date);
  const result = new Date(d);
  result.setHours(0, 0, 0, 0);
  return result;
}

/**
 * Get the end of the day for a given date
 * @param date - Date to get the end of
 * @returns New date set to the end of the day (23:59:59.999)
 */
export function endOfDay(date: DateInput): Date {
  const d = parseDate(date);
  const result = new Date(d);
  result.setHours(23, 59, 59, 999);
  return result;
}

/**
 * Get the number of days in a month
 * @param year - Year
 * @param month - Month (0-11)
 * @returns Number of days in the month
 */
export function daysInMonth(year: number, month: number): number {
  return new Date(year, month + 1, 0).getDate();
}

/**
 * Check if two dates are the same day
 * @param date1 - First date
 * @param date2 - Second date
 * @returns True if the dates are the same day
 */
export function isSameDay(date1: DateInput, date2: DateInput): boolean {
  if (!date1 || !date2) return false;
  const d1 = parseDate(date1);
  const d2 = parseDate(date2);
  return (
    d1.getFullYear() === d2.getFullYear() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getDate() === d2.getDate()
  );
}

/**
 * Format a duration in milliseconds as a human-readable string
 * @param ms - Duration in milliseconds
 * @returns Formatted duration string (e.g., '2h 30m')
 */
export function formatDuration(ms: number): string {
  if (!ms && ms !== 0) return '';
  
  const isNegative = ms < 0;
  const absMs = Math.abs(ms);
  
  const seconds = Math.floor(absMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  const parts: string[] = [];
  
  if (days > 0) parts.push(`${days}d`);
  if (hours % 24 > 0) parts.push(`${hours % 24}h`);
  if (minutes % 60 > 0 && days === 0) parts.push(`${minutes % 60}m`);
  if (seconds % 60 > 0 && hours === 0) parts.push(`${seconds % 60}s`);
  
  if (parts.length === 0) return '0s';
  
  return (isNegative ? '-' : '') + parts.join(' ');
}

/**
 * Get the current date in ISO format (YYYY-MM-DD)
 * @returns Current date in ISO format
 */
export function todayISO(): string {
  return formatISODate(new Date());
}

/**
 * Get the current date and time in ISO format (YYYY-MM-DDTHH:mm:ss.sssZ)
 * @returns Current date and time in ISO format
 */
export function nowISO(): string {
  return new Date().toISOString();
}