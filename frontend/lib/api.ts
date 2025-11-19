/**
 * API client for communicating with the backend
 */
import axios from 'axios';
import type {
  Factor,
  TimeSeriesResponse,
  ComparisonResponse,
  RollingStatsResponse,
  FactorStatistics,
  CorrelationMatrix,
  TopFactorsResponse,
  FactorGroup
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Factor endpoints
export const factorApi = {
  /**
   * Get list of factors with optional filters
   */
  list: async (params?: {
    region?: string;
    asset_class?: string;
    frequency?: string;
    group_id?: number;
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<Factor[]> => {
    const response = await api.get('/api/factors', { params });
    return response.data;
  },

  /**
   * Get detailed information about a specific factor
   */
  get: async (factorId: number): Promise<Factor> => {
    const response = await api.get(`/api/factors/${factorId}`);
    return response.data;
  },

  /**
   * Get time series data for a factor
   */
  getTimeSeries: async (
    factorId: number,
    params?: {
      start_date?: string;
      end_date?: string;
      cumulative?: boolean;
    }
  ): Promise<TimeSeriesResponse> => {
    const response = await api.get(`/api/factors/${factorId}/timeseries`, { params });
    return response.data;
  },

  /**
   * Get rolling statistics for a factor
   */
  getRollingStats: async (
    factorId: number,
    params?: {
      window_length?: number;
      metric?: 'return' | 'volatility' | 'sharpe';
    }
  ): Promise<RollingStatsResponse> => {
    const response = await api.get(`/api/factors/${factorId}/rolling`, { params });
    return response.data;
  },

  /**
   * Get statistics for a factor over a specific period
   */
  getStatistics: async (
    factorId: number,
    params?: {
      start_date?: string;
      end_date?: string;
    }
  ): Promise<FactorStatistics> => {
    const response = await api.get(`/api/factors/${factorId}/statistics`, { params });
    return response.data;
  },
};

// Analytics endpoints
export const analyticsApi = {
  /**
   * Compare multiple factors
   */
  compare: async (params: {
    factor_ids: number[];
    start_date?: string;
    end_date?: string;
  }): Promise<ComparisonResponse> => {
    const queryParams = new URLSearchParams();
    params.factor_ids.forEach(id => queryParams.append('factor_ids', id.toString()));
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);

    const response = await api.get(`/api/analytics/comparison?${queryParams.toString()}`);
    return response.data;
  },

  /**
   * Compute correlation matrix for selected factors
   */
  getCorrelation: async (params: {
    factor_ids: number[];
    start_date?: string;
    end_date?: string;
  }): Promise<CorrelationMatrix> => {
    const queryParams = new URLSearchParams();
    params.factor_ids.forEach(id => queryParams.append('factor_ids', id.toString()));
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);

    const response = await api.get(`/api/analytics/correlation?${queryParams.toString()}`);
    return response.data;
  },

  /**
   * Get top performing factors
   */
  getTopFactors: async (params?: {
    period?: string;
    metric?: string;
    limit?: number;
    region?: string;
  }): Promise<TopFactorsResponse> => {
    const response = await api.get('/api/analytics/top-factors', { params });
    return response.data;
  },
};

// Metadata endpoints
export const metadataApi = {
  /**
   * Get list of available regions
   */
  getRegions: async (): Promise<string[]> => {
    const response = await api.get('/api/regions');
    return response.data.regions;
  },

  /**
   * Get list of available asset classes
   */
  getAssetClasses: async (): Promise<string[]> => {
    const response = await api.get('/api/asset-classes');
    return response.data.asset_classes;
  },

  /**
   * Get list of available frequencies
   */
  getFrequencies: async (): Promise<string[]> => {
    const response = await api.get('/api/frequencies');
    return response.data.frequencies;
  },
};

export default api;
