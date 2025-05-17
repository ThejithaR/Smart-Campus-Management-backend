import aio_pika
import asyncio
import json
# Remove the import of RABBITMQ_URL from config
# from config import RABBITMQ_URL, SCHEDULE_QUEUE
from config import SCHEDULE_QUEUE # Keep the queue name import
from controllers.scheduling_controller import handle_schedule_message

# Import the shared connection function
from .connection import get_connection

async def schedule_consume():
    # Initialize connection to None
    connection = None
    try:
        # Use the shared get_connection function
        connection = await get_connection()
        channel = await connection.channel()
        # Declare the queue
        queue = await channel.declare_queue(SCHEDULE_QUEUE, durable=True)
        # Correct the print statement to be specific to this consumer
        print(f"✅ Schedule consumer started on queue: {SCHEDULE_QUEUE}")

        # Use an asynchronous iterator for consuming messages
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                # Process the message automatically acknowledging it upon success
                async with message.process():
                    payload = json.loads(message.body.decode())

                    action = payload.get("action")
                    data = payload.get("payload")

                    print(f"📨 Received action: {action}, payload: {data} on queue {SCHEDULE_QUEUE}")

                    try:
                        # Call the message handling function
                        # Ensure handle_schedule_message is an async function
                        result = await handle_schedule_message(action, data)
                        print(f"✅ Message processed for queue {SCHEDULE_QUEUE}.")

                    except Exception as e:
                        # Handle errors during message processing
                        result = {"error": str(e)}
                        print(f"Error processing message on queue {SCHEDULE_QUEUE}: {str(e)}")
                        # Message is auto-acked by `message.process()` context manager.
                        # If you need to nack explicitly on error, remove `async with message.process():`
                        # and manually call message.ack() or message.nack().

                    # Reply back if needed
                    reply_to = message.reply_to
                    correlation_id = message.correlation_id

                    if reply_to and correlation_id:
                        # Publish the reply
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
                        print(f"✅ Reply sent for message on queue {SCHEDULE_QUEUE}.")

    except Exception as e:
        # Handle connection or channel errors
        print(f"Error in schedule consumer: {str(e)}")
    finally:
        # Ensure connection is closed when the consumer stops or on error
        if connection and not connection.is_closed:
            await connection.close()
            print(f"RabbitMQ connection closed for {SCHEDULE_QUEUE} consumer.")