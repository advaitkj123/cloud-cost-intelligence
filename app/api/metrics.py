from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.db.repositories.metric_repository import MetricRepository
from app.schemas.metrics import MetricCreate, MetricIngestResponse, MetricRead
from app.services.orchestrator import MetricOrchestrator

router = APIRouter()


@router.post("/metrics", response_model=MetricIngestResponse)
def ingest_metric(payload: MetricCreate, db: Session = Depends(get_db)) -> MetricIngestResponse:
    orchestrator = MetricOrchestrator(db)
    try:
        return orchestrator.ingest_metric(payload)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/metrics", response_model=list[MetricRead])
def list_metrics(
    resource_id: int | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[MetricRead]:
    repository = MetricRepository(db)
    return repository.list(limit=limit, resource_id=resource_id)
