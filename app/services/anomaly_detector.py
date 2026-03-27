from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import IsolationForest

from app.core.config import get_settings
from app.db.repositories.cost_repository import CostRecordRepository
from app.db.repositories.metric_repository import MetricRepository
from app.models.resource import Resource
from app.schemas.metrics import MetricCreate

settings = get_settings()


@dataclass
class AnomalyResult:
    is_anomaly: bool
    score: float
    reason: str


class AnomalyDetector:
    def __init__(self, metric_repository: MetricRepository, cost_repository: CostRecordRepository):
        self.metric_repository = metric_repository
        self.cost_repository = cost_repository

    def _build_features(self, cpu: float, memory: float, requests: int, storage: float, cost: float) -> list[float]:
        return [cpu, memory, float(requests), storage, cost]

    def detect(self, resource: Resource, metric: MetricCreate, estimated_cost: float) -> AnomalyResult:
        historical = self.metric_repository.recent_for_resource(
            resource.id, limit=settings.default_metric_window
        )
        historical_costs = list(reversed(self.cost_repository.recent_for_resource(resource.id, limit=len(historical) or 1)))
        features = []
        for index, metric_item in enumerate(reversed(historical)):
            historical_cost = historical_costs[index].estimated_cost if index < len(historical_costs) else 0.0
            features.append(
                self._build_features(
                    metric_item.cpu_usage,
                    metric_item.memory_usage,
                    metric_item.requests,
                    metric_item.storage_used,
                    historical_cost,
                )
            )
        current = self._build_features(
            metric.cpu_usage, metric.memory_usage, metric.requests, metric.storage_used, estimated_cost
        )
        reasons: list[str] = []

        if len(features) >= settings.anomaly_min_training_points:
            x_train = np.array(features, dtype=float)
            x_current = np.array([current], dtype=float)
            model = IsolationForest(
                contamination=settings.isolation_forest_contamination,
                random_state=42,
                n_estimators=200,
            )
            model.fit(x_train)
            prediction = model.predict(x_current)[0]
            raw_score = float(-model.decision_function(x_current)[0])
            is_anomaly = prediction == -1
        else:
            raw_score = 0.0
            is_anomaly = False

        if historical:
            avg_requests = sum(m.requests for m in historical) / len(historical)
            avg_cpu = sum(m.cpu_usage for m in historical) / len(historical)
            if avg_requests > 0 and metric.requests > avg_requests * settings.high_request_spike_multiplier:
                is_anomaly = True
                raw_score += 0.6
                reasons.append("Request rate spiked sharply above historical baseline")
            if metric.cpu_usage > max(avg_cpu * 2.5, 90):
                is_anomaly = True
                raw_score += 0.4
                reasons.append("CPU usage deviated materially from historical behavior")

        if estimated_cost > settings.cost_threshold_for_stop * 2:
            reasons.append("Estimated cost is significantly above optimization threshold")

        if not reasons:
            reasons.append("Isolation Forest score within normal range" if not is_anomaly else "Isolation Forest detected unusual behavior")

        return AnomalyResult(
            is_anomaly=is_anomaly,
            score=round(raw_score, 4),
            reason="; ".join(reasons),
        )
