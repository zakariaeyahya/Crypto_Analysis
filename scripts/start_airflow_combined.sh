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

echo "Patching airflow.cfg to force port 8080..."
sed -i "s/^web_server_port = .*/web_server_port = 8080/" /opt/airflow/airflow.cfg
sed -i "s/^web_server_host = .*/web_server_host = 0.0.0.0/" /opt/airflow/airflow.cfg

# RAILWAY: Scheduler disabled to save resources - webserver only
# For automated DAG execution, deploy a separate scheduler service
echo "NOTE: Scheduler is disabled for Railway deployment (low memory)"

# Configure Gunicorn for Railway - minimal resources
export GUNICORN_CMD_ARGS="--workers=1 --worker-class=sync --timeout=120 --bind=0.0.0.0:8080 --access-logfile=- --error-logfile=- --log-level=info"

# Increase Airflow webserver startup timeout
export AIRFLOW__WEBSERVER__WEB_SERVER_MASTER_TIMEOUT=300

# Reduce memory footprint
export AIRFLOW__CORE__PARALLELISM=4
export AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG=2
export AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG=1
export AIRFLOW__WEBSERVER__WORKERS=1
export AIRFLOW__WEBSERVER__WORKER_REFRESH_INTERVAL=0

echo "============================================"
echo "Starting Airflow webserver on 0.0.0.0:8080"
echo "Memory-optimized for Railway deployment"
echo "Scheduler: DISABLED (webserver only)"
echo "============================================"

AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8080 \
AIRFLOW__WEBSERVER__WEB_SERVER_HOST=0.0.0.0 \
exec airflow webserver
