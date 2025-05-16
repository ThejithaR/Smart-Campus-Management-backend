# rabbitmq.py
import pika
import json
from manual_approvals import add_vehicle

def consume_manual_approvals():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="manual_approval_requests", durable=True)

    def callback(ch, method, properties, body):
        message = json.loads(body)
        print(f"[x] Received manual approval request: {message}")
        add_vehicle(message)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue="manual_approval_requests", on_message_callback=callback)
    print(" [*] Waiting for manual approval requests. To exit press CTRL+C")
    channel.start_consuming()

def send_manual_approval(vehicle):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
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
    connection.close()