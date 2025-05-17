import aio_pika
import asyncio
import json
from config import RABBITMQ_URL, REALTIME_QUEUE
from controllers.realtime_controller import handle_realtime_message

async def consume_realtime():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue(REALTIME_QUEUE, durable=True)
    print("✅ Realtime WebSocket consumer started...")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                payload = json.loads(message.body.decode())

                action = payload.get("action")
                data = payload.get("payload")

                #print(f"📨 [Realtime] Received action: {action}, payload: {data}")

                try:
                    result = await handle_realtime_message(action, data)
                except Exception as e:
                    result = {"error": str(e)}

                reply_to = message.reply_to
                correlation_id = message.correlation_id

                if reply_to and correlation_id:
                    await channel.default_exchange.publish(
                        aio_pika.Message(
                            body=json.dumps({
                                "status": "success" if "error" not in result else "error",
                                "result": result
                            }).encode(),
                            correlation_id=correlation_id
                        ),
                        routing_key=reply_to
                    )

                print("✅ [Realtime] Response sent.")
