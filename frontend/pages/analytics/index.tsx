/**
 * Analytics page with heatmaps and top factors
 */
import React, { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { analyticsApi, factorApi } from '@/lib/api';
import type { TopFactorsResponse, Factor } from '@/types';
import { formatPercent, getValueColor } from '@/lib/utils';
import Link from 'next/link';

export default function AnalyticsPage() {
  const [topFactors, setTopFactors] = useState<TopFactorsResponse | null>(null);
  const [loading, setLoading] = useState(false);

  // Controls
  const [period, setPeriod] = useState('all_time');
  const [metric, setMetric] = useState('annualized_return');
  const [selectedRegion, setSelectedRegion] = useState('');

  useEffect(() => {
    loadTopFactors();
  }, [period, metric, selectedRegion]);

  const loadTopFactors = async () => {
    try {
      setLoading(true);

      const params: any = {
        period,
        metric,
        limit: 20
      };

      if (selectedRegion) {
        params.region = selectedRegion;
      }

      const data = await analyticsApi.getTopFactors(params);
      setTopFactors(data);
    } catch (error) {
      console.error('Error loading top factors:', error);
    } finally {
      setLoading(false);
    }
  };

  const periodOptions = [
    { value: 'all_time', label: 'All Time' },
    { value: 'last_1y', label: 'Last 1 Year' },
    { value: 'last_3y', label: 'Last 3 Years' },
    { value: 'last_5y', label: 'Last 5 Years' },
    { value: 'last_10y', label: 'Last 10 Years' },
  ];

  const metricOptions = [
    { value: 'annualized_return', label: 'Annualized Return' },
    { value: 'sharpe_ratio', label: 'Sharpe Ratio' },
  ];

  const regionOptions = [
    { value: '', label: 'All Regions' },
    { value: 'US', label: 'US' },
    { value: 'Global', label: 'Global' },
    { value: 'International', label: 'International' },
    { value: 'Europe', label: 'Europe' },
    { value: 'Asia Pacific', label: 'Asia Pacific' },
    { value: 'Emerging Markets', label: 'Emerging Markets' },
  ];

  const getMedalColor = (rank: number) => {
    if (rank === 1) return 'text-yellow-500';
    if (rank === 2) return 'text-gray-400';
    if (rank === 3) return 'text-orange-600';
    return 'text-gray-600';
  };

  const getMedalIcon = (rank: number) => {
    if (rank <= 3) {
      return (
        <svg className={`w-6 h-6 ${getMedalColor(rank)}`} fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      );
    }
    return <span className="text-gray-500 font-semibold">#{rank}</span>;
  };

  return (
    <Layout
      title="Factor Analytics - AQR Factor Explorer"
      description="Analyze top performing factors across different time periods and metrics. Discover factor trends and rankings."
    >
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Factor Analytics</h1>
        <p className="text-gray-600">
          Discover top performing factors and analyze trends across different time periods
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Analysis Controls</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Time Period
            </label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {periodOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ranking Metric
            </label>
            <select
              value={metric}
              onChange={(e) => setMetric(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {metricOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Region Filter
            </label>
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {regionOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Top Factors */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
        </div>
      ) : topFactors && topFactors.factors.length > 0 ? (
        <>
          <div className="bg-white rounded-lg shadow overflow-hidden mb-8">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">
                Top Factors - {periodOptions.find(p => p.value === period)?.label}
              </h2>
              <p className="text-gray-600 mt-1">
                Ranked by {metricOptions.find(m => m.value === metric)?.label}
                {selectedRegion && ` in ${selectedRegion}`}
              </p>
            </div>

            {/* Podium for Top 3 */}
            {topFactors.factors.length >= 3 && (
              <div className="p-6 bg-gradient-to-b from-gray-50 to-white border-b border-gray-200">
                <div className="flex justify-center items-end gap-4 max-w-3xl mx-auto">
                  {/* Second Place */}
                  <div className="flex-1 text-center">
                    <div className="bg-gray-100 rounded-t-lg p-4 mb-2" style={{ height: '140px' }}>
                      <div className="flex justify-center mb-2">
                        {getMedalIcon(2)}
                      </div>
                      <Link href={`/factor/${topFactors.factors[1].factor_id}`}>
                        <p className="font-semibold text-sm hover:text-primary-600 cursor-pointer">
                          {topFactors.factors[1].factor_name}
                        </p>
                      </Link>
                      <p className="text-xs text-gray-500 mt-1">
                        {topFactors.factors[1].region}
                      </p>
                      <p className={`text-lg font-bold mt-2 ${getValueColor(topFactors.factors[1].metric_value)}`}>
                        {metric === 'sharpe_ratio'
                          ? topFactors.factors[1].metric_value.toFixed(2)
                          : formatPercent(topFactors.factors[1].metric_value)}
                      </p>
                    </div>
                  </div>

                  {/* First Place */}
                  <div className="flex-1 text-center">
                    <div className="bg-yellow-50 border-2 border-yellow-400 rounded-t-lg p-4 mb-2" style={{ height: '180px' }}>
                      <div className="flex justify-center mb-2">
                        {getMedalIcon(1)}
                      </div>
                      <Link href={`/factor/${topFactors.factors[0].factor_id}`}>
                        <p className="font-bold text-base hover:text-primary-600 cursor-pointer">
                          {topFactors.factors[0].factor_name}
                        </p>
                      </Link>
                      <p className="text-xs text-gray-500 mt-1">
                        {topFactors.factors[0].region}
                      </p>
                      <p className={`text-2xl font-bold mt-2 ${getValueColor(topFactors.factors[0].metric_value)}`}>
                        {metric === 'sharpe_ratio'
                          ? topFactors.factors[0].metric_value.toFixed(2)
                          : formatPercent(topFactors.factors[0].metric_value)}
                      </p>
                    </div>
                  </div>

                  {/* Third Place */}
                  <div className="flex-1 text-center">
                    <div className="bg-orange-50 rounded-t-lg p-4 mb-2" style={{ height: '120px' }}>
                      <div className="flex justify-center mb-2">
                        {getMedalIcon(3)}
                      </div>
                      <Link href={`/factor/${topFactors.factors[2].factor_id}`}>
                        <p className="font-semibold text-sm hover:text-primary-600 cursor-pointer">
                          {topFactors.factors[2].factor_name}
                        </p>
                      </Link>
                      <p className="text-xs text-gray-500 mt-1">
                        {topFactors.factors[2].region}
                      </p>
                      <p className={`text-lg font-bold mt-2 ${getValueColor(topFactors.factors[2].metric_value)}`}>
                        {metric === 'sharpe_ratio'
                          ? topFactors.factors[2].metric_value.toFixed(2)
                          : formatPercent(topFactors.factors[2].metric_value)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Full Rankings Table */}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Rank
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Factor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Region
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      {metricOptions.find(m => m.value === metric)?.label}
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {topFactors.factors.map((factor) => (
                    <tr
                      key={factor.factor_id}
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => window.location.href = `/factor/${factor.factor_id}`}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {getMedalIcon(factor.rank)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <p className="font-medium text-sm text-gray-900">
                            {factor.factor_name}
                          </p>
                          <p className="text-xs text-gray-500 font-mono">
                            {factor.factor_code}
                          </p>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {factor.region || 'N/A'}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-right text-sm font-semibold ${getValueColor(factor.metric_value)}`}>
                        {metric === 'sharpe_ratio'
                          ? factor.metric_value.toFixed(2)
                          : formatPercent(factor.metric_value)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Insights */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="font-semibold text-gray-900 mb-2">Key Insights</h3>
            <ul className="text-sm text-gray-700 space-y-2">
              <li>
                • <strong>Top Performer:</strong> {topFactors.factors[0].factor_name} leads with a{' '}
                {metric === 'sharpe_ratio' ? 'Sharpe ratio' : 'return'} of{' '}
                {metric === 'sharpe_ratio'
                  ? topFactors.factors[0].metric_value.toFixed(2)
                  : formatPercent(topFactors.factors[0].metric_value)}
              </li>
              <li>
                • <strong>Time Period:</strong> Analysis covers{' '}
                {periodOptions.find(p => p.value === period)?.label.toLowerCase()}
              </li>
              <li>
                • <strong>Note:</strong> Past performance does not guarantee future results. Factor performance
                can vary significantly across different market regimes.
              </li>
            </ul>
          </div>
        </>
      ) : (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 text-lg">
            No factor data available for the selected criteria.
          </p>
        </div>
      )}
    </Layout>
  );
}
