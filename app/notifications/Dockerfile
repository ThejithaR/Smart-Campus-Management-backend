# Use a Python slim image as the base
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install any necessary system dependencies (if required by your Python packages)
# For a basic FastAPI app, often none are needed beyond the base image
# RUN apt-get update && apt-get install -y ... && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code from your local directory to the container's working directory
COPY . .

# Expose the port the FastAPI application will run on
EXPOSE 8000

# Command to run the application using uvicorn
# Assumes your main FastAPI application instance is in app/main.py and is named 'app'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]