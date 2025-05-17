import aio_pika
import os
import asyncio

# Define the RabbitMQ host using an environment variable, defaulting to 'rabbitmq'
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
# Construct the AMQP URL
RABBITMQ_URL = f"amqp://guest:guest@{RABBITMQ_HOST}:5672/"

async def get_connection():
    """Helper function to establish RabbitMQ connection with basic error handling."""
    connection = None
    # Implement a basic retry mechanism in case RabbitMQ isn't immediately available
    retries = 10  # Increased retries
    delay = 5  # seconds
    
    for i in range(retries):
        try:
            print(f"Attempt {i+1}/{retries}: Attempting to connect to RabbitMQ at {RABBITMQ_HOST}")
            # Use robust connection for automatic reconnection
            connection = await aio_pika.connect_robust(
                RABBITMQ_URL,
                timeout=30  # Add timeout
            )
            print("Successfully connected to RabbitMQ.")
            return connection
        except Exception as e:
            print(f"Attempt {i+1}/{retries}: Failed to connect to RabbitMQ at {RABBITMQ_HOST}: {str(e)}")
            if i < retries - 1:
                print(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                print("Max retries reached. Could not connect to RabbitMQ.")
                raise