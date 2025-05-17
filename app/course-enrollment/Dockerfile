FROM python:3.10-slim

# Install essential system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY app ./app

# Expose FastAPI port
EXPOSE 4002

# Run FastAPI app (note the module path is app.main:app)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4002"]
