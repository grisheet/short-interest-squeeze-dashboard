import React from 'react';
import { Link } from 'react-router-dom';
import { TickerSummary } from '../types';

interface TickerTableProps {
  data: TickerSummary[];
  loading: boolean;
}

const gradeColor: Record<string, string> = {
  A: 'text-green-400', B: 'text-blue-400', C: 'text-yellow-400', D: 'text-orange-400', F: 'text-red-400',
};

const TickerTable: React.FC<TickerTableProps> = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-800">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-gray-900 border-b border-gray-800">
            <th className="text-left px-4 py-3 text-gray-400 font-semibold">Symbol</th>
            <th className="text-right px-4 py-3 text-gray-400 font-semibold">Price</th>
            <th className="text-right px-4 py-3 text-gray-400 font-semibold">Short % Float</th>
            <th className="text-right px-4 py-3 text-gray-400 font-semibold"
              title="Days to Cover = Short Interest / Avg 20-Day Volume">
              Days to Cover
            </th>
            <th className="text-right px-4 py-3 text-gray-400 font-semibold">Borrow Rate</th>
            <th className="text-center px-4 py-3 text-gray-400 font-semibold">Score</th>
            <th className="text-center px-4 py-3 text-gray-400 font-semibold">Data Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800">
          {data.map((ticker) => (
            <tr key={ticker.symbol} className="bg-gray-950 hover:bg-gray-900 transition-colors">
              <td className="px-4 py-3">
                <Link to={`/ticker/${ticker.symbol}`} className="hover:underline">
                  <div className="font-bold text-white">{ticker.symbol}</div>
                  <div className="text-xs text-gray-500 truncate max-w-[160px]">{ticker.companyName}</div>
                </Link>
              </td>
              <td className="px-4 py-3 text-right">
                <div className="text-white">${ticker.price.toFixed(2)}</div>
                <div className={`text-xs ${ticker.priceChangePercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {ticker.priceChangePercent >= 0 ? '+' : ''}{ticker.priceChangePercent.toFixed(2)}%
                </div>
              </td>
              <td className="px-4 py-3 text-right text-white">
                {ticker.shortData.shortPercentOfFloat.toFixed(1)}%
              </td>
              <td className="px-4 py-3 text-right">
                <span className={`text-white ${ticker.shortData.daysTocover > 5 ? 'font-bold text-amber-400' : ''}`}>
                  {ticker.shortData.daysTocover.toFixed(1)}d
                </span>
              </td>
              <td className="px-4 py-3 text-right">
                <span className={ticker.borrowRate > 50 ? 'text-red-400 font-bold' : 'text-white'}>
                  {ticker.borrowRate.toFixed(1)}%
                </span>
              </td>
              <td className="px-4 py-3 text-center">
                <span className={`font-bold text-lg ${gradeColor[ticker.squeezeScore.grade]}`}>
                  {ticker.squeezeScore.score}
                </span>
                <span className={`ml-1 text-xs ${gradeColor[ticker.squeezeScore.grade]}`}>
                  ({ticker.squeezeScore.grade})
                </span>
              </td>
              <td className="px-4 py-3 text-center">
                <span className={`text-xs px-2 py-0.5 rounded-full border ${
                  ticker.shortData.dataFreshness === 'STALE'
                    ? 'text-amber-400 border-amber-600 bg-amber-900/20'
                    : 'text-green-400 border-green-600 bg-green-900/20'
                }`}>
                  {ticker.shortData.dataFreshness === 'STALE' ? '⚠ STALE' : '✓ RECENT'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TickerTable;
