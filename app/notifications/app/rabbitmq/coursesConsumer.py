import aio_pika
import json
import asyncio
from app.config import RABBITMQ_URL, COURSES_NOTIFICATIONS_QUEUE
from app.controllers.notification_controller import handle_message
from .connection import get_connection

async def consume_courses_messages():
    while True:  # Add infinite retry loop
        try:
            connection = await get_connection()
            channel = await connection.channel()
            queue = await channel.declare_queue(COURSES_NOTIFICATIONS_QUEUE, durable=True)
            print("✅ Courses Consumer started...")

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        payload = json.loads(message.body.decode())
                        response = await handle_message(payload)
                        
                        reply_to = message.reply_to
                        correlation_id = message.correlation_id

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
                        print("✅ Notification processed and response sent.")
        except Exception as e:
            print(f"Error in courses consumer: {str(e)}")
            print("Retrying in 5 seconds...")
            await asyncio.sleep(5)
            continue