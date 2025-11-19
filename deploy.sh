#!/bin/bash
#
# DV Aviation Chat Agent - L7 Deployment Script
# Deploy minimal chat agent to Google Cloud Run
#
# Usage: ./deploy.sh
#

set -e  # Exit on error

echo "=========================================="
echo "DV Aviation Chat Agent - L7 Deployment"
echo "=========================================="
echo ""

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-n8n-agent-451019}"
SERVICE_NAME="dv-aviation-chat"
REGION="us-east4"
MEMORY="512Mi"
CPU="1"
TIMEOUT="60"  # Start with 60s, increase if needed
MIN_INSTANCES="0"
MAX_INSTANCES="5"

echo "Configuration:"
echo "  Project: $PROJECT_ID"
echo "  Service: $SERVICE_NAME"
echo "  Region: $REGION"
echo "  Memory: $MEMORY"
echo "  Timeout: ${TIMEOUT}s"
echo ""

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ERROR: ANTHROPIC_API_KEY environment variable not set"
    echo ""
    echo "Set it with:"
    echo "  export ANTHROPIC_API_KEY='your-key-here'"
    echo ""
    exit 1
fi

# Confirm deployment
echo "Ready to deploy to Cloud Run?"
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

# Create secret for API key (if doesn't exist)
echo "📦 Ensuring API key secret exists..."
if ! gcloud secrets describe anthropic-api-key --project=$PROJECT_ID &>/dev/null; then
    echo "Creating secret..."
    echo -n "$ANTHROPIC_API_KEY" | gcloud secrets create anthropic-api-key \
        --data-file=- \
        --project=$PROJECT_ID
else
    echo "Secret already exists, updating..."
    echo -n "$ANTHROPIC_API_KEY" | gcloud secrets versions add anthropic-api-key \
        --data-file=- \
        --project=$PROJECT_ID
fi

# Deploy to Cloud Run
echo ""
echo "🚀 Deploying to Cloud Run..."
echo ""

gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --timeout $TIMEOUT \
    --memory $MEMORY \
    --cpu $CPU \
    --min-instances $MIN_INSTANCES \
    --max-instances $MAX_INSTANCES \
    --set-env-vars ENVIRONMENT=production \
    --set-secrets ANTHROPIC_API_KEY=anthropic-api-key:latest \
    --project $PROJECT_ID

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --project $PROJECT_ID \
    --format='value(status.url)')

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Service URL: $SERVICE_URL"
echo ""
echo "Test it:"
echo "  Health: curl $SERVICE_URL/health"
echo "  Chat: curl -X POST $SERVICE_URL/api/chat/message \\"
echo "         -H 'Content-Type: application/json' \\"
echo "         -d '{\"message\": \"What charter services do you offer?\"}'"
echo ""
echo "Embed on dvaviation.com:"
echo "  <script src=\"$SERVICE_URL/shared/universal-chat-widget.js\"></script>"
echo "  <script>"
echo "    new UniversalChatWidget({"
echo "      apiUrl: '$SERVICE_URL',"
echo "      primaryColor: '#1E3A8A',"
echo "      companyName: 'DV Aviation'"
echo "    });"
echo "  </script>"
echo ""
echo "=========================================="
