import pika
import json
from supabase_utils import log_vehicle, log_surveillance_alert
import threading

def consume_vehicle_authorized():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="vehicle.authorization.result", durable=True)

    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(f"[x] Received vehicle authorization data: {data}")
        log_vehicle(data["plate_number"], "entered", True)  # TODO: Dynamic
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue="vehicle.authorization.result", on_message_callback=callback)
    print("[*] Waiting for vehicle authorization results...")
    channel.start_consuming()

def consume_surveillance_alerts():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="surveillance.alerts", durable=True)

    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(f"[x] Received surveillance alert: {data}")
        log_surveillance_alert(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue="surveillance.alerts", on_message_callback=callback)
    print("[*] Waiting for surveillance alerts...")
    channel.start_consuming()
