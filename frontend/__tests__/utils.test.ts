/**
 * Tests for utility functions
 */
import { formatPercent, formatDate, getValueColor, formatNumber } from '../lib/utils';

describe('formatPercent', () => {
    test('formats decimal to percentage', () => {
        expect(formatPercent(0.08)).toBe('8.00%');
        expect(formatPercent(0.1234)).toBe('12.34%');
        expect(formatPercent(-0.05)).toBe('-5.00%');
    });

    test('handles null and undefined', () => {
        expect(formatPercent(null)).toBe('N/A');
        expect(formatPercent(undefined)).toBe('N/A');
    });

    test('handles NaN', () => {
        expect(formatPercent(NaN)).toBe('N/A');
    });

    test('respects decimal parameter', () => {
        expect(formatPercent(0.12345, 3)).toBe('12.345%');
        expect(formatPercent(0.1, 0)).toBe('10%');
    });

    test('formats zero correctly', () => {
        expect(formatPercent(0)).toBe('0.00%');
    });
});

describe('formatDate', () => {
    test('formats ISO date string', () => {
        const result = formatDate('2020-01-15');
        expect(result).toContain('Jan');
        expect(result).toContain('15');
        expect(result).toContain('2020');
    });

    test('handles null and undefined', () => {
        expect(formatDate(null)).toBe('N/A');
        expect(formatDate(undefined)).toBe('N/A');
    });

    test('handles empty string', () => {
        expect(formatDate('')).toBe('N/A');
    });
});

describe('getValueColor', () => {
    test('returns positive color for positive values', () => {
        expect(getValueColor(0.05)).toBe('text-finance-positive');
        expect(getValueColor(0)).toBe('text-finance-positive');
    });

    test('returns negative color for negative values', () => {
        expect(getValueColor(-0.05)).toBe('text-finance-negative');
    });

    test('returns gray for null/undefined', () => {
        expect(getValueColor(null)).toBe('text-gray-500');
        expect(getValueColor(undefined)).toBe('text-gray-500');
    });

    test('returns gray for NaN', () => {
        expect(getValueColor(NaN)).toBe('text-gray-500');
    });
});

describe('formatNumber', () => {
    test('formats numbers with commas', () => {
        expect(formatNumber(1000)).toBe('1,000.00');
        expect(formatNumber(1234567.89)).toBe('1,234,567.89');
    });

    test('handles null and undefined', () => {
        expect(formatNumber(null)).toBe('N/A');
        expect(formatNumber(undefined)).toBe('N/A');
    });

    test('respects decimal parameter', () => {
        expect(formatNumber(1234.5678, 3)).toBe('1,234.568');
    });
});
