#!/bin/bash
# Deployment script for Fly.io

set -e

echo "=== Legal Analysis System - Fly.io Deployment ==="

# Check if fly CLI is installed
if ! command -v fly &> /dev/null; then
    echo "Error: Fly CLI not found. Install from https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
fi

# Build and deploy
echo ""
echo "Step 1: Building application..."
fly deploy

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Next steps:"
echo "1. Create volume if not exists: fly volumes create tr_project_data --size 1 --region dfw"
echo "2. Set secrets: fly secrets set OPENAI_API_KEY=your_key_here"
echo "3. Upload database: ./upload_data.sh"
echo "4. View logs: fly logs"
echo "5. Open app: fly open"
echo ""
echo "Note: OPENAI_API_KEY is REQUIRED for semantic search (uses text-embedding-3-small API)"
