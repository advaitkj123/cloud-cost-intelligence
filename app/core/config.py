from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "Cloud Cost Intelligence Platform"
    environment: str = "development"
    api_prefix: str = ""
    debug: bool = True

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/cost_intelligence"

    cors_origins: List[AnyHttpUrl | str] = Field(default_factory=lambda: ["http://localhost:5173"])

    cloud_collector_mode: str = "simulated"
    aws_access_key: str = ""
    aws_secret_key: str = ""
    aws_session_token: str = ""
    aws_region: str = "us-east-1"
    aws_pricing_region: str = "us-east-1"
    aws_use_pricing_api: bool = True
    aws_metric_period_seconds: int = 300
    aws_metric_lookback_minutes: int = 60

    ec2_hourly_rate: float = 0.096
    lambda_request_cost_per_million: float = 0.20
    lambda_duration_cost_per_gb_second: float = 0.0000166667
    s3_storage_cost_per_gb_month: float = 0.023

    low_cpu_threshold: float = 5.0
    high_request_spike_multiplier: float = 3.0
    cost_threshold_for_stop: float = 1.0

    auto_apply_optimizations: bool = True
    dry_run_optimizations: bool = True

    scheduler_enabled: bool = True
    scheduler_interval_seconds: int = 20
    default_metric_window: int = 200
    anomaly_min_training_points: int = 12
    isolation_forest_contamination: float = 0.08


@lru_cache
def get_settings() -> Settings:
    return Settings()
