import React, { useState } from 'react';
import { useShortInterest } from '../hooks/useShortInterest';
import TickerTable from './TickerTable';

const StatCard: React.FC<{ label: string; value: string; sub?: string; color?: string }> = ({ label, value, sub, color = 'text-white' }) => (
  <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
    <p className="text-xs text-gray-400 font-medium uppercase tracking-wider">{label}</p>
    <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
    {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
  </div>
);

const Dashboard: React.FC = () => {
  const [minScore, setMinScore] = useState(0);
  const [minShortPercent, setMinShortPercent] = useState(0);

  const { data, loading, error, refetch } = useShortInterest({ minScore, minShortPercent });

  const avgScore = data.length ? Math.round(data.reduce((s, t) => s + t.squeezeScore.score, 0) / data.length) : 0;
  const topCandidate = data.reduce((best, t) => t.squeezeScore.score > (best?.squeezeScore.score ?? 0) ? t : best, data[0]);
  const staleCount = data.filter(t => t.shortData.dataFreshness === 'STALE').length;

  return (
    <div className="space-y-6">
      {/* FINRA Data Warning Banner */}
      <div className="bg-amber-900/20 border border-amber-700/50 rounded-xl p-4 flex items-start gap-3">
        <span className="text-amber-400 text-xl mt-0.5">⚠️</span>
        <div>
          <p className="text-amber-400 font-semibold text-sm">FINRA Short Interest Data Disclosure</p>
          <p className="text-gray-400 text-xs mt-1">
            Short interest data is sourced from FINRA and published twice monthly (mid-month and end-of-month).
            Data shown may be <strong className="text-amber-300">1 to 14 days stale</strong>.
            Days-to-cover is calculated as: <code className="text-blue-300">Short Interest ÷ Average 20-Day Volume</code>.
            This is not financial advice.
          </p>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Tracked Tickers" value={data.length.toString()} sub="Active short positions" />
        <StatCard label="Avg Squeeze Score" value={avgScore.toString()} color={avgScore >= 70 ? 'text-green-400' : avgScore >= 40 ? 'text-yellow-400' : 'text-red-400'} />
        <StatCard label="Top Candidate" value={topCandidate?.symbol ?? '-'} sub={topCandidate ? `Score: ${topCandidate.squeezeScore.score}` : ''} color="text-blue-400" />
        <StatCard label="Stale Data" value={`${staleCount}/${data.length}`} sub="FINRA twice-monthly" color="text-amber-400" />
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center bg-gray-900 border border-gray-800 rounded-xl p-4">
        <div className="flex items-center gap-2">
          <label className="text-xs text-gray-400">Min Score:</label>
          <input
            type="range" min="0" max="100" value={minScore}
            onChange={e => setMinScore(Number(e.target.value))}
            className="w-24 accent-blue-500"
          />
          <span className="text-xs text-white w-8">{minScore}</span>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-xs text-gray-400">Min Short %:</label>
          <input
            type="range" min="0" max="100" value={minShortPercent}
            onChange={e => setMinShortPercent(Number(e.target.value))}
            className="w-24 accent-blue-500"
          />
          <span className="text-xs text-white w-8">{minShortPercent}%</span>
        </div>
        <button
          onClick={refetch}
          className="ml-auto px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition-colors"
        >
          Refresh Data
        </button>
      </div>

      {error && (
        <div className="bg-blue-900/20 border border-blue-700/50 rounded-xl p-3">
          <p className="text-blue-400 text-xs">ℹ️ Demo mode: showing sample data. Connect the FastAPI backend for live FINRA data.</p>
        </div>
      )}

      <TickerTable data={data} loading={loading} />
    </div>
  );
};

export default Dashboard;
