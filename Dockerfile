# Image Python legere
FROM python:3.11-slim

WORKDIR /app

# Installer les dependances systeme
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le backend
COPY backend/ ./backend/

# Copier les donnees
COPY data/ ./data/

# Workdir dans backend
WORKDIR /app/backend

# Port
EXPOSE 8000

# Demarrer
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
