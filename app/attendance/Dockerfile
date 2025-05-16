FROM python:3.10-slim

# Install minimal dependencies for dlib and face_recognition
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libboost-python-dev \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency list and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt && \
    pip install opencv-python-headless

# Copy the application code
COPY . .

# Expose FastAPI port
EXPOSE 4000

# Run FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4000"]
