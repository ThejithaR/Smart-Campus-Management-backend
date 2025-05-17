import pika
import json
import os # Import the os module
from supabase_utils import log_vehicle, log_surveillance_alert
import threading # Keep existing imports

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
        # For now, we'll print and raise for clarity.
        raise # Re-raise the exception after printing for easier debugging

def consume_vehicle_authorized():
    connection = None # Initialize connection to None
    try:
        connection = get_connection()
        if not connection:
            # get_connection already prints an error, just return
            print("Could not start vehicle authorized consumer due to connection failure.")
            return

        channel = connection.channel()

        channel.queue_declare(queue="vehicle.authorization.result", durable=True)

        def callback(ch, method, properties, body):
            data = json.loads(body)
            print(f"[x] Received vehicle authorization data: {data}")
            try:
                log_vehicle(data["plate_number"], "entered", True)  # TODO: Dynamic
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"Error processing vehicle authorization message {data}: {str(e)}")
                # Optionally Nack the message if processing failed and you want it redelivered
                # ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                pass # Or handle the error appropriately


        channel.basic_consume(queue="vehicle.authorization.result", on_message_callback=callback)
        print("[*] Waiting for vehicle authorization results...")
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
        print(f"An unexpected error occurred in consume_vehicle_authorized: {str(e)}")
        # Consider if you need to stop consuming or just log
    finally:
        # Ensure connection is closed if it was successfully opened
        if connection and not connection.is_closed:
            try:
                connection.close()
                print("RabbitMQ connection closed for vehicle authorized consumer.")
            except Exception as e:
                print(f"Error closing connection for vehicle authorized consumer: {str(e)}")


def consume_surveillance_alerts():
    connection = None # Initialize connection to None
    try:
        connection = get_connection()
        if not connection:
            # get_connection already prints an error, just return
            print("Could not start surveillance alerts consumer due to connection failure.")
            return

        channel = connection.channel()

        channel.queue_declare(queue="surveillance.alerts", durable=True)

        def callback(ch, method, properties, body):
            data = json.loads(body)
            print(f"[x] Received surveillance alert: {data}")
            try:
                log_surveillance_alert(data)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"Error processing surveillance alert message {data}: {str(e)}")
                # Optionally Nack the message
                # ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                pass # Or handle the error appropriately

        channel.basic_consume(queue="surveillance.alerts", on_message_callback=callback)
        print("[*] Waiting for surveillance alerts...")
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
        print(f"An unexpected error occurred in consume_surveillance_alerts: {str(e)}")
        # Consider if you need to stop consuming or just log
    finally:
        # Ensure connection is closed if it was successfully opened
        if connection and not connection.is_closed:
            try:
                connection.close()
                print("RabbitMQ connection closed for surveillance alerts consumer.")
            except Exception as e:
                print(f"Error closing connection for surveillance alerts consumer: {str(e)}")

# Note: The original file structure shows these functions are likely called
# from main.py, possibly within threads. The connection handling should
# ideally be managed carefully with threading, but this update provides
# the basic fix for the hostname and some robust error handling per function call.