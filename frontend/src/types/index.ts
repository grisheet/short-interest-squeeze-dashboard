export interface ShortInterestData {
  symbol: string;
  companyName: string;
  shortInterest: number;
  shortPercentOfFloat: number;
  daysTocover: number;
  shortPercentOfSharesOutstanding: number;
  settleDate: string;
  dataSource: 'FINRA' | 'CALCULATED';
  dataFreshness: 'STALE' | 'RECENT';
  nextUpdateDate: string;
}

export interface SqueezeScore {
  symbol: string;
  score: number; // 0-100
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  components: {
    shortInterestScore: number;
    daysToCoverScore: number;
    borrowCostScore: number;
    momentumScore: number;
    floatScore: number;
  };
  lastCalculated: string;
}

export interface TickerSummary {
  symbol: string;
  companyName: string;
  price: number;
  priceChange: number;
  priceChangePercent: number;
  shortData: ShortInterestData;
  squeezeScore: SqueezeScore;
  borrowRate: number;
  marketCap: number;
  floatShares: number;
}

export interface Alert {
  id: string;
  symbol: string;
  type: 'SCORE_THRESHOLD' | 'SHORT_INCREASE' | 'DAYS_TO_COVER';
  threshold: number;
  active: boolean;
  createdAt: string;
}

export interface FilterOptions {
  minScore: number;
  maxDaysToCover: number;
  minShortPercent: number;
  sortBy: 'score' | 'shortPercent' | 'daysToCover' | 'symbol';
  sortOrder: 'asc' | 'desc';
}
