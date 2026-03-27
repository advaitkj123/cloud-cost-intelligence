from datetime import datetime
import random

from app.cloud.aws.cloudwatch_service import CloudWatchMetricPoint, AWSCloudWatchService
from app.cloud.aws.ec2_service import AWSEC2Service, EC2InstanceDescription
from app.cloud.aws.pricing_service import AWSPricingService
from app.core.config import get_settings
from app.models.resource import Resource, ResourceType
from app.schemas.metrics import MetricCreate

settings = get_settings()


class CloudMetricCollector:
    def __init__(self) -> None:
        self.aws_ec2_service = AWSEC2Service()
        self.aws_cloudwatch_service = AWSCloudWatchService()
        self.aws_pricing_service = AWSPricingService()

    def generate_metric(self, resource: Resource) -> MetricCreate:
        if resource.type == ResourceType.ec2:
            cpu = random.uniform(1, 95)
            memory = random.uniform(20, 90)
            requests = random.randint(100, 5000)
            storage = random.uniform(5, 50)
        elif resource.type == ResourceType.lambda_fn:
            cpu = random.uniform(5, 70)
            memory = random.uniform(20, 85)
            requests = random.randint(1000, 15000)
            storage = random.uniform(0.1, 5)
        else:
            cpu = random.uniform(0, 10)
            memory = random.uniform(10, 40)
            requests = random.randint(0, 300)
            storage = random.uniform(100, 1500)

        return MetricCreate(
            resource_id=resource.id,
            timestamp=datetime.utcnow(),
            cpu_usage=round(cpu, 2),
            memory_usage=round(memory, 2),
            requests=requests,
            storage_used=round(storage, 2),
            network_in=0.0,
            network_out=0.0,
        )

    def fetch_aws_resources(self) -> list[EC2InstanceDescription]:
        return self.aws_ec2_service.list_instances(region_name=settings.aws_region)

    def fetch_aws_metrics(self, instance_id: str, region_name: str) -> list[CloudWatchMetricPoint]:
        return self.aws_cloudwatch_service.get_instance_metrics(
            instance_id=instance_id,
            region_name=region_name,
            lookback_minutes=settings.aws_metric_lookback_minutes,
            period_seconds=settings.aws_metric_period_seconds,
        )

    def get_aws_hourly_cost(self, instance_type: str, region_name: str) -> float:
        return self.aws_pricing_service.get_ec2_hourly_price(instance_type, region_name)
