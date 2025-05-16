import pika
import json
from supabase import create_client, Client
from supabase_utils import check_authorization

def consume_vehicle_detected():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
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
            publish_authorization_result(result)
        else:
            # Send unauthorized vehicle to manual approval queue
            publish_manual_approval_request(result)

        ch.basic_ack(delivery_tag=method.delivery_tag)


    channel.basic_consume(queue="vehicle_detected", on_message_callback=callback)
    print(" [*] Authorization service is listening for vehicle detections...")
    channel.start_consuming()

def publish_authorization_result(data: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="vehicle.authorization.result", durable=True)

    channel.basic_publish(
        exchange="",
        routing_key="vehicle.authorization.result",
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print(f" [x] Sent authorization result: {data}")
    connection.close()

def publish_manual_approval_request(data: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="manual_approval_requests", durable=True)

    channel.basic_publish(
        exchange="",
        routing_key="manual_approval_requests",
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print(f" [x] Sent unauthorized vehicle to manual approval queue: {data}")
    connection.close()
