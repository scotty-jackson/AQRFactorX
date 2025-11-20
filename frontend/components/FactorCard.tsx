/**
 * Factor card component for displaying factor summary
 */
import React from 'react';
import Link from 'next/link';
import { Factor } from '@/types';
import { formatPercent, formatDate, getValueColor } from '@/lib/utils';

interface FactorCardProps {
  factor: Factor;
}

export default function FactorCard({ factor }: FactorCardProps) {
  return (
    <Link href={`/factor/${factor.id}`}>
      <div className="bg-white p-5 rounded-lg shadow hover:shadow-lg transition-shadow border border-gray-200 cursor-pointer">
        <div className="flex justify-between items-start gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-lg text-gray-900 break-words line-clamp-2">{factor.name}</h3>
            <p className="text-sm text-gray-500 font-mono truncate">{factor.code}</p>
          </div>
          <span className="px-2 py-1 text-xs bg-primary-100 text-primary-700 rounded whitespace-nowrap flex-shrink-0">
            {factor.region || 'N/A'}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-3">
          <div title="Annualized Return: Average yearly return of the factor">
            <p className="text-xs text-gray-500">Ann. Return</p>
            <p className={`text-sm font-semibold ${getValueColor(factor.annualized_return)}`}>
              {formatPercent(factor.annualized_return)}
            </p>
          </div>
          <div title="Volatility: Standard deviation of returns, measuring risk">
            <p className="text-xs text-gray-500">Volatility</p>
            <p className="text-sm font-semibold text-gray-700">
              {formatPercent(factor.annualized_volatility)}
            </p>
          </div>
          <div title="Sharpe Ratio: Risk-adjusted return (return per unit of risk)">
            <p className="text-xs text-gray-500">Sharpe Ratio</p>
            <p className="text-sm font-semibold text-gray-700">
              {factor.sharpe_ratio?.toFixed(2) || 'N/A'}
            </p>
          </div>
          <div title="Maximum Drawdown: Largest peak-to-trough decline">
            <p className="text-xs text-gray-500">Max DD</p>
            <p className="text-sm font-semibold text-finance-negative">
              {formatPercent(factor.max_drawdown)}
            </p>
          </div>
        </div>

        <div className="flex justify-between items-center pt-3 border-t border-gray-100">
          <div>
            <p className="text-xs text-gray-500">Frequency</p>
            <p className="text-xs font-medium text-gray-700">{factor.frequency || 'N/A'}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500">Data Range</p>
            <p className="text-xs font-medium text-gray-700">
              {formatDate(factor.first_date)} - {formatDate(factor.last_date)}
            </p>
          </div>
        </div>
      </div>
    </Link>
  );
}
