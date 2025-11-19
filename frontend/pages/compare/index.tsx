/**
 * Factor comparison page
 */
import React, { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import CumulativeReturnChart from '@/components/CumulativeReturnChart';
import { factorApi, analyticsApi } from '@/lib/api';
import type { Factor, ComparisonResponse, CorrelationMatrix } from '@/types';
import { formatPercent } from '@/lib/utils';

const CHART_COLORS = [
  '#0ea5e9', // blue
  '#10b981', // green
  '#f59e0b', // orange
  '#ef4444', // red
  '#8b5cf6', // purple
  '#ec4899', // pink
];

export default function ComparePage() {
  const [availableFactors, setAvailableFactors] = useState<Factor[]>([]);
  const [selectedFactorIds, setSelectedFactorIds] = useState<number[]>([]);
  const [comparisonData, setComparisonData] = useState<ComparisonResponse | null>(null);
  const [correlationData, setCorrelationData] = useState<CorrelationMatrix | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadAvailableFactors();
  }, []);

  const loadAvailableFactors = async () => {
    try {
      const factors = await factorApi.list({ limit: 100 });
      setAvailableFactors(factors);
    } catch (error) {
      console.error('Error loading factors:', error);
    }
  };

  const handleFactorToggle = (factorId: number) => {
    setSelectedFactorIds(prev => {
      if (prev.includes(factorId)) {
        return prev.filter(id => id !== factorId);
      } else {
        if (prev.length >= 6) {
          alert('Maximum 6 factors can be compared at once');
          return prev;
        }
        return [...prev, factorId];
      }
    });
  };

  const handleCompare = async () => {
    if (selectedFactorIds.length < 2) {
      alert('Please select at least 2 factors to compare');
      return;
    }

    try {
      setLoading(true);

      const [comparison, correlation] = await Promise.all([
        analyticsApi.compare({ factor_ids: selectedFactorIds }),
        analyticsApi.getCorrelation({ factor_ids: selectedFactorIds })
      ]);

      setComparisonData(comparison);
      setCorrelationData(correlation);
    } catch (error) {
      console.error('Error comparing factors:', error);
      alert('Error loading comparison data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Prepare chart data
  const chartData: any[] = [];
  if (comparisonData) {
    const dateMap = new Map<string, any>();

    comparisonData.factors.forEach(factor => {
      factor.data.forEach(point => {
        if (!dateMap.has(point.date)) {
          dateMap.set(point.date, { date: point.date });
        }
        dateMap.get(point.date)![factor.factor_code] = point.cumulative_return;
      });
    });

    chartData.push(...Array.from(dateMap.values()).sort((a, b) =>
      new Date(a.date).getTime() - new Date(b.date).getTime()
    ));
  }

  const chartLines = comparisonData?.factors.map((factor, index) => ({
    dataKey: factor.factor_code,
    name: factor.factor_name,
    color: CHART_COLORS[index % CHART_COLORS.length]
  })) || [];

  const filteredFactors = availableFactors.filter(factor =>
    factor.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    factor.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Layout
      title="Compare Factors - AQR Factor Explorer"
      description="Compare performance of multiple AQR factors side-by-side with interactive charts and correlation analysis."
    >
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Compare Factors</h1>
        <p className="text-gray-600">
          Select 2-6 factors to compare their performance and correlations
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Factor Selection Panel */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-6 sticky top-24">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Select Factors ({selectedFactorIds.length}/6)
            </h2>

            {/* Search */}
            <input
              type="text"
              placeholder="Search factors..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md mb-4 focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />

            {/* Factor List */}
            <div className="max-h-96 overflow-y-auto space-y-2">
              {filteredFactors.map(factor => {
                const isSelected = selectedFactorIds.includes(factor.id);
                return (
                  <label
                    key={factor.id}
                    className={`flex items-start p-3 rounded-lg border cursor-pointer transition-colors ${
                      isSelected
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => handleFactorToggle(factor.id)}
                      className="mt-1 mr-3"
                    />
                    <div className="flex-grow">
                      <p className="font-medium text-sm text-gray-900">{factor.name}</p>
                      <p className="text-xs text-gray-500 font-mono">{factor.code}</p>
                      <p className="text-xs text-gray-600 mt-1">
                        {factor.region} • {formatPercent(factor.annualized_return)}
                      </p>
                    </div>
                  </label>
                );
              })}
            </div>

            {/* Compare Button */}
            <button
              onClick={handleCompare}
              disabled={selectedFactorIds.length < 2 || loading}
              className={`w-full mt-4 py-3 rounded-lg font-semibold transition-colors ${
                selectedFactorIds.length >= 2 && !loading
                  ? 'bg-primary-600 text-white hover:bg-primary-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              {loading ? 'Loading...' : 'Compare Factors'}
            </button>

            {selectedFactorIds.length > 0 && (
              <button
                onClick={() => setSelectedFactorIds([])}
                className="w-full mt-2 py-2 text-sm text-gray-600 hover:text-gray-900"
              >
                Clear Selection
              </button>
            )}
          </div>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2">
          {!comparisonData ? (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <svg
                className="mx-auto h-16 w-16 text-gray-400 mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              <p className="text-gray-600 text-lg mb-2">Select factors to compare</p>
              <p className="text-gray-500 text-sm">
                Choose at least 2 factors from the list and click "Compare Factors"
              </p>
            </div>
          ) : (
            <>
              {/* Cumulative Performance Chart */}
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  Cumulative Performance Comparison
                </h2>
                <p className="text-gray-600 mb-4">
                  Comparing {comparisonData.factors.length} factors from{' '}
                  {new Date(comparisonData.start_date).toLocaleDateString()} to{' '}
                  {new Date(comparisonData.end_date).toLocaleDateString()}
                </p>
                <CumulativeReturnChart
                  data={chartData}
                  lines={chartLines}
                  height={450}
                />
              </div>

              {/* Performance Summary Table */}
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  Performance Summary
                </h2>
                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Factor
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          Total Return
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          Observations
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {comparisonData.factors.map((factor, index) => {
                        const lastPoint = factor.data[factor.data.length - 1];
                        return (
                          <tr key={factor.factor_id}>
                            <td className="px-4 py-3">
                              <div className="flex items-center">
                                <div
                                  className="w-3 h-3 rounded-full mr-3"
                                  style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }}
                                ></div>
                                <div>
                                  <p className="font-medium text-sm text-gray-900">
                                    {factor.factor_name}
                                  </p>
                                  <p className="text-xs text-gray-500 font-mono">
                                    {factor.factor_code}
                                  </p>
                                </div>
                              </div>
                            </td>
                            <td className="px-4 py-3 text-right font-semibold">
                              {formatPercent(lastPoint?.cumulative_return)}
                            </td>
                            <td className="px-4 py-3 text-right text-sm text-gray-600">
                              {factor.data.length}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Correlation Matrix */}
              {correlationData && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">
                    Correlation Matrix
                  </h2>
                  <p className="text-gray-600 mb-4">
                    Correlation between factors (1.0 = perfect positive correlation, -1.0 = perfect negative correlation)
                  </p>
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                      <thead>
                        <tr>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500"></th>
                          {correlationData.factor_codes.map(code => (
                            <th
                              key={code}
                              className="px-3 py-2 text-center text-xs font-medium text-gray-500 font-mono"
                            >
                              {code}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {correlationData.correlations.map((row, i) => (
                          <tr key={i}>
                            <td className="px-3 py-2 font-medium text-xs text-gray-700 font-mono">
                              {correlationData.factor_codes[i]}
                            </td>
                            {row.map((corr, j) => {
                              const intensity = Math.abs(corr);
                              const color = corr >= 0
                                ? `rgba(16, 185, 129, ${intensity * 0.8})`  // green for positive
                                : `rgba(239, 68, 68, ${intensity * 0.8})`;   // red for negative
                              return (
                                <td
                                  key={j}
                                  className="px-3 py-2 text-center font-mono"
                                  style={{ backgroundColor: color }}
                                >
                                  {corr.toFixed(2)}
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Educational Content */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-gray-900 mb-2">Understanding Factor Correlations</h3>
        <p className="text-sm text-gray-700 mb-2">
          Correlation measures how factors move together:
        </p>
        <ul className="text-sm text-gray-700 space-y-1 ml-4">
          <li>• <strong>High positive correlation (0.7-1.0):</strong> Factors tend to move in the same direction</li>
          <li>• <strong>Low correlation (0.3 to -0.3):</strong> Factors provide diversification benefits</li>
          <li>• <strong>Negative correlation (-0.7 to -1.0):</strong> Factors tend to move in opposite directions</li>
        </ul>
      </div>
    </Layout>
  );
}
