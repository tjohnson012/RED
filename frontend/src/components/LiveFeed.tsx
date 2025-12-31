import { AttackCard } from './AttackCard';
import type { AttackResult } from '../types';

interface LiveFeedProps {
  results: AttackResult[];
  currentAttackId: string | null;
  currentAttackName: string | null;
}

export function LiveFeed({ results, currentAttackId, currentAttackName }: LiveFeedProps) {
  if (results.length === 0 && !currentAttackId) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-text-secondary text-sm">Run an attack to see results</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-3">
      {currentAttackId && currentAttackName && (
        <AttackCard
          result={{
            attack_id: currentAttackId,
            attack_name: currentAttackName,
            category: '',
            success: false,
            confidence: 0,
            severity: 'none',
            leak_types: [],
            evidence: [],
            response: '',
            latency: 0,
          }}
          isRunning={true}
        />
      )}
      {results.map((result, index) => (
        <AttackCard key={`${result.attack_id}-${index}`} result={result} />
      ))}
    </div>
  );
}
