import type {
  Action,
  Anomaly,
  AwsMetric,
  AwsSyncResponse,
  CostSummary,
  Metric,
  ResourceSummary,
} from '../types';

const API_BASE = '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...init,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed for ${path}`);
  }

  return response.json() as Promise<T>;
}

export const api = {
  getHealth: () => request<{ status: string; service: string }>('/'),
  getCost: () => request<CostSummary>('/cost'),
  getResources: () => request<ResourceSummary[]>('/resources'),
  getAwsResources: () => request<ResourceSummary[]>('/aws/resources'),
  getMetrics: () => request<Metric[]>('/metrics?limit=100'),
  getAwsMetrics: () => request<AwsMetric[]>('/aws/metrics?limit=100'),
  syncAws: () => request<AwsSyncResponse>('/aws/sync', { method: 'POST' }),
  getAnomalies: () => request<Anomaly[]>('/anomalies?limit=100'),
  getActions: () => request<Action[]>('/actions?limit=100'),
  triggerAction: (resourceId: number, actionType: string, dryRun = true) =>
    request<{ action_id: number; status: string; estimated_savings: number }>('/actions', {
      method: 'POST',
      body: JSON.stringify({ resource_id: resourceId, action_type: actionType, dry_run: dryRun }),
    }),
};
