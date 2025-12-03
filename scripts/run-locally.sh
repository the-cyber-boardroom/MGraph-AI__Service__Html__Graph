#!/bin/bash
PORT=10020

# Load environment variables from .env file if it exists
if [ -f .local-server.env ]; then
    echo "Loading environment variables from .local-server.env file..."
    export $(cat .local-server.env | grep -v '^#' | grep -v '^[[:space:]]*$' | xargs)
    echo "✓ Environment variables loaded"
else
    echo "⚠️  Warning: .env file not found"
    echo "   Create a .env file with your configuration"
fi

poetry run uvicorn mgraph_ai_service_html_graph.fast_api.lambda_handler:app --reload --host 0.0.0.0 --port $PORT \
    --log-level info \
    --no-access-log