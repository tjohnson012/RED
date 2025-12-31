"""
Custom metrics for RED security testing.
Uses Datadog API directly for agentless mode.
"""

import os
import time
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_series import MetricSeries


class MetricsReporter:
    """Reports custom metrics to Datadog via API (agentless)."""

    def __init__(self):
        self.config = Configuration()
        self.config.api_key["apiKeyAuth"] = os.getenv("DD_API_KEY")
        self.config.api_key["appKeyAuth"] = os.getenv("DD_APP_KEY")
        self.config.server_variables["site"] = os.getenv("DD_SITE", "us5.datadoghq.com")

    def _submit_metric(self, metric_name: str, value: float, tags: list = None):
        """Submit a metric to Datadog."""
        with ApiClient(self.config) as api_client:
            api = MetricsApi(api_client)

            timestamp = int(time.time())

            payload = MetricPayload(
                series=[
                    MetricSeries(
                        metric=metric_name,
                        type=MetricIntakeType.GAUGE,
                        points=[
                            MetricPoint(
                                timestamp=timestamp,
                                value=value,
                            )
                        ],
                        tags=tags or ["env:production", "service:red-llm-security"],
                    )
                ]
            )

            try:
                api.submit_metrics(body=payload)
                print(f"[DD] Metric sent: {metric_name}={value}")
            except Exception as e:
                print(f"[DD] Failed to send metric {metric_name}: {e}")

    def report_attack(self, attack_id: str, category: str, success: bool,
                      severity: str, confidence: float, latency: float):
        """Report attack metrics to Datadog."""
        tags = [
            f"attack_id:{attack_id}",
            f"category:{category}",
            f"severity:{severity}",
            f"success:{str(success).lower()}",
            "env:production",
            "service:red-llm-security"
        ]

        # Attack count
        self._submit_metric("red.security.attack.count", 1, tags)

        # Success/failure
        if success:
            self._submit_metric("red.security.attack.success", 1, tags)
        else:
            self._submit_metric("red.security.attack.failed", 1, tags)

        # Confidence score
        self._submit_metric("red.security.attack.confidence", confidence, tags)

        # Latency
        self._submit_metric("red.security.attack.latency", latency, tags)

    def report_leak(self, leak_type: str, attack_id: str):
        """Report detected leak to Datadog."""
        tags = [
            f"leak_type:{leak_type}",
            f"attack_id:{attack_id}",
            "env:production",
            "service:red-llm-security"
        ]
        self._submit_metric("red.security.leak.detected", 1, tags)

    def report_assessment_complete(self, total: int, successful: int, vulnerability_score: float):
        """Report assessment completion metrics."""
        tags = ["env:production", "service:red-llm-security"]

        self._submit_metric("red.security.assessment.total", total, tags)
        self._submit_metric("red.security.assessment.successful", successful, tags)
        self._submit_metric("red.security.assessment.vulnerability_score", vulnerability_score, tags)


# Global instance
metrics = MetricsReporter()
