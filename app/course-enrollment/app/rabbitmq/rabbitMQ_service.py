import asyncio
import json
import uuid
import aio_pika
from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractChannel, AbstractConnection
from app.config import RABBITMQ_URL

connection: AbstractConnection = None
channel: AbstractChannel = None

async def initialize_rabbitmq():
    global connection, channel
    connection = await connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

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
