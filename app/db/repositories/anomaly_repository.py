from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.anomalies import Anomaly


class AnomalyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, anomaly: Anomaly) -> Anomaly:
        self.db.add(anomaly)
        self.db.flush()
        self.db.refresh(anomaly)
        return anomaly

    def list(self, limit: int = 100) -> list[Anomaly]:
        stmt = select(Anomaly).order_by(desc(Anomaly.timestamp)).limit(limit)
        return list(self.db.scalars(stmt))
