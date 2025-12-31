# RED - Adversarial LLM Security Testing Platform

**RED finds what attackers will find first.**

A comprehensive adversarial security testing platform for LLM applications. RED systematically probes target systems with 38+ attack techniques, evaluates success using LLM-as-a-judge methodology, and integrates with Datadog for full observability.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![React](https://img.shields.io/badge/React-18-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- **38+ Adversarial Attacks** - Jailbreaks, prompt injections, data extraction, encoding bypasses, social engineering, and chain attacks
- **Intelligent Evaluation** - Three-stage detection: pattern matching, LLM-as-judge, and behavioral jailbreak detection
- **Custom Attack Input** - Test your own adversarial prompts with full evaluation
- **Datadog Integration** - Custom metrics, LLM Observability, automatic incident creation
- **Real-Time Dashboard** - Watch attacks execute with live results and statistics

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                    React + TypeScript                        │
│         ┌──────────┬──────────────┬─────────────┐           │
│         │  Attack  │  Live Feed   │  Results    │           │
│         │  Panel   │              │  Summary    │           │
│         └──────────┴──────────────┴─────────────┘           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Attack    │  │   Target    │  │     Evaluator       │  │
│  │   Agent     │──│   Chatbot   │──│  (Pattern + LLM +   │  │
│  │             │  │  (Gemini)   │  │   Jailbreak Check)  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Datadog                                 │
│     Metrics │ LLM Observability │ Incidents │ Dashboards    │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Google Cloud Project with Vertex AI enabled
- Datadog account

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run backend
uvicorn src.main:app --host 0.0.0.0 --port 8080
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Environment Variables

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true

# Datadog
DD_API_KEY=your-api-key
DD_APP_KEY=your-app-key
DD_SITE=us5.datadoghq.com
DD_SERVICE=red-llm-security
DD_ENV=production
DD_LLMOBS_ENABLED=1
DD_LLMOBS_ML_APP=red-security-testing
DD_LLMOBS_AGENTLESS_ENABLED=1
```

## Attack Categories

| Category | Count | Description |
|----------|-------|-------------|
| Jailbreaks | 8 | Bypass safety guidelines (DAN, Developer Mode, etc.) |
| Injections | 6 | Hijack instruction flow |
| Extractions | 5 | Leak sensitive data |
| Encoding | 6 | Obfuscation to evade filters |
| Social Engineering | 7 | Manipulation through roleplay |
| Chain Attacks | 6 | Multi-step exploitation sequences |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/attacks` | List all attacks |
| POST | `/api/v1/attack/single` | Run single attack |
| POST | `/api/v1/attack/custom` | Run custom prompt |
| POST | `/api/v1/attack/assessment` | Run full assessment |
| POST | `/api/v1/reset` | Reset session |

## Evaluation Pipeline

```
Response
   │
   ▼
┌──────────────────┐
│ Pattern Matching │ → Exact secret detection (credentials, PII, URLs)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  LLM-as-Judge    │ → Semantic analysis (refusal vs. actual leak)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Jailbreak Check  │ → Behavioral detection (character breaking)
└────────┬─────────┘
         │
         ▼
    Final Result
```

## Datadog Metrics

- `red.security.attack.count` - Total attacks executed
- `red.security.attack.success` - Successful attacks
- `red.security.attack.confidence` - Confidence scores
- `red.security.attack.latency` - Response times
- `red.security.leak.detected` - Leak events by type
- `red.security.assessment.vulnerability_score` - Overall score

## Tech Stack

**Backend**
- Python 3.12
- FastAPI
- Vertex AI / Gemini 2.0 Flash
- Datadog (ddtrace, datadog-api-client)

**Frontend**
- React 18
- TypeScript
- Vite
- Tailwind CSS

## License

MIT License

---

*Built for the Google Cloud + Datadog Hackathon 2025*
