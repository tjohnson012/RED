# Deployment Guide

## Local Development

### Prerequisites

1. Python 3.9 or higher
2. Google Cloud CLI (`gcloud`) installed and authenticated
3. Datadog account with API and APP keys

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/red.git
cd red

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### Configure Environment Variables

Edit `.env` with your credentials:

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true

# Datadog
DD_API_KEY=your-datadog-api-key
DD_APP_KEY=your-datadog-app-key
DD_SITE=datadoghq.com
DD_SERVICE=red-llm-security
DD_ENV=production
DD_LLMOBS_ENABLED=1
DD_LLMOBS_ML_APP=red-security-testing
DD_LLMOBS_AGENTLESS_ENABLED=1
```

### Authenticate with Google Cloud

```bash
# Login to Google Cloud
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project your-project-id

# Enable Vertex AI
gcloud services enable aiplatform.googleapis.com
```

### Run the Application

```bash
# Start the server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Access the API docs
open http://localhost:8000/docs
```

## Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t red-llm-security .

# Run with environment variables
docker run -p 8000:8000 \
  -e GOOGLE_CLOUD_PROJECT=your-project \
  -e DD_API_KEY=your-key \
  -e DD_APP_KEY=your-app-key \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  red-llm-security
```

### Using Docker Compose

```bash
# Set environment variables
export GOOGLE_CLOUD_PROJECT=your-project
export DD_API_KEY=your-key
export DD_APP_KEY=your-app-key

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Cloud Deployment (Google Cloud Run)

### Build and Deploy

```bash
# Build image
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/red-llm-security

# Deploy to Cloud Run
gcloud run deploy red-llm-security \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/red-llm-security \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DD_API_KEY=$DD_API_KEY,DD_APP_KEY=$DD_APP_KEY,DD_SITE=datadoghq.com"
```

## Datadog Setup

### Create Monitors

Run the export script to generate sample configurations:

```bash
python scripts/export_datadog.py --sample --output datadog/
```

Then import them into Datadog using the API or UI.

### Create Dashboard

1. Go to Datadog Dashboards
2. Click "New Dashboard"
3. Import the JSON from `datadog/dashboard.json`

### Verify Integration

1. Run the traffic generator:
   ```bash
   python scripts/traffic_generator.py --rules
   ```

2. Check Datadog:
   - LLM Observability: https://app.datadoghq.com/llm
   - Metrics Explorer: Search for `red.security.*`
   - Monitors: Check for triggered alerts

## Troubleshooting

### Common Issues

**Vertex AI Authentication Error**
```
Error: Could not automatically determine credentials
```
Solution: Run `gcloud auth application-default login`

**Datadog Metrics Not Appearing**
- Verify DD_API_KEY is correct
- Check DD_SITE matches your region
- Wait 1-2 minutes for metrics to appear

**Rate Limiting from Gemini**
- Add delays between attacks in traffic generator
- Use `max_attacks` parameter to limit batch size
