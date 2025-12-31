import { useState } from 'react';
import { SeverityBadge } from './SeverityBadge';
import type { AttackResult } from '../types';

interface AttackCardProps {
  result: AttackResult;
  isRunning?: boolean;
}

export function AttackCard({ result, isRunning = false }: AttackCardProps) {
  const [promptExpanded, setPromptExpanded] = useState(false);
  const [responseExpanded, setResponseExpanded] = useState(false);

  if (isRunning) {
    return (
      <div className="bg-surface border border-border animate-pulse-border p-4">
        <div className="flex items-center justify-between">
          <span className="font-mono text-sm text-text-primary">{result.attack_name}</span>
          <span className="text-text-secondary text-xs">Running...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface border border-border p-4 space-y-3">
      <div className="flex items-center justify-between gap-2">
        <span className="font-mono text-sm text-text-primary truncate flex-1">
          {result.attack_name}
        </span>
        <div className="flex items-center gap-2 flex-shrink-0">
          <SeverityBadge severity={result.severity} />
          <span
            className={`px-2 py-0.5 text-xs font-medium uppercase ${
              result.success
                ? 'bg-success text-black'
                : 'bg-failure text-white'
            }`}
          >
            {result.success ? 'Success' : 'Failed'}
          </span>
        </div>
      </div>

      {result.prompt && (
        <div>
          <button
            onClick={() => setPromptExpanded(!promptExpanded)}
            className="text-sm text-text-secondary hover:text-text-primary font-mono"
          >
            Prompt [{promptExpanded ? '-' : '+'}]
          </button>
          {promptExpanded && (
            <div className="mt-2 p-3 bg-[#0A0A0A] rounded font-mono text-sm text-text-secondary whitespace-pre-wrap break-words">
              {result.prompt}
            </div>
          )}
        </div>
      )}

      <div>
        <button
          onClick={() => setResponseExpanded(!responseExpanded)}
          className="text-sm text-text-secondary hover:text-text-primary font-mono"
        >
          Response [{responseExpanded ? '-' : '+'}]
        </button>
        {responseExpanded && (
          <div className="mt-2 p-3 bg-[#0A0A0A] rounded font-mono text-sm text-text-secondary whitespace-pre-wrap break-words">
            {result.response}
          </div>
        )}
      </div>

      <div className="flex items-center justify-between text-xs text-text-secondary">
        <div>
          {result.leak_types.length > 0 && (
            <span>
              Leaks: <span className="text-text-primary font-mono">{result.leak_types.join(', ')}</span>
            </span>
          )}
        </div>
        <div className="flex items-center gap-4">
          <span>
            Confidence: <span className="text-text-primary font-mono">{(result.confidence * 100).toFixed(0)}%</span>
          </span>
          <span>
            Latency: <span className="text-text-primary font-mono">{result.latency.toFixed(2)}s</span>
          </span>
        </div>
      </div>
    </div>
  );
}
