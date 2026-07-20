import { useState, useEffect, useCallback } from 'react';
import { TickerSummary, FilterOptions } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Mock data for GitHub Pages demo (no backend needed)
const MOCK_DATA: TickerSummary[] = [
  {
    symbol: 'GME',
    companyName: 'GameStop Corp.',
    price: 14.52,
    priceChange: 0.87,
    priceChangePercent: 6.37,
    borrowRate: 12.5,
    marketCap: 4400000000,
    floatShares: 232000000,
    shortData: {
      symbol: 'GME',
      companyName: 'GameStop Corp.',
      shortInterest: 61000000,
      shortPercentOfFloat: 26.3,
      daysTocover: 3.2,
      shortPercentOfSharesOutstanding: 18.5,
      settleDate: '2024-01-15',
      dataSource: 'FINRA',
      dataFreshness: 'STALE',
      nextUpdateDate: '2024-02-01',
    },
    squeezeScore: {
      symbol: 'GME',
      score: 78,
      grade: 'B',
      components: { shortInterestScore: 85, daysToCoverScore: 60, borrowCostScore: 70, momentumScore: 80, floatScore: 75 },
      lastCalculated: new Date().toISOString(),
    },
  },
  {
    symbol: 'AMC',
    companyName: 'AMC Entertainment Holdings',
    price: 4.21,
    priceChange: -0.15,
    priceChangePercent: -3.44,
    borrowRate: 35.2,
    marketCap: 2100000000,
    floatShares: 270000000,
    shortData: {
      symbol: 'AMC',
      companyName: 'AMC Entertainment Holdings',
      shortInterest: 80000000,
      shortPercentOfFloat: 29.6,
      daysTocover: 2.8,
      shortPercentOfSharesOutstanding: 16.2,
      settleDate: '2024-01-15',
      dataSource: 'FINRA',
      dataFreshness: 'STALE',
      nextUpdateDate: '2024-02-01',
    },
    squeezeScore: {
      symbol: 'AMC',
      score: 82,
      grade: 'B',
      components: { shortInterestScore: 90, daysToCoverScore: 65, borrowCostScore: 88, momentumScore: 70, floatScore: 72 },
      lastCalculated: new Date().toISOString(),
    },
  },
  {
    symbol: 'BBBY',
    companyName: 'Bed Bath & Beyond Inc.',
    price: 0.21,
    priceChange: 0.02,
    priceChangePercent: 10.53,
    borrowRate: 125.0,
    marketCap: 45000000,
    floatShares: 380000000,
    shortData: {
      symbol: 'BBBY',
      companyName: 'Bed Bath & Beyond Inc.',
      shortInterest: 95000000,
      shortPercentOfFloat: 25.0,
      daysTocover: 1.2,
      shortPercentOfSharesOutstanding: 12.5,
      settleDate: '2024-01-15',
      dataSource: 'FINRA',
      dataFreshness: 'STALE',
      nextUpdateDate: '2024-02-01',
    },
    squeezeScore: {
      symbol: 'BBBY',
      score: 91,
      grade: 'A',
      components: { shortInterestScore: 95, daysToCoverScore: 40, borrowCostScore: 99, momentumScore: 90, floatScore: 88 },
      lastCalculated: new Date().toISOString(),
    },
  },
];

export const useShortInterest = (filters?: Partial<FilterOptions>) => {
  const [data, setData] = useState<TickerSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/tickers/summary`);
      if (!res.ok) throw new Error('API unavailable');
      const json = await res.json();
      setData(json);
    } catch {
      // Fall back to mock data for demo/GitHub Pages
      setData(MOCK_DATA);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const filtered = data.filter(t => {
    if (filters?.minScore && t.squeezeScore.score < filters.minScore) return false;
    if (filters?.minShortPercent && t.shortData.shortPercentOfFloat < filters.minShortPercent) return false;
    return true;
  });

  return { data: filtered, loading, error, refetch: fetchData };
};
