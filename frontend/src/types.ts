export interface Attack {
  id: string;
  name: string;
  category: string;
  subcategory: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
}

export interface ChainAttack {
  id: string;
  name: string;
  steps: number;
  severity: 'critical' | 'high' | 'medium' | 'low';
}

export interface AttackListResponse {
  single_attacks: Attack[];
  chain_attacks: ChainAttack[];
  total: number;
}

export interface AttackResult {
  attack_id: string;
  attack_name: string;
  category: string;
  subcategory?: string;
  success: boolean;
  confidence: number;
  severity: string;
  leak_types: string[];
  evidence: string[];
  prompt?: string;
  response: string;
  latency: number;
  timestamp?: string;
}

export interface AssessmentSummary {
  total_attacks: number;
  successful_attacks: number;
  success_rate: number;
  vulnerability_score: number;
  risk_level: string;
}

export interface AssessmentReport {
  session_id: string;
  timestamp: string;
  duration_seconds: number;
  summary: AssessmentSummary;
  by_category: Record<string, { total: number; successful: number }>;
  by_severity: Record<string, number>;
  successful_attacks: AttackResult[];
  all_results: AttackResult[];
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
}

export interface AppState {
  backendConnected: boolean;
  attacks: Attack[];
  chainAttacks: ChainAttack[];
  results: AttackResult[];
  isRunning: boolean;
  currentAttackId: string | null;
  error: string | null;
}
