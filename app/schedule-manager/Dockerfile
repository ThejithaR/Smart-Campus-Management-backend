# Use a Python slim image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install any necessary system dependencies (if required by your Python packages)
# Add any specific libs needed by packages in requirements.txt here
# RUN apt-get update && apt-get install -y \
#     some-dependency \
#     another-dependency \
#     && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the working directory
COPY requirements.txt .

# Install the Python dependencies
# Use --no-cache-dir to save space
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code from your local directory to the container's working directory
COPY . .

# Expose the port the FastAPI application will run on
# Assuming this service also runs on port 8000 internally, like most others
EXPOSE 8000

# Command to run the application using uvicorn
# Assumes your main FastAPI application instance is in main.py and is named 'app'
# Since main.py is directly under ./app/schedule-manager, it's /app/main.py in the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]