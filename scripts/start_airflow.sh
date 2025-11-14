#!/bin/bash
# Script to start Airflow services automatically
# Usage: Add to crontab with @reboot or systemd service

cd "$(dirname "$0")/.." || exit 1

# Start Docker Compose services
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for Airflow services to start..."
sleep 30

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✓ Airflow services started successfully"
    echo "Access Airflow UI at: http://localhost:8080"
else
    echo "❌ Error: Some services failed to start"
    docker-compose ps
    exit 1
fi

