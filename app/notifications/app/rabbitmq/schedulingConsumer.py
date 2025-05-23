# notifications/app/rabbitmq/consumer.py
import aio_pika
import json
from app.config import RABBITMQ_URL, SCHEDULING_NOTIFICATIONS_QUEUE
from app.controllers.notification_controller import handle_message
from .connection import get_connection

async def consume_scheduling_messages():
    connection = await get_connection()
    channel = await connection.channel()
    queue = await channel.declare_queue(SCHEDULING_NOTIFICATIONS_QUEUE, durable=True)
    print("✅ Scheduling Consumer started...")

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
