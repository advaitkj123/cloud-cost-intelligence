from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.db.repositories.anomaly_repository import AnomalyRepository
from app.schemas.anomalies import AnomalyRead

router = APIRouter()


@router.get("/anomalies", response_model=list[AnomalyRead])
def list_anomalies(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[AnomalyRead]:
    repository = AnomalyRepository(db)
    return repository.list(limit=limit)
