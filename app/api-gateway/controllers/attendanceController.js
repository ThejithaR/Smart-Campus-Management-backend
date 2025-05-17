import {publishMessageWithReply} from "../services/rabbitmqService.js";

const QUEUE_NAME = "attendance_queue"; // (define queue name here)
const WS_QUEUE_NAME = "realtime_queue"; // (define queue name here)

export const manualAttendance = async (req, res) => {
  try {
    const { reg_number, status, location, course_code } = req.body;

    console.log("Manual Attendance Request:", { reg_number, status, location, course_code });

    const response = await publishMessageWithReply(QUEUE_NAME,{
      action: "manualAttendance",
      payload: { reg_number, status, location, course_code }
    });

    console.log("Manual Attendance Response:", response);

    res.status(200).json({ success: true, message: "Manual Attendance request sent." , response: response });
  } catch (error) {
    console.error("Manual Attendance Error:", error);
    res.status(500).json({ success: false, message: "Internal server error" });
  }
};

async function processFrame({ image_base64, threshold, location, course_code }) {
    // Validate input
    if (!image_base64 || !course_code) {
      throw new Error('Missing image or course code');
    }
  
    //console.log("Processing Frame:", { image_base64, threshold, location, course_code });

    const message = {
        action: "faceRecognition",
        payload: {
          image_base64,
          threshold,
          location,
          course_code,
          timestamp: Date.now()
        }
    };
  
    // Publish to RabbitMQ
    const response = await publishMessageWithReply(WS_QUEUE_NAME, message);

    console.log("Processing Frame Response:", response);
  
    return response.result;
  }

export function handleFaceRecognitionSocket(ws) {
    ws.on('message', async (message) => {
      try {
        const data = JSON.parse(message);
        const result = await processFrame(data); // send to service
        ws.send(JSON.stringify({ status: 'ok', result }));
      } catch (err) {
        console.error('WS Message Error:', err);
        ws.send(JSON.stringify({ status: 'error', message: err.message }));
      }
    });
  
    ws.on('close', () => {
      console.log('WebSocket connection closed');
    });
  
    ws.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  }


export const registerFace = async (req, res) => {
    try {
        const { reg_number, image_base64 } = req.body;
    
        console.log("Register Face Request:", { reg_number, image_base64 });
    
        const response = await publishMessageWithReply(QUEUE_NAME,{
            action: "registerFace",
            payload: { 
                reg_number, 
                image_base64 
            }
        });
    
        console.log("Register Face Response:", response);
    
        res.status(200).json({ success: true, message: "Register Face request sent." , response: response });
    } catch (error) {
        console.error("Register Face Error:", error);
        res.status(500).json({ success: false, message: "Internal server error" });
    }
}