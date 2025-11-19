/**
 * Utility functions
 */

/**
 * Format percentage value
 */
export function formatPercent(value: number | null | undefined, decimals: number = 2): string {
  if (value === null || value === undefined || isNaN(value)) {
    return 'N/A';
  }
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format number with thousand separators
 */
export function formatNumber(value: number | null | undefined, decimals: number = 2): string {
  if (value === null || value === undefined || isNaN(value)) {
    return 'N/A';
  }
  return value.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
}

/**
 * Format date to readable string
 */
export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return 'N/A';

  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch (e) {
    return dateString;
  }
}

/**
 * Get color based on value (for returns, positive is green, negative is red)
 */
export function getValueColor(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) {
    return 'text-gray-500';
  }
  return value >= 0 ? 'text-finance-positive' : 'text-finance-negative';
}

/**
 * Clamp a value between min and max
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/**
 * Calculate cumulative returns from period returns
 */
export function calculateCumulativeReturns(returns: number[]): number[] {
  let cumulative = 1.0;
  return returns.map(ret => {
    cumulative *= (1 + ret);
    return cumulative - 1;
  });
}

/**
 * Parse ISO date string to Date object
 */
export function parseDate(dateString: string): Date {
  return new Date(dateString);
}

/**
 * Format date for API calls (YYYY-MM-DD)
 */
export function formatDateForAPI(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Get date N years ago
 */
export function getDateYearsAgo(years: number): Date {
  const date = new Date();
  date.setFullYear(date.getFullYear() - years);
  return date;
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

/**
 * Combine CSS class names
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}
