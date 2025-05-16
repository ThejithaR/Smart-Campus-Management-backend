import pika
import json

def publish_vehicle_detected(data: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="vehicle_detected", durable=True)

    channel.basic_publish(
        exchange="",
        routing_key="vehicle_detected",
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
    )
    print(f" [x] Sent to queue: {data}")
    connection.close()
