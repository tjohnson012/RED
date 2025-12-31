import type { AttackListResponse, AttackResult, AssessmentReport, HealthResponse } from './types';

const API_BASE = '/api/v1';

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error('Backend not available');
  }
  return response.json();
}

export async function getAttacks(): Promise<AttackListResponse> {
  const response = await fetch(`${API_BASE}/attacks`);
  if (!response.ok) {
    throw new Error('Failed to fetch attacks');
  }
  return response.json();
}

export async function runSingleAttack(attackId: string): Promise<AttackResult> {
  const response = await fetch(`${API_BASE}/attack/single?attack_id=${attackId}`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to run attack: ${attackId}`);
  }
  return response.json();
}

export async function runAssessment(
  maxAttacks: number = 38,
  includeChains: boolean = true
): Promise<AssessmentReport> {
  const response = await fetch(`${API_BASE}/attack/assessment`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      max_attacks: maxAttacks,
      include_chains: includeChains,
    }),
  });
  if (!response.ok) {
    throw new Error('Failed to run assessment');
  }
  return response.json();
}

export async function resetSession(): Promise<void> {
  const response = await fetch(`${API_BASE}/reset`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to reset session');
  }
}

export async function runCustomAttack(prompt: string, name: string = 'Custom Attack'): Promise<AttackResult> {
  const response = await fetch(`${API_BASE}/attack/custom`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt, name }),
  });
  if (!response.ok) {
    throw new Error('Failed to run custom attack');
  }
  return response.json();
}
