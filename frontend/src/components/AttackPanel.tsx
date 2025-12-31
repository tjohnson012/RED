import { useState } from 'react';
import { SeverityBadge } from './SeverityBadge';
import type { Attack, ChainAttack } from '../types';

interface AttackPanelProps {
  attacks: Attack[];
  chainAttacks: ChainAttack[];
  isRunning: boolean;
  currentAttackId: string | null;
  runningCount: number;
  totalCount: number;
  onRunAssessment: () => void;
  onRunSingleAttack: (attackId: string) => void;
  onCustomAttack: (prompt: string, name: string) => void;
  onReset: () => void;
}

interface CategoryGroup {
  name: string;
  attacks: Attack[];
}

export function AttackPanel({
  attacks,
  chainAttacks,
  isRunning,
  runningCount,
  totalCount,
  onRunAssessment,
  onRunSingleAttack,
  onCustomAttack,
  onReset,
}: AttackPanelProps) {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [showCustom, setShowCustom] = useState(false);
  const [customPrompt, setCustomPrompt] = useState('');
  const [customName, setCustomName] = useState('');

  const categories: CategoryGroup[] = attacks.reduce((acc: CategoryGroup[], attack) => {
    const existing = acc.find((c) => c.name === attack.category);
    if (existing) {
      existing.attacks.push(attack);
    } else {
      acc.push({ name: attack.category, attacks: [attack] });
    }
    return acc;
  }, []);

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  const formatCategoryName = (name: string) => {
    return name.charAt(0).toUpperCase() + name.slice(1) + 's';
  };

  const handleRunCustom = () => {
    if (!customPrompt.trim()) return;
    onCustomAttack(customPrompt, customName.trim() || 'Custom Attack');
    setCustomPrompt('');
    setCustomName('');
    setShowCustom(false);
  };

  return (
    <div className="w-[280px] flex-shrink-0 border-r border-border flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-border space-y-2">
        <button
          onClick={onRunAssessment}
          disabled={isRunning}
          className={`w-full h-11 font-medium text-sm transition-colors ${
            isRunning
              ? 'bg-red-primary/50 text-white/50 cursor-not-allowed'
              : 'bg-red-primary text-white hover:bg-red-hover'
          }`}
        >
          {isRunning ? `Running... (${runningCount}/${totalCount})` : 'Run Full Assessment'}
        </button>

        <button
          onClick={() => setShowCustom(!showCustom)}
          disabled={isRunning}
          className={`w-full h-9 text-sm font-mono border transition-colors ${
            isRunning
              ? 'border-border text-text-secondary/50 cursor-not-allowed'
              : showCustom
              ? 'border-red-primary text-red-primary bg-red-primary/10'
              : 'border-border text-text-secondary hover:border-text-secondary hover:text-text-primary'
          }`}
        >
          {showCustom ? '[-] Custom Attack' : '[+] Custom Attack'}
        </button>

        {showCustom && (
          <div className="space-y-2 pt-1">
            <input
              type="text"
              value={customName}
              onChange={(e) => setCustomName(e.target.value)}
              placeholder="Attack name (optional)"
              disabled={isRunning}
              className="w-full h-8 px-2 bg-background border border-border text-text-primary text-xs font-mono placeholder:text-text-secondary/50 focus:outline-none focus:border-text-secondary disabled:opacity-50"
            />
            <textarea
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              placeholder="Enter adversarial prompt..."
              disabled={isRunning}
              rows={4}
              className="w-full px-2 py-2 bg-background border border-border text-text-primary text-xs font-mono placeholder:text-text-secondary/50 focus:outline-none focus:border-text-secondary resize-none disabled:opacity-50"
            />
            <button
              onClick={handleRunCustom}
              disabled={isRunning || !customPrompt.trim()}
              className={`w-full h-9 text-sm font-medium transition-colors ${
                isRunning || !customPrompt.trim()
                  ? 'bg-red-primary/30 text-white/50 cursor-not-allowed'
                  : 'bg-red-primary text-white hover:bg-red-hover'
              }`}
            >
              Execute
            </button>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="p-4 space-y-2">
          <h3 className="text-xs font-medium text-text-secondary uppercase tracking-wide mb-3">
            Attack Categories
          </h3>

          {categories.map((category) => (
            <div key={category.name} className="border border-border">
              <button
                onClick={() => toggleCategory(category.name)}
                className="w-full px-3 py-2 flex items-center justify-between text-left hover:bg-surface/50 transition-colors"
              >
                <span className="text-sm text-text-primary">
                  {formatCategoryName(category.name)} ({category.attacks.length})
                </span>
                <span className="text-text-secondary text-xs">
                  {expandedCategories.has(category.name) ? '[-]' : '[+]'}
                </span>
              </button>

              {expandedCategories.has(category.name) && (
                <div className="border-t border-border">
                  {category.attacks.map((attack) => (
                    <div
                      key={attack.id}
                      className="px-3 py-2 flex items-center justify-between gap-2 hover:bg-surface/50 transition-colors"
                    >
                      <span className="font-mono text-xs text-text-primary truncate flex-1">
                        {attack.name}
                      </span>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <SeverityBadge severity={attack.severity} />
                        <button
                          onClick={() => onRunSingleAttack(attack.id)}
                          disabled={isRunning}
                          className={`px-2 py-1 text-xs border transition-colors ${
                            isRunning
                              ? 'border-border text-text-secondary cursor-not-allowed'
                              : 'border-border text-text-primary hover:border-red-primary hover:text-red-primary'
                          }`}
                        >
                          Run
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}

          {chainAttacks.length > 0 && (
            <div className="border border-border">
              <button
                onClick={() => toggleCategory('chain')}
                className="w-full px-3 py-2 flex items-center justify-between text-left hover:bg-surface/50 transition-colors"
              >
                <span className="text-sm text-text-primary">
                  Chain Attacks ({chainAttacks.length})
                </span>
                <span className="text-text-secondary text-xs">
                  {expandedCategories.has('chain') ? '[-]' : '[+]'}
                </span>
              </button>

              {expandedCategories.has('chain') && (
                <div className="border-t border-border">
                  {chainAttacks.map((attack) => (
                    <div
                      key={attack.id}
                      className="px-3 py-2 flex items-center justify-between gap-2 hover:bg-surface/50 transition-colors"
                    >
                      <span className="font-mono text-xs text-text-primary truncate flex-1">
                        {attack.name} ({attack.steps} steps)
                      </span>
                      <SeverityBadge severity={attack.severity} />
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="p-4 border-t border-border">
        <button
          onClick={onReset}
          disabled={isRunning}
          className={`text-xs transition-colors ${
            isRunning
              ? 'text-text-secondary/50 cursor-not-allowed'
              : 'text-text-secondary hover:text-text-primary'
          }`}
        >
          Reset Session
        </button>
      </div>
    </div>
  );
}
