#!/bin/bash
# Start both Airflow webserver and scheduler in one container
# Used for cloud deployments that don't support multi-container docker-compose

set -e

echo "=========================================="
echo "Starting Airflow services..."
echo "=========================================="

# Wait for database to be ready (important for Railway)
echo "Waiting for database connection..."
until airflow db check; do
    echo "Database is unavailable - sleeping"
    sleep 2
done
echo "Database is ready!"

# Initialize database if needed (migrate will create tables if they don't exist)
echo "Initializing Airflow database..."
airflow db migrate

# Create admin user if it doesn't exist
echo "Creating admin user..."
airflow users create \
    --username airflow \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password airflow 2>/dev/null || echo "Admin user already exists"

# Start scheduler in background
echo "Starting Airflow scheduler in background..."
airflow scheduler &

# Wait a bit for scheduler to start
sleep 10

# Start webserver in foreground (this keeps container alive)
echo "Starting Airflow webserver..."
echo "=========================================="
echo "Airflow is ready!"
echo "Access the UI at the Railway URL"
echo "=========================================="
exec airflow webserver

