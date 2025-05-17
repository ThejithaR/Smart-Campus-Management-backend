# rabbitmq.py
import pika
import json
import os  # Import the os module
from manual_approvals import add_vehicle
# You might have other imports here

# Define the RabbitMQ host using an environment variable, defaulting to 'rabbitmq'
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')

def get_connection():
    """Helper function to establish RabbitMQ connection with basic error handling."""
    try:
        # Use the defined RABBITMQ_HOST instead of "localhost"
        print(f"Attempting to connect to RabbitMQ at {RABBITMQ_HOST}")
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        print("Successfully connected to RabbitMQ.")
        return connection
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Failed to connect to RabbitMQ at {RABBITMQ_HOST}: {str(e)}")
        # Depending on how critical the connection is, you might want to
        # exit, retry, or just return None and handle it in calling functions.
        # For now, we'll print and return None or raise. Let's raise for clarity.
        raise # Re-raise the exception after printing for easier debugging

def consume_manual_approvals():
    connection = None # Initialize connection to None
    try:
        connection = get_connection()
        if not connection:
            # get_connection already prints an error, just return
            return

        channel = connection.channel()
        channel.queue_declare(queue="manual_approval_requests", durable=True)

        def callback(ch, method, properties, body):
            message = json.loads(body)
            print(f"[x] Received manual approval request: {message}")
            try:
                add_vehicle(message) # Make sure add_vehicle handles potential errors
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"Error processing message {message}: {str(e)}")
                # Optionally Nack the message if processing failed and you want it redelivered
                # ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                pass # Or handle the error appropriately


        channel.basic_consume(queue="manual_approval_requests", on_message_callback=callback)
        print(" [*] Waiting for manual approval requests. To exit press CTRL+C")
        channel.start_consuming()
    except pika.exceptions.ConnectionClosedByBroker:
        print("RabbitMQ connection closed by broker. Reconnecting...")
        # Implement reconnection logic here if needed
    except pika.exceptions.AMQPChannelError as e:
         print(f"AMQP Channel Error: {e}")
         # Handle channel errors (e.g., queue gone)
    except pika.exceptions.AMQPConnectionError as e:
         print(f"AMQP Connection Error: {e}")
         # Handle connection errors (e.g., RabbitMQ down)
    except Exception as e:
        print(f"An unexpected error occurred in consume_manual_approvals: {str(e)}")
        # Consider if you need to stop consuming or just log
    finally:
        # Ensure connection is closed if it was successfully opened
        if connection and not connection.is_closed:
            try:
                connection.close()
                print("RabbitMQ connection closed.")
            except Exception as e:
                print(f"Error closing connection: {str(e)}")


def send_manual_approval(vehicle):
    connection = None # Initialize connection to None
    try:
        connection = get_connection()
        if not connection:
             # get_connection already prints an error, just return
             print("Could not send manual approval due to connection failure.")
             return

        channel = connection.channel()

        channel.queue_declare(queue="vehicle.authorization.result", durable=True)

        # Manually approve the vehicle
        message = {
            "plate_number": vehicle["plate_number"],
            "status": "manually approved",
            "security_clear": True,
            "timestamp": vehicle["timestamp"]
        }

        channel.basic_publish(
            exchange="",
            routing_key="vehicle.authorization.result",
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f" [x] Sent manual approval result: {message}")
    except pika.exceptions.AMQPConnectionError as e:
         print(f"AMQP Connection Error sending manual approval: {e}")
    except Exception as e:
        print(f"Error sending manual approval message: {str(e)}")
    finally:
        # Ensure connection is closed if it was successfully opened
        if connection and not connection.is_closed:
            try:
                connection.close()
                print("RabbitMQ connection closed after sending manual approval.")
            except Exception as e:
                 print(f"Error closing connection after sending manual approval: {str(e)}")