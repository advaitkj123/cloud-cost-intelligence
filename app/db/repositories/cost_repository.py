from datetime import datetime, timedelta

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.cost import CostRecord
from app.models.resource import Resource


class CostRecordRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, record: CostRecord) -> CostRecord:
        self.db.add(record)
        self.db.flush()
        self.db.refresh(record)
        return record

    def latest_for_resource(self, resource_id: int) -> CostRecord | None:
        stmt = (
            select(CostRecord)
            .where(CostRecord.resource_id == resource_id)
            .order_by(desc(CostRecord.timestamp))
            .limit(1)
        )
        return self.db.scalar(stmt)

    def recent_for_resource(self, resource_id: int, limit: int = 200) -> list[CostRecord]:
        stmt = (
            select(CostRecord)
            .where(CostRecord.resource_id == resource_id)
            .order_by(desc(CostRecord.timestamp))
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def total_cost(self) -> float:
        return float(self.db.scalar(select(func.coalesce(func.sum(CostRecord.estimated_cost), 0.0))) or 0.0)

    def per_resource_totals(self) -> list[tuple[int, str, str, float]]:
        stmt = (
            select(
                Resource.id,
                Resource.name,
                Resource.type,
                func.coalesce(func.sum(CostRecord.estimated_cost), 0.0),
            )
            .join(CostRecord, CostRecord.resource_id == Resource.id)
            .group_by(Resource.id, Resource.name, Resource.type)
            .order_by(func.sum(CostRecord.estimated_cost).desc())
        )
        return [(row[0], row[1], str(row[2].value), float(row[3])) for row in self.db.execute(stmt).all()]

    def trend(self, hours: int = 24) -> list[tuple[datetime, float]]:
        since = datetime.utcnow() - timedelta(hours=hours)
        stmt = (
            select(CostRecord.timestamp, func.sum(CostRecord.estimated_cost))
            .where(CostRecord.timestamp >= since)
            .group_by(CostRecord.timestamp)
            .order_by(CostRecord.timestamp.asc())
        )
        return [(row[0], float(row[1])) for row in self.db.execute(stmt).all()]
