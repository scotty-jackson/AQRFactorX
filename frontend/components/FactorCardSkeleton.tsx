/**
 * Skeleton loading component for factor cards
 */
import React from 'react';

export default function FactorCardSkeleton() {
    return (
        <div className="bg-white p-5 rounded-lg shadow border border-gray-200 animate-pulse">
            <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                    <div className="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-4 bg-gray-100 rounded w-1/2"></div>
                </div>
                <div className="h-6 w-16 bg-gray-200 rounded"></div>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-3">
                <div>
                    <div className="h-3 bg-gray-100 rounded w-20 mb-1"></div>
                    <div className="h-4 bg-gray-200 rounded w-16"></div>
                </div>
                <div>
                    <div className="h-3 bg-gray-100 rounded w-20 mb-1"></div>
                    <div className="h-4 bg-gray-200 rounded w-16"></div>
                </div>
                <div>
                    <div className="h-3 bg-gray-100 rounded w-24 mb-1"></div>
                    <div className="h-4 bg-gray-200 rounded w-12"></div>
                </div>
                <div>
                    <div className="h-3 bg-gray-100 rounded w-16 mb-1"></div>
                    <div className="h-4 bg-gray-200 rounded w-16"></div>
                </div>
            </div>

            <div className="flex justify-between items-center pt-3 border-t border-gray-100">
                <div>
                    <div className="h-3 bg-gray-100 rounded w-16 mb-1"></div>
                    <div className="h-3 bg-gray-200 rounded w-20"></div>
                </div>
                <div className="text-right">
                    <div className="h-3 bg-gray-100 rounded w-20 mb-1 ml-auto"></div>
                    <div className="h-3 bg-gray-200 rounded w-32 ml-auto"></div>
                </div>
            </div>
        </div>
    );
}
