// import amqp from "amqplib";
import { connectRabbitMQ } from "../config/rabbitMQ.js";
import { v4 as uuidv4 } from 'uuid';

let channel = null;

const initializeRabbitMQ = async () => {
  channel = await connectRabbitMQ();
};

initializeRabbitMQ();

export const publishMessageWithReply = async (queue, message) => {
  if (!channel) {
    console.error("RabbitMQ channel not initialized");
    return;
  }

  const correlationId = uuidv4();

  const replyQueue = await channel.assertQueue('', { exclusive: true });

  return new Promise((resolve, reject) => {

    const timeout = setTimeout(() => {
      reject(new Error("Request timed out"));
    }, 5000);

    channel.consume(
      replyQueue.queue,
      (msg) => {
        if (msg.properties.correlationId === correlationId) {
          clearTimeout(timeout); // ✅ clear timeout if response is received
          const response = JSON.parse(msg.content.toString());
          resolve(response);
        }
      },
      { noAck: true }
    );

    channel.sendToQueue(queue, Buffer.from(JSON.stringify(message)), {
      correlationId: correlationId,
      replyTo: replyQueue.queue,
    });
  });
};