#!/bin/bash
set -e

echo "=== Starting Airflow (Railway optimized) ==="

echo "Waiting for database connection..."
until airflow db check; do
    echo "DB unavailable - sleeping"
    sleep 2
done

echo "DB ready!"

echo "Running migrations..."
airflow db migrate

echo "Creating admin user..."
airflow users create \
    --username airflow \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password airflow 2>/dev/null || echo "Admin user exists"

echo "Starting scheduler in background..."
airflow scheduler &

sleep 5

echo "Starting Airflow webserver on Railway port: $PORT"

export AIRFLOW__WEBSERVER__WEB_SERVER_MASTER_TIMEOUT=300
export GUNICORN_CMD_ARGS="--workers=1 --timeout=300 --bind=0.0.0.0:$PORT"

exec airflow webserver
