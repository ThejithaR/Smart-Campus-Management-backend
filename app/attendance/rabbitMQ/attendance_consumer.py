import aio_pika
import asyncio
import json
from config import ATTENDANCE_QUEUE
from controllers.attendance_controller import handle_attendance_message
from .connection import get_connection

async def attendance_consume():
    connection = None
    try:
        connection = await get_connection()
        channel = await connection.channel()
        queue = await channel.declare_queue(ATTENDANCE_QUEUE, durable=True)
        print("✅ Attendance consumer started...")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    payload = json.loads(message.body.decode())

                    action = payload.get("action")
                    data = payload.get("payload")

                    print(f"📨 Received action: {action}, payload: {data}")

                    try:
                        result = await handle_attendance_message(action, data)
                    except Exception as e:
                        result = {"error": str(e)}

                    # Reply back if needed
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

                    print("✅ Response sent.")

    except Exception as e:
        print(f"Error in attendance consumer: {str(e)}")
    finally:
        if connection and not connection.is_closed:
            await connection.close()
            print("RabbitMQ connection closed.")