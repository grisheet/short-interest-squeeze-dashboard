import React from 'react';
import { SqueezeScore } from '../types';

interface SqueezeScoreCardProps {
  score: SqueezeScore;
  compact?: boolean;
}

const gradeColors: Record<string, string> = {
  A: 'text-green-400 bg-green-900/30 border-green-600',
  B: 'text-blue-400 bg-blue-900/30 border-blue-600',
  C: 'text-yellow-400 bg-yellow-900/30 border-yellow-600',
  D: 'text-orange-400 bg-orange-900/30 border-orange-600',
  F: 'text-red-400 bg-red-900/30 border-red-600',
};

const ScoreBar: React.FC<{ label: string; value: number }> = ({ label, value }) => (
  <div className="space-y-1">
    <div className="flex justify-between text-xs">
      <span className="text-gray-400">{label}</span>
      <span className="text-gray-300 font-medium">{value}</span>
    </div>
    <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
      <div
        className="h-full rounded-full transition-all"
        style={{
          width: `${value}%`,
          background: value >= 70 ? '#22c55e' : value >= 40 ? '#eab308' : '#ef4444',
        }}
      />
    </div>
  </div>
);

const SqueezeScoreCard: React.FC<SqueezeScoreCardProps> = ({ score, compact = false }) => {
  const gradeClass = gradeColors[score.grade] || gradeColors.F;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <div className={`w-16 h-16 rounded-xl border-2 flex items-center justify-center font-bold text-2xl ${gradeClass}`}>
          {score.grade}
        </div>
        <div>
          <div className="text-3xl font-bold text-white">{score.score}</div>
          <div className="text-xs text-gray-400">Squeeze Score / 100</div>
        </div>
      </div>

      {!compact && (
        <div className="space-y-2">
          <ScoreBar label="Short Interest" value={score.components.shortInterestScore} />
          <ScoreBar label="Days to Cover" value={score.components.daysToCoverScore} />
          <ScoreBar label="Borrow Cost" value={score.components.borrowCostScore} />
          <ScoreBar label="Momentum" value={score.components.momentumScore} />
          <ScoreBar label="Float" value={score.components.floatScore} />
        </div>
      )}
    </div>
  );
};

export default SqueezeScoreCard;
