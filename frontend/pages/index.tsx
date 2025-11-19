/**
 * Landing page for AQR Factor Explorer
 */
import React, { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import FactorCard from '@/components/FactorCard';
import CumulativeReturnChart from '@/components/CumulativeReturnChart';
import { factorApi, analyticsApi } from '@/lib/api';
import type { Factor, ComparisonResponse, TopFactorsResponse } from '@/types';
import Link from 'next/link';

export default function Home() {
  const [topFactors, setTopFactors] = useState<Factor[]>([]);
  const [recentPerformance, setRecentPerformance] = useState<ComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);

      // Load top factors
      const factors = await factorApi.list({ limit: 6 });
      setTopFactors(factors.slice(0, 6));

      // Load comparison data for top 4 factors (if available)
      if (factors.length >= 4) {
        const factorIds = factors.slice(0, 4).map(f => f.id);
        const comparison = await analyticsApi.compare({
          factor_ids: factorIds
        });
        setRecentPerformance(comparison);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      window.location.href = `/factors?search=${encodeURIComponent(searchQuery)}`;
    }
  };

  // Prepare chart data
  const chartData = recentPerformance?.factors.map(factor => ({
    lines: factor.data.map((point, index) => ({
      date: point.date,
      [factor.factor_code]: point.cumulative_return
    }))
  }));

  // Merge all data points by date
  const mergedChartData: any[] = [];
  if (recentPerformance) {
    const dateMap = new Map<string, any>();

    recentPerformance.factors.forEach(factor => {
      factor.data.forEach(point => {
        if (!dateMap.has(point.date)) {
          dateMap.set(point.date, { date: point.date });
        }
        dateMap.get(point.date)![factor.factor_code] = point.cumulative_return;
      });
    });

    mergedChartData.push(...Array.from(dateMap.values()).sort((a, b) =>
      new Date(a.date).getTime() - new Date(b.date).getTime()
    ));
  }

  const chartLines = recentPerformance?.factors.map((factor, index) => ({
    dataKey: factor.factor_code,
    name: factor.factor_name,
    color: ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444'][index % 4]
  })) || [];

  return (
    <Layout
      title="AQR Factor Explorer - Interactive Factor Performance Analysis"
      description="Explore and analyze AQR factor returns with interactive charts, cross-factor comparisons, and comprehensive analytics. Data-driven insights for factor investing."
    >
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-800 text-white rounded-lg p-8 md:p-12 mb-8 shadow-xl">
        <h1 className="text-4xl md:text-5xl font-bold mb-4">
          AQR Factor Explorer
        </h1>
        <p className="text-xl md:text-2xl mb-6 text-primary-100">
          Interactive tools for analyzing factor performance using publicly available AQR research data
        </p>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="max-w-2xl">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Search for factors (e.g., QMJ, Value, Momentum)..."
              className="flex-grow px-4 py-3 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-300"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button
              type="submit"
              className="px-6 py-3 bg-white text-primary-700 font-semibold rounded-lg hover:bg-primary-50 transition-colors"
            >
              Search
            </button>
          </div>
        </form>
      </section>

      {/* What is a Factor? */}
      <section className="bg-white rounded-lg p-8 mb-8 shadow">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">What are Factors?</h2>
        <div className="prose prose-gray max-w-none">
          <p className="text-gray-700 mb-4">
            Factors are characteristics of securities that help explain their risk and return. Academic research
            and practitioners have identified several factors that have historically provided excess returns over
            the market, including:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="p-4 bg-blue-50 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">Value</h3>
              <p className="text-sm text-gray-700">
                Buying undervalued securities relative to fundamentals
              </p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <h3 className="font-semibold text-green-900 mb-2">Momentum</h3>
              <p className="text-sm text-gray-700">
                Investing in recent winners and avoiding losers
              </p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <h3 className="font-semibold text-purple-900 mb-2">Quality</h3>
              <p className="text-sm text-gray-700">
                Favoring profitable, stable, and growing companies
              </p>
            </div>
            <div className="p-4 bg-orange-50 rounded-lg">
              <h3 className="font-semibold text-orange-900 mb-2">Low Risk</h3>
              <p className="text-sm text-gray-700">
                Investing in lower-volatility, lower-beta securities
              </p>
            </div>
            <div className="p-4 bg-red-50 rounded-lg">
              <h3 className="font-semibold text-red-900 mb-2">Carry</h3>
              <p className="text-sm text-gray-700">
                Earning yield premium across asset classes
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">Size</h3>
              <p className="text-sm text-gray-700">
                Small-cap stocks historically outperforming large-cap
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Recent Performance Chart */}
      {!loading && recentPerformance && mergedChartData.length > 0 && (
        <section className="bg-white rounded-lg p-8 mb-8 shadow">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Factor Performance</h2>
          <p className="text-gray-600 mb-4">
            Cumulative returns for selected AQR factors. Compare how different factor strategies have
            performed over time.
          </p>
          <CumulativeReturnChart
            data={mergedChartData}
            lines={chartLines}
            height={400}
          />
        </section>
      )}

      {/* Featured Factors */}
      <section className="mb-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Featured Factors</h2>
          <Link
            href="/factors"
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            View All →
          </Link>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600">Loading factors...</p>
          </div>
        ) : topFactors.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {topFactors.map(factor => (
              <FactorCard key={factor.id} factor={factor} />
            ))}
          </div>
        ) : (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
            <p className="text-gray-700">
              No factors found. Please ensure you have loaded factor data using the ETL tool.
            </p>
          </div>
        )}
      </section>

      {/* Important Disclaimers */}
      <section className="bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded">
        <h3 className="font-semibold text-gray-900 mb-2">Important Disclaimers</h3>
        <ul className="text-sm text-gray-700 space-y-2">
          <li>• This data is for educational and research purposes only</li>
          <li>• Past performance does not guarantee future results</li>
          <li>• This is not investment advice or a recommendation to buy or sell securities</li>
          <li>• Factor returns shown are based on academic research and may not reflect actual investable returns</li>
          <li>• All data sourced from publicly available AQR research datasets</li>
        </ul>
      </section>
    </Layout>
  );
}
