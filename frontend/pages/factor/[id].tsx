/**
 * Factor detail page with charts and statistics
 */
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import CumulativeReturnChart from '@/components/CumulativeReturnChart';
import { factorApi } from '@/lib/api';
import type { Factor, TimeSeriesResponse, RollingStatsResponse, FactorStatistics } from '@/types';
import { formatPercent, formatDate, getValueColor, formatNumber } from '@/lib/utils';

export default function FactorDetailPage() {
  const router = useRouter();
  const { id } = router.query;

  const [factor, setFactor] = useState<Factor | null>(null);
  const [timeSeries, setTimeSeries] = useState<TimeSeriesResponse | null>(null);
  const [rollingStats, setRollingStats] = useState<RollingStatsResponse | null>(null);
  const [statistics, setStatistics] = useState<FactorStatistics | null>(null);
  const [loading, setLoading] = useState(true);

  // Chart controls
  const [rollingMetric, setRollingMetric] = useState<'return' | 'volatility' | 'sharpe'>('return');
  const [rollingWindow, setRollingWindow] = useState(36);

  useEffect(() => {
    if (id) {
      loadFactorData(Number(id));
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      loadRollingStats(Number(id), rollingMetric, rollingWindow);
    }
  }, [id, rollingMetric, rollingWindow]);

  const loadFactorData = async (factorId: number) => {
    try {
      setLoading(true);

      const [factorData, timeSeriesData, statsData] = await Promise.all([
        factorApi.get(factorId),
        factorApi.getTimeSeries(factorId, { cumulative: true }),
        factorApi.getStatistics(factorId)
      ]);

      setFactor(factorData);
      setTimeSeries(timeSeriesData);
      setStatistics(statsData);
    } catch (error) {
      console.error('Error loading factor data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRollingStats = async (
    factorId: number,
    metric: 'return' | 'volatility' | 'sharpe',
    window: number
  ) => {
    try {
      const data = await factorApi.getRollingStats(factorId, {
        metric,
        window_length: window
      });
      setRollingStats(data);
    } catch (error) {
      console.error('Error loading rolling stats:', error);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Loading factor data...</p>
        </div>
      </Layout>
    );
  }

  if (!factor || !timeSeries) {
    return (
      <Layout>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700">Factor not found</p>
          <button
            onClick={() => router.push('/factors')}
            className="mt-4 px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Back to Factors
          </button>
        </div>
      </Layout>
    );
  }

  // Prepare chart data
  const cumulativeChartData = timeSeries.data.map(point => ({
    date: point.date,
    cumulative: point.cumulative_return
  }));

  const rollingChartData = rollingStats?.data.map(point => ({
    date: point.date,
    value: point.value
  })) || [];

  return (
    <Layout
      title={`${factor.name} (${factor.code}) - Factor Analysis | AQR Factor Explorer`}
      description={`Detailed performance analysis of ${factor.name} factor including cumulative returns, rolling statistics, drawdown analysis, and key performance metrics.`}
    >
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => router.back()}
          className="text-primary-600 hover:text-primary-700 mb-4 flex items-center"
        >
          ← Back
        </button>

        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{factor.name}</h1>
            <p className="text-lg text-gray-600 font-mono">{factor.code}</p>
            {factor.description && (
              <p className="mt-2 text-gray-700">{factor.description}</p>
            )}
          </div>
          <div className="flex gap-2">
            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-md text-sm">
              {factor.region}
            </span>
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-md text-sm">
              {factor.frequency}
            </span>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-8">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-xs text-gray-500 mb-1">Annualized Return</p>
          <p className={`text-xl font-bold ${getValueColor(factor.annualized_return)}`}>
            {formatPercent(factor.annualized_return)}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-xs text-gray-500 mb-1">Volatility</p>
          <p className="text-xl font-bold text-gray-700">
            {formatPercent(factor.annualized_volatility)}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-xs text-gray-500 mb-1">Sharpe Ratio</p>
          <p className="text-xl font-bold text-gray-700">
            {factor.sharpe_ratio?.toFixed(2) || 'N/A'}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-xs text-gray-500 mb-1">Max Drawdown</p>
          <p className="text-xl font-bold text-finance-negative">
            {formatPercent(factor.max_drawdown)}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-xs text-gray-500 mb-1">Total Return</p>
          <p className={`text-xl font-bold ${getValueColor(factor.total_return)}`}>
            {formatPercent(factor.total_return)}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-xs text-gray-500 mb-1">Data Range</p>
          <p className="text-sm font-semibold text-gray-700">
            {formatDate(factor.first_date)}
          </p>
          <p className="text-xs text-gray-500">to {formatDate(factor.last_date)}</p>
        </div>
      </div>

      {/* Cumulative Returns Chart */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Cumulative Returns</h2>
        <p className="text-gray-600 mb-4">
          Growth of $1 invested in this factor from {formatDate(factor.first_date)} to {formatDate(factor.last_date)}
        </p>
        <CumulativeReturnChart
          data={cumulativeChartData}
          lines={[{
            dataKey: 'cumulative',
            name: factor.name,
            color: '#0ea5e9'
          }]}
          height={400}
        />
      </div>

      {/* Rolling Statistics */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">Rolling Statistics</h2>
          <div className="flex gap-4">
            <div>
              <label className="text-sm text-gray-600 mr-2">Metric:</label>
              <select
                value={rollingMetric}
                onChange={(e) => setRollingMetric(e.target.value as any)}
                className="px-3 py-1 border border-gray-300 rounded-md text-sm"
              >
                <option value="return">Annualized Return</option>
                <option value="volatility">Volatility</option>
                <option value="sharpe">Sharpe Ratio</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600 mr-2">Window:</label>
              <select
                value={rollingWindow}
                onChange={(e) => setRollingWindow(Number(e.target.value))}
                className="px-3 py-1 border border-gray-300 rounded-md text-sm"
              >
                <option value="12">12 Months</option>
                <option value="24">24 Months</option>
                <option value="36">36 Months</option>
                <option value="60">60 Months</option>
              </select>
            </div>
          </div>
        </div>
        {rollingChartData.length > 0 && (
          <CumulativeReturnChart
            data={rollingChartData}
            lines={[{
              dataKey: 'value',
              name: `Rolling ${rollingWindow}M ${rollingMetric}`,
              color: '#10b981'
            }]}
            height={350}
            yAxisLabel={rollingMetric === 'sharpe' ? 'Sharpe Ratio' : 'Return'}
          />
        )}
      </div>

      {/* Period Statistics */}
      {statistics && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Period Statistics</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-gray-500 mb-1">Best Month</p>
              <p className="text-lg font-semibold text-finance-positive">
                {formatPercent(statistics.best_month)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Worst Month</p>
              <p className="text-lg font-semibold text-finance-negative">
                {formatPercent(statistics.worst_month)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Positive Months</p>
              <p className="text-lg font-semibold text-gray-700">
                {statistics.positive_months} / {statistics.total_months}
                {statistics.total_months && statistics.positive_months && (
                  <span className="text-sm text-gray-500 ml-1">
                    ({((statistics.positive_months / statistics.total_months) * 100).toFixed(0)}%)
                  </span>
                )}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Total Observations</p>
              <p className="text-lg font-semibold text-gray-700">
                {statistics.total_months}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Educational Content */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-gray-900 mb-2">How to Interpret These Charts</h3>
        <ul className="text-sm text-gray-700 space-y-2">
          <li>
            <strong>Cumulative Returns:</strong> Shows total growth over time. A steadily rising line
            indicates consistent positive returns.
          </li>
          <li>
            <strong>Rolling Statistics:</strong> Shows how the factor's performance metrics have evolved
            over rolling time windows. This helps identify regime changes.
          </li>
          <li>
            <strong>Sharpe Ratio:</strong> Risk-adjusted return. Higher is better. Above 0.5 is generally
            considered good for factor strategies.
          </li>
          <li>
            <strong>Max Drawdown:</strong> The largest peak-to-trough decline. Indicates worst-case
            loss experience.
          </li>
        </ul>
      </div>
    </Layout>
  );
}
