"""
API module for RED.
"""

from .routes import router
from .schemas import (
    ChatRequest,
    ChatResponse,
    AttackRequest,
    AssessmentReport,
    HealthResponse
)

__all__ = [
    "router",
    "ChatRequest",
    "ChatResponse",
    "AttackRequest",
    "AssessmentReport",
    "HealthResponse"
]
