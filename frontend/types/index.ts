/**
 * TypeScript type definitions for AQR Factor Explorer
 */

export interface Factor {
  id: number;
  code: string;
  name: string;
  provider: string;
  region: string | null;
  asset_class: string | null;
  frequency: string | null;
  description: string | null;
  first_date: string | null;
  last_date: string | null;
  group_id: number | null;
  total_return: number | null;
  annualized_return: number | null;
  annualized_volatility: number | null;
  max_drawdown: number | null;
  sharpe_ratio: number | null;
  created_at: string;
  updated_at: string;
}

export interface FactorGroup {
  id: number;
  code: string;
  name: string;
  description: string | null;
  created_at: string;
}

export interface TimeSeriesPoint {
  date: string;
  return_value: number;
  cumulative_return: number | null;
}

export interface TimeSeriesResponse {
  factor_id: number;
  factor_code: string;
  factor_name: string;
  start_date: string;
  end_date: string;
  data: TimeSeriesPoint[];
}

export interface ComparisonSeriesData {
  factor_id: number;
  factor_code: string;
  factor_name: string;
  data: TimeSeriesPoint[];
}

export interface ComparisonResponse {
  start_date: string;
  end_date: string;
  factors: ComparisonSeriesData[];
}

export interface RollingStatPoint {
  date: string;
  value: number;
}

export interface RollingStatsResponse {
  factor_id: number;
  factor_code: string;
  metric: string;
  window_length: number;
  data: RollingStatPoint[];
}

export interface FactorStatistics {
  factor_id: number;
  factor_code: string;
  start_date: string;
  end_date: string;
  total_return: number;
  annualized_return: number;
  annualized_volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  best_month: number | null;
  worst_month: number | null;
  positive_months: number | null;
  total_months: number | null;
}

export interface CorrelationMatrix {
  start_date: string;
  end_date: string;
  factor_codes: string[];
  correlations: number[][];
}

export interface TopFactor {
  factor_id: number;
  factor_code: string;
  factor_name: string;
  region: string | null;
  metric_value: number;
  rank: number;
}

export interface TopFactorsResponse {
  period: string;
  metric: string;
  start_date: string;
  end_date: string;
  factors: TopFactor[];
}
