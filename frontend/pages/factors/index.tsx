/**
 * Factors directory page with filtering and sorting
 */
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import FactorCard from '@/components/FactorCard';
import FactorCardSkeleton from '@/components/FactorCardSkeleton';
import { factorApi, metadataApi } from '@/lib/api';
import type { Factor } from '@/types';
import { formatPercent, getValueColor } from '@/lib/utils';

export default function FactorsPage() {
  const router = useRouter();
  const [factors, setFactors] = useState<Factor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('');
  const [selectedFrequency, setSelectedFrequency] = useState('');
  const [selectedAssetClass, setSelectedAssetClass] = useState('');

  // Metadata
  const [regions, setRegions] = useState<string[]>([]);
  const [frequencies, setFrequencies] = useState<string[]>([]);
  const [assetClasses, setAssetClasses] = useState<string[]>([]);

  useEffect(() => {
    loadMetadata();
  }, []);

  useEffect(() => {
    // Check URL parameters
    const { search } = router.query;
    if (search && typeof search === 'string') {
      setSearchQuery(search);
    }
  }, [router.query]);

  useEffect(() => {
    loadFactors();
  }, [searchQuery, selectedRegion, selectedFrequency, selectedAssetClass]);

  const loadMetadata = async () => {
    try {
      const [regionsData, frequenciesData, assetClassesData] = await Promise.all([
        metadataApi.getRegions(),
        metadataApi.getFrequencies(),
        metadataApi.getAssetClasses()
      ]);

      setRegions(regionsData);
      setFrequencies(frequenciesData);
      setAssetClasses(assetClassesData);
    } catch (error) {
      console.error('Error loading metadata:', error);
      // Metadata errors are non-critical, continue with empty arrays
    }
  };

  const loadFactors = async () => {
    try {
      setLoading(true);
      setError(null);

      const params: any = { limit: 100 };

      if (searchQuery) params.search = searchQuery;
      if (selectedRegion) params.region = selectedRegion;
      if (selectedFrequency) params.frequency = selectedFrequency;
      if (selectedAssetClass) params.asset_class = selectedAssetClass;

      const data = await factorApi.list(params);

      // Validate response is an array
      if (!Array.isArray(data)) {
        throw new Error('Invalid response format from API');
      }

      setFactors(data);
    } catch (error) {
      console.error('Error loading factors:', error);
      setError(error instanceof Error ? error.message : 'Failed to load factors. Please try again.');
      setFactors([]);
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedRegion('');
    setSelectedFrequency('');
    setSelectedAssetClass('');
    setError(null);
  };

  const activeFiltersCount = [
    searchQuery,
    selectedRegion,
    selectedFrequency,
    selectedAssetClass
  ].filter(Boolean).length;

  return (
    <Layout
      title="Factor Directory - AQR Factor Explorer"
      description="Browse and filter through all available AQR factors. Compare performance metrics, regions, and asset classes."
    >
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Factor Directory</h1>
        <p className="text-gray-600">
          Browse and filter {factors.length} factors from AQR's research library
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
          {activeFiltersCount > 0 && (
            <button
              onClick={clearFilters}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              Clear All ({activeFiltersCount})
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search
            </label>
            <input
              type="text"
              placeholder="Factor name or code..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {/* Region Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Region
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
            >
              <option value="">All Regions</option>
              {regions.map(region => (
                <option key={region} value={region}>{region}</option>
              ))}
            </select>
          </div>

          {/* Frequency Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Frequency
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={selectedFrequency}
              onChange={(e) => setSelectedFrequency(e.target.value)}
            >
              <option value="">All Frequencies</option>
              {frequencies.map(freq => (
                <option key={freq} value={freq}>{freq}</option>
              ))}
            </select>
          </div>

          {/* Asset Class Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Asset Class
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={selectedAssetClass}
              onChange={(e) => setSelectedAssetClass(e.target.value)}
            >
              <option value="">All Asset Classes</option>
              {assetClasses.map(ac => (
                <option key={ac} value={ac}>{ac}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* View Mode Toggle */}
      <div className="flex justify-between items-center mb-6">
        <p className="text-gray-600">
          {loading ? 'Loading...' : `${factors.length} factors found`}
        </p>
        <div className="flex gap-2">
          <button
            className={`px-4 py-2 rounded-md font-medium ${viewMode === 'grid'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            onClick={() => setViewMode('grid')}
          >
            Grid
          </button>
          <button
            className={`px-4 py-2 rounded-md font-medium ${viewMode === 'table'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            onClick={() => setViewMode('table')}
          >
            Table
          </button>
        </div>
      </div>

      {/* Results */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <FactorCardSkeleton key={i} />
          ))}
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
          <div className="text-red-600 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Factors</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => loadFactors()}
            className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      ) : factors.length > 0 ? (
        viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {factors.map(factor => (
              <FactorCard key={factor.id} factor={factor} />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Factor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Region
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Frequency
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ann. Return
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Volatility
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Sharpe
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Max DD
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {factors.map(factor => (
                    <tr
                      key={factor.id}
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => router.push(`/factor/${factor.id}`)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{factor.name}</div>
                        <div className="text-xs text-gray-500 font-mono">{factor.code}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {factor.region || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {factor.frequency || 'N/A'}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-medium ${getValueColor(factor.annualized_return)}`}>
                        {formatPercent(factor.annualized_return)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                        {formatPercent(factor.annualized_volatility)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                        {factor.sharpe_ratio?.toFixed(2) || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-finance-negative">
                        {formatPercent(factor.max_drawdown)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )
      ) : (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No factors found
          </h3>
          <p className="text-gray-600 mb-4">
            {activeFiltersCount > 0
              ? 'Try adjusting your filters to see more results.'
              : 'No factors available in the database.'}
          </p>
          {activeFiltersCount > 0 && (
            <button
              onClick={clearFilters}
              className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
            >
              Clear All Filters
            </button>
          )}
        </div>
      )}
    </Layout>
  );
}
