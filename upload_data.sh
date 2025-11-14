#!/bin/bash
# Script to upload SQLite database to Fly.io volume

set -e

echo "=== Upload Database to Fly.io Volume ==="

# Check if database exists
if [ ! -f "data/orders.db" ]; then
    echo "Error: Database file not found at data/orders.db"
    echo "Please run the processing pipeline first to generate the database."
    exit 1
fi

# Get app name from fly.toml
APP_NAME=$(grep "^app = " fly.toml | cut -d "'" -f 2)

echo "App name: $APP_NAME"
echo "Database size: $(du -h data/orders.db | cut -f1)"
echo ""

# Check if volume exists
echo "Checking if volume exists..."
if ! fly volumes list | grep -q "tr_project_data"; then
    echo "Creating volume tr_project_data..."
    fly volumes create tr_project_data --size 1 --region dfw
else
    echo "Volume tr_project_data already exists"
fi

echo ""
echo "Uploading database to /data/orders.db..."

# Use fly ssh to upload the database
# First, we need to create an SFTP session or use fly proxy
fly ssh sftp shell <<EOF
put data/orders.db /data/orders.db
EOF

echo ""
echo "=== Upload Complete ==="
echo ""
echo "Verify the upload:"
echo "  fly ssh console"
echo "  ls -lh /data/orders.db"
