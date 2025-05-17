import asyncio
import json
import uuid
import aio_pika
from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractChannel, AbstractConnection
from app.config import RABBITMQ_URL
import os

# Define retry parameters
RETRY_ATTEMPTS = 10
RETRY_DELAY = 5

connection: AbstractConnection = None
channel: AbstractChannel = None

async def initialize_rabbitmq():
    global connection, channel
    
    for attempt in range(RETRY_ATTEMPTS):
        try:
            print(f"Attempt {attempt + 1}/{RETRY_ATTEMPTS}: Connecting to RabbitMQ...")
            
            # Configure connection parameters
            connection = await connect_robust(
                RABBITMQ_URL,
                timeout=5,
                reconnect_interval=5,
                connection_attempts=3
            )
            
            channel = await connection.channel()
            
            # Set QoS prefetch count
            await channel.set_qos(prefetch_count=1)
            
            print("Successfully connected to RabbitMQ.")
            return
            
        except Exception as e:
            print(f"Attempt {attempt + 1}/{RETRY_ATTEMPTS}: Failed to connect to RabbitMQ: {str(e)}")
            if attempt < RETRY_ATTEMPTS - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                await asyncio.sleep(RETRY_DELAY)
            else:
                print("Max retry attempts reached. Could not establish initial connection to RabbitMQ.")
                raise

# Call once on app startup
asyncio.create_task(initialize_rabbitmq())

async def publish_message_with_reply(queue_name: str, payload: dict, timeout: int = 5):
    if not channel:
        raise RuntimeError("RabbitMQ channel not initialized")

    correlation_id = str(uuid.uuid4())

    # Create a temporary exclusive reply queue
    reply_queue = await channel.declare_queue(exclusive=True)

    future = asyncio.get_event_loop().create_future()

    async def on_message(message: aio_pika.IncomingMessage):
        if message.correlation_id == correlation_id:
            future.set_result(json.loads(message.body.decode()))
            await message.ack()

    await reply_queue.consume(on_message, no_ack=False)

    message = Message(
        body=json.dumps(payload).encode(),
        correlation_id=correlation_id,
        reply_to=reply_queue.name,
        content_type='application/json'
    )

    await channel.default_exchange.publish(
        message, routing_key=queue_name
    )

    try:
        return await asyncio.wait_for(future, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError("Request timed out")