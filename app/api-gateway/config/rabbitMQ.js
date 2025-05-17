import amqp from "amqplib";

let channel = null;
let connection = null;

const RETRY_ATTEMPTS = 10;
const RETRY_DELAY = 5000; // 5 seconds in milliseconds
const RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/";

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const connectRabbitMQ = async () => {
  if (channel) {
    return channel; // already connected
  }

  for (let attempt = 1; attempt <= RETRY_ATTEMPTS; attempt++) {
    try {
      console.log(`Attempt ${attempt}/${RETRY_ATTEMPTS}: Connecting to RabbitMQ...`);
      
      connection = await amqp.connect(RABBITMQ_URL, {
        heartbeat: 60, // 60 seconds
        timeout: 5000, // 5 seconds
        connectionTimeout: 5000, // 5 seconds
      });

      // Handle connection errors
      connection.on('error', (err) => {
        console.error('RabbitMQ connection error:', err);
        channel = null;
        connection = null;
      });

      connection.on('close', () => {
        console.log('RabbitMQ connection closed');
        channel = null;
        connection = null;
      });

      channel = await connection.createChannel();
      
      // Set QoS prefetch count
      await channel.prefetch(1);
      
      console.log("✅ Connected to RabbitMQ");
      return channel;
    } catch (error) {
      console.error(`Attempt ${attempt}/${RETRY_ATTEMPTS}: Failed to connect to RabbitMQ:`, error.message);
      
      if (attempt < RETRY_ATTEMPTS) {
        console.log(`Retrying in ${RETRY_DELAY/1000} seconds...`);
        await sleep(RETRY_DELAY);
      } else {
        console.error("Max retry attempts reached. Could not establish connection to RabbitMQ.");
        throw error;
      }
    }
  }
};

// Graceful shutdown
export const closeConnection = async () => {
  try {
    if (channel) {
      await channel.close();
      channel = null;
    }
    if (connection) {
      await connection.close();
      connection = null;
    }
    console.log("RabbitMQ connection closed gracefully");
  } catch (error) {
    console.error("Error closing RabbitMQ connection:", error);
  }
};