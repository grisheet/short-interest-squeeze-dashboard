import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useShortInterest } from '../hooks/useShortInterest';
import SqueezeScoreCard from './SqueezeScoreCard';

const DataRow: React.FC<{ label: string; value: string; tooltip?: string; highlight?: boolean }> = ({
  label, value, tooltip, highlight
}) => (
  <div className="flex justify-between items-center py-2 border-b border-gray-800 last:border-0">
    <span className="text-xs text-gray-400" title={tooltip}>{label}{tooltip && ' ℹ️'}</span>
    <span className={`text-sm font-semibold ${highlight ? 'text-amber-400' : 'text-white'}`}>{value}</span>
  </div>
);

const TickerDetail: React.FC = () => {
  const { symbol } = useParams<{ symbol: string }>();
  const { data, loading } = useShortInterest();
  const ticker = data.find(t => t.symbol === symbol?.toUpperCase());

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    );
  }

  if (!ticker) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-400 text-lg">Ticker <strong className="text-white">{symbol}</strong> not found.</p>
        <Link to="/" className="mt-4 inline-block text-blue-400 hover:underline">Back to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/" className="text-gray-400 hover:text-white">← Dashboard</Link>
        <span className="text-gray-600">/</span>
        <h2 className="text-2xl font-bold text-white">{ticker.symbol}</h2>
        <span className="text-gray-400">{ticker.companyName}</span>
      </div>

      {/* FINRA Disclosure */}
      <div className="bg-amber-900/20 border border-amber-700/50 rounded-xl p-3">
        <p className="text-amber-400 text-xs">
          ⚠️ Short interest data from FINRA, published twice monthly. Last settlement: {ticker.shortData.settleDate}.
          Next update: {ticker.shortData.nextUpdateDate}. Data may be stale.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Price Card */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Price Info</h3>
          <div className="text-4xl font-bold text-white mb-1">${ticker.price.toFixed(2)}</div>
          <div className={`text-sm ${ticker.priceChangePercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {ticker.priceChangePercent >= 0 ? '+' : ''}{ticker.priceChangePercent.toFixed(2)}% today
          </div>
          <div className="mt-4 space-y-0">
            <DataRow label="Market Cap" value={`$${(ticker.marketCap / 1e9).toFixed(2)}B`} />
            <DataRow label="Float Shares" value={`${(ticker.floatShares / 1e6).toFixed(1)}M`} />
            <DataRow label="Borrow Rate" value={`${ticker.borrowRate.toFixed(1)}%`} highlight={ticker.borrowRate > 50} tooltip="Annual cost to borrow shares for short selling" />
          </div>
        </div>

        {/* Squeeze Score Card */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Squeeze Score</h3>
          <SqueezeScoreCard score={ticker.squeezeScore} />
        </div>

        {/* Short Interest Card */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 md:col-span-2">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Short Interest Data
            <span className="ml-2 text-xs text-amber-400 font-normal">(FINRA - Twice Monthly)</span>
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-0">
            <DataRow label="Short Interest" value={`${(ticker.shortData.shortInterest / 1e6).toFixed(1)}M shares`} />
            <DataRow label="Short % of Float" value={`${ticker.shortData.shortPercentOfFloat.toFixed(1)}%`} />
            <DataRow
              label="Days to Cover"
              value={`${ticker.shortData.daysTocover.toFixed(1)} days`}
              tooltip="Days to Cover = Short Interest ÷ Average 20-Day Daily Volume. Higher = harder to cover quickly."
              highlight={ticker.shortData.daysTocover > 5}
            />
            <DataRow label="Short % Outstanding" value={`${ticker.shortData.shortPercentOfSharesOutstanding.toFixed(1)}%`} />
            <DataRow label="Settlement Date" value={ticker.shortData.settleDate} />
            <DataRow
              label="Data Status"
              value={ticker.shortData.dataFreshness}
              highlight={ticker.shortData.dataFreshness === 'STALE'}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TickerDetail;
