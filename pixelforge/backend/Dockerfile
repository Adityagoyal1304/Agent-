# PixelForge — Backend Dockerfile
# Based on Playwright's official Python image — Chromium dependencies are pre-installed
FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (already in base image but explicit is safer)
RUN playwright install chromium

# Copy backend source
COPY . .

# Expose FastAPI port
EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
