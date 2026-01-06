# Image Python legere
FROM python:3.11-slim

WORKDIR /app

# Installer les dependances systeme necessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer
COPY requirements.txt .

# Installer pip packages avec cache
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Port
EXPOSE 8000

# Demarrer
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
