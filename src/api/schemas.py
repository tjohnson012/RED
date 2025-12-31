"""
Pydantic schemas for API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_count: int


class AttackRequest(BaseModel):
    attack_id: Optional[str] = None
    categories: Optional[List[str]] = None
    max_attacks: Optional[int] = Field(None, ge=1, le=100)
    include_chains: bool = True


class CustomAttackRequest(BaseModel):
    """Request schema for custom attack prompts."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="The attack prompt to send")
    name: str = Field(default="Custom Attack", max_length=100, description="Name for this attack")


class AttackResult(BaseModel):
    attack_id: str
    attack_name: str
    category: str
    success: bool
    confidence: float
    severity: str
    leak_types: List[str]
    timestamp: str


class AssessmentReport(BaseModel):
    session_id: str
    timestamp: str
    duration_seconds: float
    summary: dict
    by_category: dict
    by_severity: dict
    successful_attacks: List[dict]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
