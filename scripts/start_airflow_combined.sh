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

echo "Patching airflow.cfg to force port 8080..."
sed -i "s/^web_server_port = .*/web_server_port = 8080/" /opt/airflow/airflow.cfg
sed -i "s/^web_server_host = .*/web_server_host = 0.0.0.0/" /opt/airflow/airflow.cfg

echo "Starting Airflow webserver on 0.0.0.0:8080"
AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8080 \
AIRFLOW__WEBSERVER__WEB_SERVER_HOST=0.0.0.0 \
exec airflow webserver
