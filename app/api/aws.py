from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.resources import build_resource_response
from app.core.dependencies import get_db
from app.db.repositories.cost_repository import CostRecordRepository
from app.db.repositories.metric_repository import MetricRepository
from app.db.repositories.resource_repository import ResourceRepository
from app.schemas.aws import AWSMetricRead, AWSSyncResponse
from app.schemas.resource import ResourceWithLatest
from app.services.collector import CloudMetricCollector
from app.services.orchestrator import MetricOrchestrator

router = APIRouter()


@router.get("/aws/resources", response_model=list[ResourceWithLatest])
def list_aws_resources(db: Session = Depends(get_db)) -> list[ResourceWithLatest]:
    resource_repo = ResourceRepository(db)
    metric_repo = MetricRepository(db)
    cost_repo = CostRecordRepository(db)

    response: list[ResourceWithLatest] = []
    for resource in resource_repo.list_by_provider("aws"):
        latest_metric = metric_repo.latest_for_resource(resource.id)
        latest_cost = cost_repo.latest_for_resource(resource.id)
        response.append(build_resource_response(resource, latest_metric, latest_cost))
    return response


@router.get("/aws/metrics", response_model=list[AWSMetricRead])
def list_aws_metrics(
    resource_id: int | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[AWSMetricRead]:
    metric_repo = MetricRepository(db)
    resource_repo = ResourceRepository(db)
    resources = {resource.id: resource for resource in resource_repo.list_by_provider("aws")}

    metrics = metric_repo.list_for_provider("aws", limit=limit, resource_id=resource_id)
    return [
        AWSMetricRead(
            resource_id=metric.resource_id,
            instance_id=resources.get(metric.resource_id).external_id if resources.get(metric.resource_id) else None,
            instance_type=resources.get(metric.resource_id).instance_type if resources.get(metric.resource_id) else None,
            timestamp=metric.timestamp,
            cpu_usage=metric.cpu_usage,
            network_in=metric.network_in,
            network_out=metric.network_out,
        )
        for metric in metrics
    ]


@router.post("/aws/sync", response_model=AWSSyncResponse)
def sync_aws(db: Session = Depends(get_db)) -> AWSSyncResponse:
    orchestrator = MetricOrchestrator(db, collector=CloudMetricCollector())
    try:
        return orchestrator.sync_aws()
    except (NoCredentialsError, ClientError, BotoCoreError) as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"AWS sync failed: {exc}") from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected AWS sync failure: {exc}") from exc
