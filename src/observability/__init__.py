"""
Datadog observability module for RED.
"""

from .tracer import initialize_observability, shutdown_observability
from .metrics import MetricsReporter
from .incidents import IncidentManager

__all__ = [
    "initialize_observability",
    "shutdown_observability",
    "MetricsReporter",
    "IncidentManager"
]
