import { useEffect, useState, useCallback } from 'react';
import { Header } from './components/Header';
import { AttackPanel } from './components/AttackPanel';
import { LiveFeed } from './components/LiveFeed';
import { ResultsSummary } from './components/ResultsSummary';
import { checkHealth, getAttacks, runSingleAttack, runAssessment, resetSession, runCustomAttack } from './api';
import type { Attack, ChainAttack, AttackResult } from './types';

export function App() {
  const [backendConnected, setBackendConnected] = useState(false);
  const [attacks, setAttacks] = useState<Attack[]>([]);
  const [chainAttacks, setChainAttacks] = useState<ChainAttack[]>([]);
  const [results, setResults] = useState<AttackResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [currentAttackId, setCurrentAttackId] = useState<string | null>(null);
  const [currentAttackName, setCurrentAttackName] = useState<string | null>(null);
  const [runningCount, setRunningCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // Check backend health
  const checkBackendHealth = useCallback(async () => {
    try {
      await checkHealth();
      setBackendConnected(true);
      setError(null);
    } catch {
      setBackendConnected(false);
    }
  }, []);

  // Load attacks on mount
  useEffect(() => {
    const init = async () => {
      await checkBackendHealth();
      try {
        const data = await getAttacks();
        setAttacks(data.single_attacks);
        setChainAttacks(data.chain_attacks);
      } catch (e) {
        setError('Failed to load attacks');
      }
    };
    init();

    // Check health every 30 seconds
    const interval = setInterval(checkBackendHealth, 30000);
    return () => clearInterval(interval);
  }, [checkBackendHealth]);

  // Run full assessment
  const handleRunAssessment = async () => {
    if (isRunning) return;

    setIsRunning(true);
    setResults([]);
    setError(null);
    setTotalCount(attacks.length + chainAttacks.length);
    setRunningCount(0);

    try {
      // Run attacks one by one to show progress
      for (let i = 0; i < attacks.length; i++) {
        const attack = attacks[i];
        setCurrentAttackId(attack.id);
        setCurrentAttackName(attack.name);
        setRunningCount(i + 1);

        try {
          const result = await runSingleAttack(attack.id);
          setResults((prev) => [result, ...prev]);
        } catch (e) {
          console.error(`Failed to run attack ${attack.id}:`, e);
        }
      }

      setCurrentAttackId(null);
      setCurrentAttackName(null);
    } catch (e) {
      setError('Assessment failed');
    } finally {
      setIsRunning(false);
      setCurrentAttackId(null);
      setCurrentAttackName(null);
    }
  };

  // Run single attack
  const handleRunSingleAttack = async (attackId: string) => {
    if (isRunning) return;

    const attack = attacks.find((a) => a.id === attackId);
    if (!attack) return;

    setIsRunning(true);
    setCurrentAttackId(attackId);
    setCurrentAttackName(attack.name);
    setError(null);

    try {
      const result = await runSingleAttack(attackId);
      setResults((prev) => [result, ...prev]);
    } catch (e) {
      setError(`Failed to run attack: ${attackId}`);
    } finally {
      setIsRunning(false);
      setCurrentAttackId(null);
      setCurrentAttackName(null);
    }
  };

  // Reset session
  const handleReset = async () => {
    if (isRunning) return;

    try {
      await resetSession();
      setResults([]);
      setError(null);
    } catch (e) {
      setError('Failed to reset session');
    }
  };

  // Run custom attack
  const handleCustomAttack = async (prompt: string, name: string) => {
    if (isRunning) return;

    setIsRunning(true);
    setCurrentAttackId('custom');
    setCurrentAttackName(name);
    setError(null);

    try {
      const result = await runCustomAttack(prompt, name);
      setResults((prev) => [result, ...prev]);
    } catch (e) {
      setError('Failed to run custom attack');
    } finally {
      setIsRunning(false);
      setCurrentAttackId(null);
      setCurrentAttackName(null);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      <Header connected={backendConnected} />

      {error && (
        <div className="px-6 py-2 bg-red-primary/10 border-b border-red-primary">
          <span className="text-red-primary text-sm">{error}</span>
        </div>
      )}

      <div className="flex-1 flex overflow-hidden">
        <AttackPanel
          attacks={attacks}
          chainAttacks={chainAttacks}
          isRunning={isRunning}
          currentAttackId={currentAttackId}
          runningCount={runningCount}
          totalCount={totalCount || attacks.length}
          onRunAssessment={handleRunAssessment}
          onRunSingleAttack={handleRunSingleAttack}
          onCustomAttack={handleCustomAttack}
          onReset={handleReset}
        />

        <LiveFeed
          results={results}
          currentAttackId={currentAttackId}
          currentAttackName={currentAttackName}
        />

        <ResultsSummary results={results} />
      </div>
    </div>
  );
}
