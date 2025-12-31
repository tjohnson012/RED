"""
FastAPI routes for RED application.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime

from .schemas import (
    ChatRequest, ChatResponse,
    AttackRequest, AssessmentReport,
    HealthResponse, CustomAttackRequest
)
from ..target.chatbot import TargetChatbot
from ..attacker.agent import RedTeamAgent

router = APIRouter()

# Initialize components
target_chatbot = TargetChatbot()
red_agent = RedTeamAgent(target_chatbot)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="red-llm-security",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the target LLM application.
    This is the "victim" chatbot that RED attacks.
    """
    try:
        result = target_chatbot.chat(
            user_message=request.message,
            session_id=request.session_id or "default"
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/attack/single")
async def run_single_attack(attack_id: str):
    """Run a single specific attack."""
    result = red_agent.run_single_attack(attack_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/attack/assessment", response_model=AssessmentReport)
async def run_assessment(request: AttackRequest, background_tasks: BackgroundTasks):
    """
    Run a full RED team assessment.
    This executes multiple attacks and generates a comprehensive report.
    """
    try:
        report = red_agent.run_assessment(
            categories=request.categories,
            max_attacks=request.max_attacks,
            include_chains=request.include_chains
        )
        return AssessmentReport(**report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attacks")
async def list_attacks():
    """List all available attacks."""
    from ..attacker.attacks import ALL_ATTACKS, ALL_CHAIN_ATTACKS

    return {
        "single_attacks": [
            {
                "id": a["id"],
                "name": a["name"],
                "category": a["category"],
                "subcategory": a.get("subcategory", ""),
                "severity": a["severity"]
            }
            for a in ALL_ATTACKS
        ],
        "chain_attacks": [
            {
                "id": c["id"],
                "name": c["name"],
                "steps": len(c["steps"]),
                "severity": c["severity"]
            }
            for c in ALL_CHAIN_ATTACKS
        ],
        "total": len(ALL_ATTACKS) + len(ALL_CHAIN_ATTACKS)
    }


@router.post("/attack/custom")
async def run_custom_attack(request: CustomAttackRequest):
    """
    Run a custom attack prompt against the target.
    Allows users to test their own adversarial prompts.
    """
    import time
    from ..attacker.evaluator import AttackEvaluator
    from ..observability.metrics import metrics

    evaluator = AttackEvaluator()

    # Reset conversation for clean attack
    target_chatbot.reset_conversation()

    # Execute the attack
    start = time.time()
    result = target_chatbot.chat(request.prompt)
    latency = time.time() - start

    # Evaluate the response
    evaluation = evaluator.evaluate(
        prompt=request.prompt,
        response=result["response"],
        attack_name=request.name,
        category="custom",
        severity="medium"
    )

    # Report to Datadog
    metrics.report_attack(
        attack_id="custom",
        category="custom",
        success=evaluation["success"],
        severity=evaluation.get("severity", "medium"),
        confidence=evaluation.get("confidence", 0),
        latency=latency
    )

    # Report leaks if any
    if evaluation["success"] and evaluation.get("leak_types"):
        for leak_type in evaluation["leak_types"]:
            metrics.report_leak(leak_type, "custom")

    return {
        "attack_id": "custom",
        "attack_name": request.name,
        "category": "custom",
        "prompt": request.prompt,
        "response": result["response"],
        "success": evaluation["success"],
        "confidence": evaluation.get("confidence", 0),
        "severity": evaluation.get("severity", "medium"),
        "leak_types": evaluation.get("leak_types", []),
        "evidence": evaluation.get("evidence", []),
        "latency": round(latency, 2)
    }


@router.post("/reset")
async def reset_session():
    """Reset the chatbot conversation."""
    target_chatbot.reset_conversation()
    return {"status": "reset", "message": "Conversation history cleared"}
