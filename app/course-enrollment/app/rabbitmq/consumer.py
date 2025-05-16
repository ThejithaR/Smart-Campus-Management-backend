import aio_pika
import asyncio
import json
from app.config import RABBITMQ_URL, COURSES_QUEUE
from app.controllers.course_controller import handle_message

async def consume():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue(COURSES_QUEUE, durable=True)
    print("✅ Consumer started, waiting for messages...")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                payload = json.loads(message.body.decode())

                # Process message
                response = await handle_message(payload)

                # Correctly access reply-to and correlation-id
                reply_to = message.reply_to
                correlation_id = message.correlation_id

                print(f"response: {response}")
                print(f"reply queue: {reply_to}")
                print(f"correlation id: {correlation_id}")

                # Reply only if required
                if reply_to and correlation_id:
                    await channel.default_exchange.publish(
                        aio_pika.Message(
                            body=json.dumps({
                                "status": "success",
                                "result": response
                            }).encode(),
                            correlation_id=correlation_id
                        ),
                        routing_key=reply_to
                    )

                print("✅ Response sent back, message acked.")
