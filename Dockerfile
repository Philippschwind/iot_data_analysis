
FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ /app/backend/

# Ensure Python logs are immediately visible
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
