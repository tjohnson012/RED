"""
RED - Adversarial LLM Security Testing Platform
Main FastAPI application entry point.
"""

import os
from dotenv import load_dotenv

# Load env FIRST
load_dotenv()

# Initialize Datadog BEFORE other imports
from ddtrace import tracer, patch_all
from ddtrace.llmobs import LLMObs

# Patch all integrations
patch_all()

# Enable LLM Observability (agentless mode)
LLMObs.enable(
    ml_app=os.getenv("DD_LLMOBS_ML_APP", "red-security-testing"),
    api_key=os.getenv("DD_API_KEY"),
    site=os.getenv("DD_SITE", "us5.datadoghq.com"),
    agentless_enabled=True,
    integrations_enabled=True,
)

# NOW import FastAPI and app code
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    print("\n" + "=" * 60)
    print("RED - Adversarial LLM Security Testing Platform")
    print("=" * 60)
    print("Datadog LLM Observability enabled (agentless mode)")
    yield
    # Shutdown
    LLMObs.flush()
    print("\nRED shutdown complete")


app = FastAPI(
    title="RED - Adversarial LLM Security Testing",
    description="""
    RED finds what attackers will find first.

    A pure offensive security tool that systematically breaks LLM applications
    with jailbreaks, prompt injections, and data extraction attacks.

    ## Features
    - 50+ adversarial attack techniques
    - LLM-as-judge evaluation
    - Datadog LLM Observability integration
    - Automated incident creation
    - Attack graph visualization
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with project info."""
    return {
        "name": "RED",
        "tagline": "We break your AI before attackers do.",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=True
    )
