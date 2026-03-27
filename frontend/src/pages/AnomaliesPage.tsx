import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import type { Anomaly } from '../types';
import { ErrorState } from '../components/ErrorState';
import { LoadingState } from '../components/LoadingState';
import { Panel } from '../components/Panel';

function severity(score: number) {
  if (score >= 0.7) return 'High';
  if (score >= 0.3) return 'Medium';
  return 'Low';
}

export function AnomaliesPage() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const response = await api.getAnomalies();
        if (active) {
          setAnomalies(response);
          setError(null);
        }
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : 'Failed to load anomalies');
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    load();
    const interval = window.setInterval(load, 10000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <Panel title="Anomaly feed" subtitle="Isolation Forest and rule engine outputs for cloud cost and utilization deviations">
      <div className="space-y-4">
        {anomalies.length === 0 ? (
          <p className="text-sm text-slate-400">No anomalies detected yet. Keep the simulator running to build history.</p>
        ) : (
          anomalies.map((anomaly) => (
            <div key={anomaly.id} className="rounded-2xl border border-slate-800 bg-slate-950/50 p-5">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <div className="text-sm text-slate-400">Resource #{anomaly.resource_id}</div>
                  <div className="mt-1 font-medium text-white">{anomaly.reason}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-slate-400">Severity</div>
                  <div className="font-semibold text-amber-300">{severity(anomaly.anomaly_score)}</div>
                </div>
              </div>
              <div className="mt-4 flex items-center justify-between text-sm text-slate-400">
                <span>Score: {anomaly.anomaly_score.toFixed(4)}</span>
                <span>{new Date(anomaly.timestamp).toLocaleString()}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </Panel>
  );
}
