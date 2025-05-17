import pika
import json
import os
from supabase import create_client, Client
from supabase_utils import check_authorization
import time # Import time for delays


RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RETRY_ATTEMPTS = 10 # Number of retry attempts
RETRY_DELAY = 5   # Delay in seconds between retries

def get_connection():
    """Helper function to establish RabbitMQ connection with retries."""
    for attempt in range(RETRY_ATTEMPTS):
        try:
            print(f"Attempt {attempt + 1}/{RETRY_ATTEMPTS}: Connecting to RabbitMQ at {RABBITMQ_HOST}")
            connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
            print("Successfully connected to RabbitMQ.")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Attempt {attempt + 1}/{RETRY_ATTEMPTS}: Failed to connect to RabbitMQ at {RABBITMQ_HOST}: {str(e)}")
            if attempt < RETRY_ATTEMPTS - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("Max retry attempts reached. Could not connect to RabbitMQ.")
                # You might want to exit or raise a critical error here
                raise # Re-raise the exception after printing

    return None 

def consume_vehicle_detected():
    try:
        connection = get_connection()
        channel = connection.channel()

        channel.queue_declare(queue="vehicle_detected", durable=True)

        def callback(ch, method, properties, body):
            message = json.loads(body)
            plate_number = message["plate_number"]
            print(f" [x] Received {plate_number}")

            # Check if vehicle is authorized
            is_authorized = check_authorization(plate_number)

            result = {
                "plate_number": plate_number,
                "is_authorized": is_authorized,
                "timestamp": message["timestamp"]
            }

            if is_authorized:
                # Publish result to logger
                print(f" [x] Vehicle {plate_number} is authorized.")
                publish_authorization_result(result)
            else:
                # Send unauthorized vehicle to manual approval queue
                print(f" [x] Vehicle {plate_number} is unauthorized. Sending to manual approval.")
                publish_manual_approval_request(result)

            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue="vehicle_detected", on_message_callback=callback)
        print(" [*] Authorization service is listening for vehicle detections...")
        channel.start_consuming()
    except Exception as e:
        print(f"Error in consume_vehicle_detected: {str(e)}")
        raise

def publish_authorization_result(data: dict):
    try:
        connection = get_connection()
        channel = connection.channel()

        channel.queue_declare(queue="vehicle.authorization.result", durable=True)

        channel.basic_publish(
            exchange="",
            routing_key="vehicle.authorization.result",
            body=json.dumps(data),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f" [x] Sent authorization result: {data}")
    except Exception as e:
        print(f"Error publishing authorization result: {str(e)}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()

def publish_manual_approval_request(data: dict):
    try:
        connection = get_connection()
        channel = connection.channel()

        channel.queue_declare(queue="manual_approval_requests", durable=True)

        channel.basic_publish(
            exchange="",
            routing_key="manual_approval_requests",
            body=json.dumps(data),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f" [x] Sent unauthorized vehicle to manual approval queue: {data}")
    except Exception as e:
        print(f"Error publishing manual approval request: {str(e)}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()