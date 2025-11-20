/**
 * Custom hook for managing factor filter state
 */
import { useState, useMemo } from 'react';

export interface FactorFilters {
    searchQuery: string;
    selectedRegion: string;
    selectedFrequency: string;
    selectedAssetClass: string;
}

export interface UseFactorFiltersReturn {
    filters: FactorFilters;
    setSearchQuery: (value: string) => void;
    setSelectedRegion: (value: string) => void;
    setSelectedFrequency: (value: string) => void;
    setSelectedAssetClass: (value: string) => void;
    clearFilters: () => void;
    activeFiltersCount: number;
}

export function useFactorFilters(): UseFactorFiltersReturn {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedRegion, setSelectedRegion] = useState('');
    const [selectedFrequency, setSelectedFrequency] = useState('');
    const [selectedAssetClass, setSelectedAssetClass] = useState('');

    const clearFilters = () => {
        setSearchQuery('');
        setSelectedRegion('');
        setSelectedFrequency('');
        setSelectedAssetClass('');
    };

    const activeFiltersCount = useMemo(() => {
        return [
            searchQuery,
            selectedRegion,
            selectedFrequency,
            selectedAssetClass
        ].filter(Boolean).length;
    }, [searchQuery, selectedRegion, selectedFrequency, selectedAssetClass]);

    return {
        filters: {
            searchQuery,
            selectedRegion,
            selectedFrequency,
            selectedAssetClass
        },
        setSearchQuery,
        setSelectedRegion,
        setSelectedFrequency,
        setSelectedAssetClass,
        clearFilters,
        activeFiltersCount
    };
}
