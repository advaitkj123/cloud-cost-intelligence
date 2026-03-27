from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnomalyRead(BaseModel):
    id: int
    resource_id: int
    timestamp: datetime
    anomaly_score: float
    reason: str

    model_config = ConfigDict(from_attributes=True)
