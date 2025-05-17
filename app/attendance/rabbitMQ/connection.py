import aio_pika
import os

# Define the RabbitMQ host using an environment variable, defaulting to 'rabbitmq'
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_URL = f"amqp://guest:guest@{RABBITMQ_HOST}/"

async def get_connection():
    """Helper function to establish RabbitMQ connection with basic error handling."""
    try:
        print(f"Attempting to connect to RabbitMQ at {RABBITMQ_HOST}")
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        print("Successfully connected to RabbitMQ.")
        return connection
    except Exception as e:
        print(f"Failed to connect to RabbitMQ at {RABBITMQ_HOST}: {str(e)}")
        raise