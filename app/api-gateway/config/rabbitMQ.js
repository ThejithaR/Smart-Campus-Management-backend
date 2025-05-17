import amqp from "amqplib";

let channel = null;

export const connectRabbitMQ = async () => {
  if (channel) {
    return channel; // already connected
  }

  try {
    const connection = await amqp.connect("amqp://admin:admin@localhost:5672/");
    channel = await connection.createChannel();
    console.log("✅ Connected to RabbitMQ - Management UI: http://localhost:15672/");
    return channel;
  } catch (error) {
    console.error("❌ Failed to connect to RabbitMQ:", error.message);
    throw error; // rethrow so caller knows there was a problem
  }
};
