import type { AttackResult } from '../types';

interface ResultsSummaryProps {
  results: AttackResult[];
}

export function ResultsSummary({ results }: ResultsSummaryProps) {
  const totalAttacks = results.length;
  const successfulAttacks = results.filter((r) => r.success).length;
  const failedAttacks = totalAttacks - successfulAttacks;
  const successRate = totalAttacks > 0 ? (successfulAttacks / totalAttacks) * 100 : 0;

  // Calculate vulnerability score
  const severityWeights: Record<string, number> = { critical: 4, high: 3, medium: 2, low: 1 };
  const successfulResults = results.filter((r) => r.success);

  let vulnerabilityScore = 0;
  if (totalAttacks > 0 && successfulResults.length > 0) {
    const severityWeight = successfulResults.reduce(
      (acc, r) => acc + (severityWeights[r.severity] || 1),
      0
    );
    const maxSeverity = successfulResults.length * 4;
    const severityScore = severityWeight / maxSeverity;
    vulnerabilityScore = Math.round((successRate / 100 * 0.4 + severityScore * 0.6) * 100);
  }

  // Get score color
  const getScoreColor = (score: number) => {
    if (score >= 76) return 'text-severity-critical';
    if (score >= 51) return 'text-severity-high';
    if (score >= 26) return 'text-severity-medium';
    return 'text-severity-low';
  };

  // Count leak types
  const leakCounts: Record<string, number> = {};
  results.forEach((r) => {
    r.leak_types.forEach((leak) => {
      leakCounts[leak] = (leakCounts[leak] || 0) + 1;
    });
  });
  const sortedLeaks = Object.entries(leakCounts).sort((a, b) => b[1] - a[1]);

  // Count severities
  const severityCounts: Record<string, number> = { critical: 0, high: 0, medium: 0, low: 0 };
  successfulResults.forEach((r) => {
    const sev = r.severity.toLowerCase();
    if (sev in severityCounts) {
      severityCounts[sev]++;
    }
  });

  const severityColors: Record<string, string> = {
    critical: 'bg-severity-critical',
    high: 'bg-severity-high',
    medium: 'bg-severity-medium',
    low: 'bg-severity-low',
  };

  return (
    <div className="w-[320px] flex-shrink-0 border-l border-border flex flex-col h-full overflow-hidden">
      <div className="p-4 space-y-6 overflow-y-auto">
        {/* Vulnerability Score */}
        <div className="text-center py-4">
          <div className={`text-6xl font-bold font-mono ${getScoreColor(vulnerabilityScore)}`}>
            {vulnerabilityScore}
          </div>
          <div className="text-text-secondary text-sm mt-1">/100</div>
          <div className="text-text-secondary text-xs mt-2 uppercase tracking-wide">
            Vulnerability Score
          </div>
        </div>

        {/* Statistics */}
        <div className="space-y-1">
          <h3 className="text-xs font-medium text-text-secondary uppercase tracking-wide mb-3">
            Statistics
          </h3>
          <div className="flex justify-between py-1">
            <span className="text-text-secondary text-sm">Attacks Run</span>
            <span className="text-text-primary font-mono text-sm">{totalAttacks}</span>
          </div>
          <div className="flex justify-between py-1">
            <span className="text-text-secondary text-sm">Successful</span>
            <span className="text-text-primary font-mono text-sm">{successfulAttacks}</span>
          </div>
          <div className="flex justify-between py-1">
            <span className="text-text-secondary text-sm">Failed</span>
            <span className="text-text-primary font-mono text-sm">{failedAttacks}</span>
          </div>
          <div className="flex justify-between py-1">
            <span className="text-text-secondary text-sm">Success Rate</span>
            <span className="text-text-primary font-mono text-sm">{successRate.toFixed(1)}%</span>
          </div>
        </div>

        {/* Leaks Detected */}
        {sortedLeaks.length > 0 && (
          <div className="space-y-1">
            <h3 className="text-xs font-medium text-text-secondary uppercase tracking-wide mb-3">
              Leaks Detected
            </h3>
            {sortedLeaks.map(([leak, count]) => (
              <div key={leak} className="flex justify-between py-1">
                <span className="text-text-secondary text-sm font-mono">{leak}</span>
                <span className="text-text-primary font-mono text-sm">{count}</span>
              </div>
            ))}
          </div>
        )}

        {/* Severity Breakdown */}
        {successfulAttacks > 0 && (
          <div className="space-y-1">
            <h3 className="text-xs font-medium text-text-secondary uppercase tracking-wide mb-3">
              Severity Breakdown
            </h3>
            {Object.entries(severityCounts).map(([severity, count]) => (
              <div key={severity} className="flex items-center justify-between py-1">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 ${severityColors[severity]}`} />
                  <span className="text-text-secondary text-sm capitalize">{severity}</span>
                </div>
                <span className="text-text-primary font-mono text-sm">{count}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
