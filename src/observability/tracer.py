"""
Datadog LLM Observability configuration.
"""

import os
from ddtrace import tracer, patch_all
from ddtrace.llmobs import LLMObs


def initialize_observability():
    """Initialize Datadog tracing and LLM Observability."""

    # Patch all supported libraries
    patch_all()

    # Enable LLM Observability
    LLMObs.enable(
        ml_app=os.getenv("DD_LLMOBS_ML_APP", "red-security-testing"),
        api_key=os.getenv("DD_API_KEY"),
        site=os.getenv("DD_SITE", "datadoghq.com"),
        agentless_enabled=os.getenv("DD_LLMOBS_AGENTLESS_ENABLED", "true").lower() == "true",
        env=os.getenv("DD_ENV", "production"),
        service=os.getenv("DD_SERVICE", "red-llm-security"),
    )

    print("✅ Datadog LLM Observability initialized")
    print(f"   ML App: {os.getenv('DD_LLMOBS_ML_APP', 'red-security-testing')}")
    print(f"   Service: {os.getenv('DD_SERVICE', 'red-llm-security')}")


def shutdown_observability():
    """Gracefully shutdown observability."""
    LLMObs.flush()
    print("✅ Datadog LLM Observability flushed and shutdown")
